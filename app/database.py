import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "students.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            dob         TEXT NOT NULL,
            class_name  TEXT NOT NULL,
            section     TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()