from fastapi import FastAPI, HTTPException, Request, Response
from app.models import Student, StudentResponse
from app.database import get_connection, init_db
from typing import List
import sqlite3

# 🔥 Prometheus imports
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Student Registry", version="1.0.0")

# 🔥 Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["endpoint"]
)

# 🔹 Startup
@app.on_event("startup")
def startup():
    init_db()

# 🔹 Middleware to track all requests
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    endpoint = request.url.path

    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        response = await call_next(request)

    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint).inc()
    return response

# 🔹 Health Check
@app.get("/health")
def health():
    return {"status": "healthy", "service": "student-registry"}

# 🔹 Prometheus Metrics Endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# 🔹 Test endpoint
@app.get("/metrics-check")
def metrics_check():
    return {"status": "ok"}

# 🔹 Create Student
@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: Student):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO students (roll_number, name, dob, class_name, section) VALUES (?,?,?,?,?)",
            (student.roll_number, student.name, student.dob, student.class_name, student.section)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM students WHERE id=?",
            (cursor.lastrowid,)
        ).fetchone()
        return dict(row)

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Roll number already exists")

    finally:
        conn.close()

# 🔹 Get All Students
@app.get("/students", response_model=List[StudentResponse])
def list_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 🔹 Get One Student
@app.get("/students/{roll_number}", response_model=StudentResponse)
def get_student(roll_number: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE roll_number=?",
        (roll_number,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    return dict(row)

# 🔹 Delete Student
@app.delete("/students/{roll_number}")
def delete_student(roll_number: str):
    conn = get_connection()
    conn.execute(
        "DELETE FROM students WHERE roll_number=?",
        (roll_number,)
    )
    conn.commit()
    conn.close()

    return {"message": "Student deleted"}