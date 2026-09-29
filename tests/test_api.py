import os
os.environ["DATABASE_URL"] = "sqlite:///./test_students.db"

from fastapi.testclient import TestClient
from main import app
from database import Base, engine

client = TestClient(app)

def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health():
    assert client.get("/health").status_code == 200

def test_student_crud():
    payload = {
        "student_number":"TEST001","first_name":"Test","last_name":"Student",
        "email":"test.student@example.edu","major":"Computer Science","gpa":3.75,"status":"Active"
    }
    created = client.post("/api/students", json=payload)
    assert created.status_code == 201
    sid = created.json()["id"]

    fetched = client.get(f"/api/students/{sid}")
    assert fetched.status_code == 200
    assert fetched.json()["student_number"] == "TEST001"

    updated = client.put(f"/api/students/{sid}", json={"gpa":3.9})
    assert updated.status_code == 200
    assert updated.json()["gpa"] == 3.9

    deleted = client.delete(f"/api/students/{sid}")
    assert deleted.status_code == 200
    assert client.get(f"/api/students/{sid}").status_code == 404

def test_validation():
    bad = {
        "student_number":"X","first_name":"","last_name":"Student",
        "email":"not-an-email","major":"C","gpa":5.0,"status":"Unknown"
    }
    assert client.post("/api/students", json=bad).status_code == 422
