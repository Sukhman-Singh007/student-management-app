from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(60), nullable=False, index=True)
    last_name = Column(String(60), nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    major = Column(String(100), nullable=False, index=True)
    gpa = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), nullable=False, default="Active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
