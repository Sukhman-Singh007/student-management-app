from database import Base, engine, SessionLocal
from models import Student

SAMPLE = [
    ("UNT10001","Ava","Patel","ava.patel@example.edu","Computer Science",3.82,"Active"),
    ("UNT10002","Noah","Williams","noah.williams@example.edu","Data Science",3.54,"Active"),
    ("UNT10003","Mia","Garcia","mia.garcia@example.edu","Information Technology",3.91,"Active"),
    ("UNT10004","Ethan","Brown","ethan.brown@example.edu","Computer Engineering",3.26,"Inactive"),
    ("UNT10005","Sophia","Lee","sophia.lee@example.edu","Computer Science",3.68,"Graduated"),
]

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    for number, first, last, email, major, gpa, status in SAMPLE:
        exists = db.query(Student).filter(Student.student_number == number).first()
        if not exists:
            db.add(Student(student_number=number, first_name=first, last_name=last,
                           email=email, major=major, gpa=gpa, status=status))
    db.commit()
    print("Sample student records added.")
finally:
    db.close()
