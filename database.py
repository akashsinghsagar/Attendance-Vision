"""
database.py
Handles SQLite database operations for attendance and user registration.
"""
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'attendance.db')

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()

    def delete_user(self, user_id):
        c = self.conn.cursor()
        # Delete from users table
        c.execute('DELETE FROM users WHERE id=?', (user_id,))
        # Delete all attendance records for this user
        c.execute('DELETE FROM attendance WHERE user_id=?', (user_id,))
        self.conn.commit()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            registered_at TEXT NOT NULL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            confidence REAL NOT NULL,
            source TEXT NOT NULL,
            UNIQUE(user_id, date)
        )''')
        self.conn.commit()

    def register_user(self, user_id, name, department):
        c = self.conn.cursor()
        c.execute('INSERT INTO users (id, name, department, registered_at) VALUES (?, ?, ?, ?)',
                  (user_id, name, department, datetime.now().isoformat()))
        self.conn.commit()

    def get_user(self, user_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM users WHERE id=?', (user_id,))
        return c.fetchone()

    def get_all_users(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM users')
        return c.fetchall()

    def mark_attendance(self, user_id, name, department, confidence, source):
        c = self.conn.cursor()
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M:%S')
        try:
            c.execute('''INSERT INTO attendance (user_id, name, department, date, time, confidence, source)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, name, department, date, time, confidence, source))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already marked today

    def get_attendance_today(self):
        c = self.conn.cursor()
        date = datetime.now().strftime('%Y-%m-%d')
        c.execute('SELECT * FROM attendance WHERE date=?', (date,))
        return c.fetchall()

    def get_attendance_by_date(self, date):
        c = self.conn.cursor()
        c.execute('SELECT * FROM attendance WHERE date=?', (date,))
        return c.fetchall()

    def get_attendance_records(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM attendance ORDER BY date DESC, time DESC')
        return c.fetchall()

    def get_attendance_trend(self, days=7):
        c = self.conn.cursor()
        c.execute('''SELECT date, COUNT(DISTINCT user_id) as count FROM attendance
                     GROUP BY date ORDER BY date DESC LIMIT ?''', (days,))
        return c.fetchall()

    def get_department_attendance(self):
        c = self.conn.cursor()
        c.execute('''SELECT department, COUNT(DISTINCT user_id) as count FROM attendance
                     WHERE date=? GROUP BY department''', (datetime.now().strftime('%Y-%m-%d'),))
        return c.fetchall()

    def close(self):
        self.conn.close()
