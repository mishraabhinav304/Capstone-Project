from pydantic import BaseModel
from typing import Optional

class Student(BaseModel):
    roll_number: str
    name: str
    dob: str          # format: YYYY-MM-DD
    class_name: str   # e.g. "10"
    section: str      # e.g. "A"

class StudentResponse(Student):
    id: int

    class Config:
        from_attributes = True