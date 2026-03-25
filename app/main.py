from fastapi import FastAPI, HTTPException
from app.models import Student, StudentResponse
from app.database import get_connection, init_db
from typing import List

app = FastAPI(title="Student Registry", version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "student-registry"}

@app.get("/metrics-check")
def metrics_check():
    return {"status": "ok"}

@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: Student):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO students (roll_number, name, dob, class_name, section) VALUES (?,?,?,?,?)",
            (student.roll_number, student.name, student.dob, student.class_name, student.section)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM students WHERE id=?", (cursor.lastrowid,)).fetchone()
        return dict(row)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Roll number already exists")
    finally:
        conn.close()

@app.get("/students", response_model=List[StudentResponse])
def list_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/students/{roll_number}", response_model=StudentResponse)
def get_student(roll_number: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)

@app.delete("/students/{roll_number}")
def delete_student(roll_number: str):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE roll_number=?", (roll_number,))
    conn.commit()
    conn.close()
    return {"message": "Student deleted"}
