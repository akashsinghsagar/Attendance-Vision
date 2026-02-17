"""
app.py
Main Streamlit app for Face Recognition Attendance System
"""
import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import time
import os
from datetime import datetime, timedelta
from database import Database
from face_utils import FaceUtils

# --- Modern CSS for improved UI ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%);
        padding: 32px;
        border-radius: 18px;
        box-shadow: 0 4px 32px rgba(0,0,0,0.08);
        max-width: 900px;
        margin: 32px auto;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #60a5fa 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 0.75em 2em;
        font-size: 1.1em;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(99,102,241,0.15);
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #60a5fa 0%, #6366f1 100%);
        color: #fff;
    }
    .stTextInput>div>input {
        border-radius: 8px;
        border: 1.5px solid #cbd5e1;
        padding: 0.5em 1em;
        font-size: 1em;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    </style>
""", unsafe_allow_html=True)

# --- Caching for performance ---
@st.cache_resource

def get_face_utils():
    return FaceUtils()

@st.cache_resource

def get_db():
    return Database()

face_utils = get_face_utils()
db = get_db()

# --- Session state for attendance memory ---
if 'marked_today' not in st.session_state:
    st.session_state['marked_today'] = set()

# --- Sidebar Menu ---
menu = [
    'Dashboard',
    'Register New User',
    'Mark Attendance (Live Camera)',
    'Upload Image',
    'Upload Video',
    'Attendance Records',
    'Analytics'
]
choice = st.sidebar.selectbox('Menu', menu)

st.sidebar.markdown('---')
st.sidebar.markdown('**Dark Mode:**')
dark_mode = st.sidebar.checkbox('Enable Dark Mode', value=True)
if dark_mode:
    st.markdown('<style>body { background-color: #222; color: #eee; }</style>', unsafe_allow_html=True)

# --- Dashboard ---
def dashboard():
    st.title('📊 Dashboard')
    users = db.get_all_users()
    attendance_today = db.get_attendance_today()
    total_users = len(users)
    present_today = len(attendance_today)
    attendance_pct = (present_today / total_users * 100) if total_users else 0
    st.metric('Total Registered Users', total_users)
    st.metric("Today's Attendance", present_today)
    st.metric('Attendance %', f'{attendance_pct:.1f}%')
    # Department-wise bar chart
    dept_data = db.get_department_attendance()
    if dept_data:
        df_dept = pd.DataFrame(dept_data, columns=['Department', 'Count'])
        st.plotly_chart(px.bar(df_dept, x='Department', y='Count', title='Department-wise Attendance'))
    # Attendance trend (last 7 days)
    trend = db.get_attendance_trend()
    if trend:
        df_trend = pd.DataFrame(trend, columns=['Date', 'Count'])
        df_trend = df_trend.sort_values('Date')
        st.plotly_chart(px.line(df_trend, x='Date', y='Count', title='Attendance Trend (Last 7 Days)'))
    # Present vs Absent pie chart
    absent = total_users - present_today
    st.plotly_chart(px.pie(pd.DataFrame({'Status': ['Present', 'Absent'], 'Count': [present_today, absent]}),
                          names='Status', values='Count', title='Present vs Absent'))

# --- Register New User ---
def register_user():
    st.title('📝 Register New User')
    # Initialize session state for registration
    if 'samples' not in st.session_state:
        st.session_state['samples'] = []
    if 'captured' not in st.session_state:
        st.session_state['captured'] = 0
    if 'last_frame' not in st.session_state:
        st.session_state['last_frame'] = None
    if 'reg_name' not in st.session_state:
        st.session_state['reg_name'] = ''
    if 'reg_user_id' not in st.session_state:
        st.session_state['reg_user_id'] = ''
    if 'reg_department' not in st.session_state:
        st.session_state['reg_department'] = ''
    if 'registration_ready' not in st.session_state:
        st.session_state['registration_ready'] = False

    st.subheader('Enter User Details')
    st.session_state['reg_name'] = st.text_input('Name', st.session_state['reg_name'])
    st.session_state['reg_user_id'] = st.text_input('Unique ID', st.session_state['reg_user_id'])
    st.session_state['reg_department'] = st.text_input('Department', st.session_state['reg_department'])

    if st.button('Start Registration'):
        # Reset session state for new registration
        st.session_state['samples'] = []
        st.session_state['captured'] = 0
        st.session_state['last_frame'] = None
        if not st.session_state['reg_name'] or not st.session_state['reg_user_id'] or not st.session_state['reg_department']:
            st.error('All fields are required!')
        else:
            user_id = st.session_state['reg_user_id']
            if face_utils.is_duplicate_registration(user_id):
                st.warning('User already registered!')
            else:
                st.session_state['registration_ready'] = True

    if st.session_state.get('registration_ready', False):
        st.info('Capture 5 face samples. Click "Capture Sample" for each sample.')
        samples = st.session_state['samples']
        captured = st.session_state['captured']
        frame_placeholder = st.empty()
        # Show last captured frame if available
        if st.session_state['last_frame'] is not None:
            frame_placeholder.image(st.session_state['last_frame'], channels='BGR')
        if st.button(f'Capture Sample {captured+1}', disabled=(captured>=5)) and captured < 5:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                st.error('Camera error!')
            else:
                st.session_state['last_frame'] = frame
                frame_placeholder.image(frame, channels='BGR')
                boxes = face_utils.detect_faces(frame)
                if not boxes:
                    st.warning('No face detected! Try again.')
                else:
                    encodings = face_utils.encode_faces(frame, boxes)
                    if encodings:
                        samples.append(encodings[0])
                        st.session_state['samples'] = samples
                        st.session_state['captured'] = captured + 1
                        st.success(f'Sample {captured+1} captured!')
                    else:
                        st.warning('Face encoding failed! Try again.')
        st.write(f"Samples captured: {len(samples)}/5")
        if len(samples) == 5:
            avg_encoding = np.mean(samples, axis=0)
            if st.button('Save Registration'):
                user_id = st.session_state['reg_user_id']
                face_utils.add_encoding(avg_encoding, user_id, st.session_state['reg_name'], st.session_state['reg_department'])
                db.register_user(user_id, st.session_state['reg_name'], st.session_state['reg_department'])
                st.success('User registered successfully!')
                st.session_state['samples'] = []
                st.session_state['captured'] = 0
                st.session_state['last_frame'] = None
                st.session_state['registration_ready'] = False

# --- Mark Attendance (Live Camera) ---
def mark_attendance_camera():
    st.title('📷 Mark Attendance (Live Camera)')
    threshold = st.slider('Confidence Threshold (%)', 60, 100, 70)
    cap = cv2.VideoCapture(0)
    fps_display = st.empty()
    frame_display = st.empty()
    while True:
        start = time.time()
        ret, frame = cap.read()
        if not ret:
            st.error('Camera error!')
            break
        small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
        boxes = face_utils.detect_faces(small)
        encodings = face_utils.encode_faces(small, boxes)
        names = []
        for encoding in encodings:
            user, conf = face_utils.recognize(encoding, threshold=1-threshold/100)
            if user and conf >= threshold:
                if user['id'] not in st.session_state['marked_today']:
                    if db.mark_attendance(user['id'], user['name'], user['department'], conf, 'Camera'):
                        st.session_state['marked_today'].add(user['id'])
                        # Email notification stub
                        # send_email(user['name'], user['id'])
                        st.success(f"Attendance marked for {user['name']} ({conf:.1f}%)")
                    else:
                        st.info('Already marked today!')
                names.append(user['name'])
            else:
                names.append('Unknown')
                st.warning('Unknown face detected!')
        frame = face_utils.draw_boxes(small, boxes, names)
        frame_display.image(frame, channels='BGR')
        fps = 1/(time.time()-start)
        fps_display.text(f'FPS: {fps:.2f}')
        if st.button('Stop Camera', key='stop_camera_btn'):
            break
    cap.release()

# --- Upload Image ---
def upload_image():
    st.title('🖼️ Upload Image')
    threshold = st.slider('Confidence Threshold (%)', 60, 100, 70)
    uploaded = st.file_uploader('Upload an image', type=['jpg', 'png'])
    if uploaded:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        boxes = face_utils.detect_faces(frame)
        encodings = face_utils.encode_faces(frame, boxes)
        names = []
        for encoding in encodings:
            user, conf = face_utils.recognize(encoding, threshold=1-threshold/100)
            if user and conf >= threshold:
                if user['id'] not in st.session_state['marked_today']:
                    if db.mark_attendance(user['id'], user['name'], user['department'], conf, 'Image'):
                        st.session_state['marked_today'].add(user['id'])
                        st.success(f"Attendance marked for {user['name']} ({conf:.1f}%)")
                    else:
                        st.info('Already marked today!')
                names.append(user['name'])
            else:
                names.append('Unknown')
                st.warning('Unknown face detected!')
        frame = face_utils.draw_boxes(frame, boxes, names)
        st.image(frame, channels='BGR')

# --- Upload Video ---
def upload_video():
    st.title('🎥 Upload Video')
    threshold = st.slider('Confidence Threshold (%)', 60, 100, 70)
    uploaded = st.file_uploader('Upload a video', type=['mp4', 'avi'])
    if uploaded:
        tfile = os.path.join('data', f'temp_{int(time.time())}.mp4')
        with open(tfile, 'wb') as f:
            f.write(uploaded.read())
        cap = cv2.VideoCapture(tfile)
        fps_display = st.empty()
        frame_display = st.empty()
        while cap.isOpened():
            start = time.time()
            ret, frame = cap.read()
            if not ret:
                break
            small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
            boxes = face_utils.detect_faces(small)
            encodings = face_utils.encode_faces(small, boxes)
            names = []
            for encoding in encodings:
                user, conf = face_utils.recognize(encoding, threshold=1-threshold/100)
                if user and conf >= threshold:
                    if user['id'] not in st.session_state['marked_today']:
                        if db.mark_attendance(user['id'], user['name'], user['department'], conf, 'Video'):
                            st.session_state['marked_today'].add(user['id'])
                            st.success(f"Attendance marked for {user['name']} ({conf:.1f}%)")
                        else:
                            st.info('Already marked today!')
                    names.append(user['name'])
                else:
                    names.append('Unknown')
                    st.warning('Unknown face detected!')
            frame = face_utils.draw_boxes(small, boxes, names)
            frame_display.image(frame, channels='BGR')
            fps = 1/(time.time()-start)
            fps_display.text(f'FPS: {fps:.2f}')
            if st.button('Stop Video'):
                break
        cap.release()
        os.remove(tfile)

# --- Attendance Records ---
def attendance_records():
    st.title('📋 Attendance Records')
    records = db.get_attendance_records()
    df = pd.DataFrame(records, columns=['ID', 'User ID', 'Name', 'Department', 'Date', 'Time', 'Confidence', 'Source'])
    st.dataframe(df)
    st.download_button('Download CSV', df.to_csv(index=False), file_name='attendance.csv')

    st.subheader('Delete User by User ID')
    user_id_to_delete = st.text_input('Enter User ID to delete user and all their attendance records:')
    if st.button('Delete User'):
        if user_id_to_delete:
            # Remove from DB and face encodings
            user = db.get_user(user_id_to_delete)
            if user:
                db.delete_user(user_id_to_delete)
                face_utils.delete_user(user_id_to_delete)
                st.success(f'User {user_id_to_delete} deleted successfully!')
            else:
                st.warning('User ID not found.')
        else:
            st.warning('Please enter a User ID.')

# --- Analytics ---
def analytics():
    st.title('📈 Analytics')
    # Reuse dashboard charts, or add more advanced analytics here
    dashboard()

# --- Main Routing ---
if choice == 'Dashboard':
    dashboard()
elif choice == 'Register New User':
    register_user()
elif choice == 'Mark Attendance (Live Camera)':
    mark_attendance_camera()
elif choice == 'Upload Image':
    upload_image()
elif choice == 'Upload Video':
    upload_video()
elif choice == 'Attendance Records':
    attendance_records()
elif choice == 'Analytics':
    analytics()
