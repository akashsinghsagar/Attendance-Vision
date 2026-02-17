# Face Recognition Attendance System

A production-ready attendance system using face recognition, OpenCV, and Streamlit.

---

## Features

- Live camera, image, and video support
- Face registration and attendance marking
- SQLite database for attendance records
- Anti-duplicate attendance logic
- Confidence score threshold
- Visual analytics dashboard
- Export to CSV
- Real-time FPS display
- Liveness detection (basic)
- Email notification stub
- Error logging
- Dark mode friendly UI

---

## Folder Structure

```
attendance_app/
│── app.py                # Main Streamlit app
│── face_utils.py         # Face detection/recognition utilities
│── database.py           # SQLite DB logic
│── encodings.pkl         # Face encodings (auto-managed)
│── requirements.txt      # All dependencies
│── utils/                # Helper modules (logger, email, validation, liveness)
│── data/                 # DB, sample data, logs
│── README.md
```

---

## Database Schema

**users**

| Column        | Type    | Description                |
|-------------- |---------|----------------------------|
| id            | TEXT    | Hashed unique user ID      |
| name          | TEXT    | User's name                |
| department    | TEXT    | Department                 |
| registered_at | TEXT    | ISO timestamp              |

**attendance**

| Column      | Type     | Description                        |
|-------------|----------|------------------------------------|
| id          | INTEGER  | Primary key (auto increment)       |
| user_id     | TEXT     | Hashed user ID (foreign key)       |
| name        | TEXT     | User's name                        |
| department  | TEXT     | Department                         |
| date        | TEXT     | Date (YYYY-MM-DD)                  |
| time        | TEXT     | Time (HH:MM:SS)                    |
| confidence  | REAL     | Similarity score (%)                |
| source      | TEXT     | Camera/Image/Video                  |

---

## Architecture & Modules

- **app.py**: Streamlit UI, routing, and business logic
- **face_utils.py**: Face detection, encoding, recognition, liveness
- **database.py**: SQLite DB connection, schema, CRUD
- **utils/logger.py**: Error/info logging
- **utils/email_stub.py**: Email notification stub
- **utils/input_validation.py**: Input validation helpers
- **utils/liveness.py**: Liveness detection stub
- **encodings.pkl**: Stores face encodings, names, IDs, departments

---

## Usage

1. **Clone the repo and navigate to `attendance_app`**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## Deployment

- Compatible with Streamlit Cloud
- All dependencies in `requirements.txt`
- SQLite DB and encodings are file-based (no server needed)

---

## Security

- User IDs are hashed (SHA-256)
- Duplicate registration prevented
- Input validation enforced

---

## Sample Data

- `data/sample_users.csv`: Example users
- `data/sample_attendance.csv`: Example attendance records

---

## Notes

- For email notifications, configure SMTP in `.env` (optional, see `utils/email_stub.py`)
- For liveness detection, blink detection is basic and optional (see `utils/liveness.py`)

---

## License

MIT
