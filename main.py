from contextlib import asynccontextmanager
from pathlib import Path
import time

from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database import Base, engine, get_db
from models import Student
from schemas import StudentCreate, StudentUpdate, StudentOut

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Student Management Web Application",
    description="Full-stack student records application by Sukhman Singh",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/students", response_model=list[StudentOut])
def list_students(
    search: str | None = Query(default=None, max_length=100),
    major: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=30),
    db: Session = Depends(get_db),
):
    query = db.query(Student)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Student.first_name.ilike(pattern),
                Student.last_name.ilike(pattern),
                Student.email.ilike(pattern),
                Student.student_number.ilike(pattern),
            )
        )
    if major:
        query = query.filter(Student.major == major)
    if status:
        query = query.filter(Student.status == status)
    return query.order_by(Student.id.desc()).all()

@app.get("/api/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/api/students", response_model=StudentOut, status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    duplicate = db.query(Student).filter(
        or_(Student.email == payload.email, Student.student_number == payload.student_number)
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Email or student number already exists")
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
        return student
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to save student record")

@app.put("/api/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    updates = payload.model_dump(exclude_unset=True)
    if "email" in updates or "student_number" in updates:
        email = updates.get("email", student.email)
        number = updates.get("student_number", student.student_number)
        duplicate = db.query(Student).filter(
            Student.id != student_id,
            or_(Student.email == email, Student.student_number == number),
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Email or student number already exists")

    for key, value in updates.items():
        setattr(student, key, value)

    try:
        db.commit()
        db.refresh(student)
        return student
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to update student record")

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        db.delete(student)
        db.commit()
        return {"message": "Student deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to delete student record")

@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Student.id)).scalar() or 0
    active = db.query(func.count(Student.id)).filter(Student.status == "Active").scalar() or 0
    avg_gpa = db.query(func.avg(Student.gpa)).scalar()
    majors = db.query(func.count(func.distinct(Student.major))).scalar() or 0
    return {
        "total_students": total,
        "active_students": active,
        "average_gpa": round(float(avg_gpa), 2) if avg_gpa is not None else 0,
        "majors": majors,
    }

@app.get("/api/majors")
def majors(db: Session = Depends(get_db)):
    rows = db.query(Student.major).distinct().order_by(Student.major).all()
    return [row[0] for row in rows]

@app.get("/api/benchmark")
def benchmark(db: Session = Depends(get_db)):
    start = time.perf_counter()
    count = db.query(func.count(Student.id)).scalar() or 0
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"records": count, "query_time_ms": round(elapsed_ms, 3)}
