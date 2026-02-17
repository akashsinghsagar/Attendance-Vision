"""
face_utils.py
Face detection, encoding, recognition, and liveness detection utilities.
"""
import face_recognition
import numpy as np
import cv2
import pickle
import os
import hashlib
from datetime import datetime

ENCODINGS_PATH = os.path.join(os.path.dirname(__file__), 'encodings.pkl')

class FaceUtils:
    def __init__(self, encodings_path=ENCODINGS_PATH):
        self.encodings_path = encodings_path
        self.known_encodings = []
        self.known_ids = []
        self.known_names = []
        self.known_departments = []
        self.load_encodings()

    def delete_user(self, user_id):
        # Remove all encodings, names, departments for this user_id
        indices = [i for i, uid in enumerate(self.known_ids) if uid == user_id]
        for idx in sorted(indices, reverse=True):
            del self.known_encodings[idx]
            del self.known_ids[idx]
            del self.known_names[idx]
            del self.known_departments[idx]
        self.save_encodings()

    def hash_id(self, id_str):
        return hashlib.sha256(id_str.encode()).hexdigest()

    def load_encodings(self):
        if os.path.exists(self.encodings_path):
            with open(self.encodings_path, 'rb') as f:
                data = pickle.load(f)
                self.known_encodings = data['encodings']
                self.known_ids = data['ids']
                self.known_names = data['names']
                self.known_departments = data['departments']
        else:
            self.known_encodings = []
            self.known_ids = []
            self.known_names = []
            self.known_departments = []

    def save_encodings(self):
        data = {
            'encodings': self.known_encodings,
            'ids': self.known_ids,
            'names': self.known_names,
            'departments': self.known_departments
        }
        with open(self.encodings_path, 'wb') as f:
            pickle.dump(data, f)

    def add_encoding(self, encoding, user_id, name, department):
        self.known_encodings.append(encoding)
        self.known_ids.append(user_id)
        self.known_names.append(name)
        self.known_departments.append(department)
        self.save_encodings()

    def is_duplicate_registration(self, user_id):
        return user_id in self.known_ids

    def detect_faces(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        return boxes

    def encode_faces(self, frame, boxes):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb, boxes)
        return encodings

    def recognize(self, encoding, threshold=0.6):
        if not self.known_encodings:
            return None, 0.0
        dists = face_recognition.face_distance(self.known_encodings, encoding)
        min_idx = np.argmin(dists)
        min_dist = dists[min_idx]
        confidence = (1 - min_dist) * 100
        if min_dist < threshold:
            return {
                'id': self.known_ids[min_idx],
                'name': self.known_names[min_idx],
                'department': self.known_departments[min_idx]
            }, confidence
        else:
            return None, confidence

    def draw_boxes(self, frame, boxes, names=None):
        for i, box in enumerate(boxes):
            top, right, bottom, left = box
            color = (0, 255, 0) if names and names[i] != 'Unknown' else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            label = names[i] if names else ''
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame

    def basic_liveness(self, frame, boxes):
        # Optional: Simple blink detection stub (returns True for now)
        return [True for _ in boxes]
