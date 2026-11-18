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

def test_search_treats_wildcards_literally():
    payload = {
        "student_number":"TEST002","first_name":"Ann","last_name":"Lee",
        "email":"ann.lee@example.edu","major":"Computer Science","gpa":3.5,"status":"Active"
    }
    created = client.post("/api/students", json=payload)
    assert created.status_code == 201
    sid = created.json()["id"]
    try:
        # "%" and "_" are LIKE wildcards — searching for them must
        # not match every student in the table.
        assert client.get("/api/students", params={"search": "%"}).json() == []
        assert client.get("/api/students", params={"search": "_"}).json() == []
        # A plain substring still finds the student.
        found = client.get("/api/students", params={"search": "ann.lee"}).json()
        assert any(s["student_number"] == "TEST002" for s in found)
    finally:
        client.delete(f"/api/students/{sid}")

def test_list_pagination():
    created_ids = []
    for i, number in enumerate(("TEST010", "TEST011", "TEST012")):
        resp = client.post("/api/students", json={
            "student_number": number, "first_name": "Page",
            "last_name": f"Test{i}",
            "email": f"page.test{i}@example.edu",
            "major": "Computer Science", "gpa": 3.0, "status": "Active",
        })
        assert resp.status_code == 201
        created_ids.append(resp.json()["id"])
    try:
        # The three new students are the newest, so the first two
        # pages (limit 2) cover all three without overlap.
        page1 = client.get("/api/students", params={"limit": 2, "offset": 0}).json()
        page2 = client.get("/api/students", params={"limit": 2, "offset": 2}).json()
        assert len(page1) == 2
        ids1 = {s["id"] for s in page1}
        ids2 = {s["id"] for s in page2}
        assert not ids1 & ids2
        assert set(created_ids) <= ids1 | ids2
        # Out-of-range values are rejected.
        assert client.get("/api/students", params={"limit": 0}).status_code == 422
        assert client.get("/api/students", params={"limit": 101}).status_code == 422
        assert client.get("/api/students", params={"offset": -1}).status_code == 422
    finally:
        for sid in created_ids:
            client.delete(f"/api/students/{sid}")
