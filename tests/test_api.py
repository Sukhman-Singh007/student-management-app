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

def test_duplicate_email_is_case_insensitive():
    payload = {
        "student_number":"TEST020","first_name":"Case","last_name":"Test",
        "email":"Case.Test@example.edu","major":"Computer Science","gpa":3.5,"status":"Active"
    }
    created = client.post("/api/students", json=payload)
    assert created.status_code == 201
    sid = created.json()["id"]
    try:
        # Same mailbox, different casing — must be rejected as a duplicate.
        twin = dict(payload, student_number="TEST021", email="case.test@example.edu")
        assert client.post("/api/students", json=twin).status_code == 409
        # Updating another student to that email (any casing) is one too.
        other = dict(payload, student_number="TEST022", email="other@example.edu")
        other_created = client.post("/api/students", json=other)
        assert other_created.status_code == 201
        other_id = other_created.json()["id"]
        try:
            resp = client.put(f"/api/students/{other_id}",
                               json={"email": "CASE.TEST@EXAMPLE.EDU"})
            assert resp.status_code == 409
        finally:
            client.delete(f"/api/students/{other_id}")
    finally:
        client.delete(f"/api/students/{sid}")

def test_major_and_status_filters_are_case_insensitive():
    payload = {
        "student_number":"TEST030","first_name":"Filter","last_name":"Test",
        "email":"filter.test@example.edu","major":"Computer Science","gpa":3.5,"status":"Active"
    }
    created = client.post("/api/students", json=payload)
    assert created.status_code == 201
    sid = created.json()["id"]
    try:
        # Lowercase filter values must match the stored casing.
        found = client.get("/api/students", params={"major": "computer science"}).json()
        assert any(s["student_number"] == "TEST030" for s in found)
        found = client.get("/api/students", params={"status": "active"}).json()
        assert any(s["student_number"] == "TEST030" for s in found)
        # A filter that matches nothing still returns nothing.
        assert client.get("/api/students", params={"major": "Biology"}).json() == []
    finally:
        client.delete(f"/api/students/{sid}")

def test_update_rejects_explicit_nulls():
    # An explicit null in a partial update used to reach the database
    # and crash the endpoint with a 500 (None assigned to a NOT NULL
    # column, or .lower() called on None in the duplicate check).
    # Nulls are not valid values for any field, so they must be
    # rejected with a 422 like any other invalid input.
    payload = {
        "student_number":"TEST040","first_name":"Null","last_name":"Test",
        "email":"null.test@example.edu","major":"Computer Science","gpa":3.5,"status":"Active"
    }
    created = client.post("/api/students", json=payload)
    assert created.status_code == 201
    sid = created.json()["id"]
    try:
        for bad in ({"gpa": None}, {"email": None}, {"status": None},
                    {"major": None}, {"student_number": None},
                    {"first_name": None}, {"last_name": None}):
            assert client.put(f"/api/students/{sid}", json=bad).status_code == 422
        # A valid partial update still works after the change.
        updated = client.put(f"/api/students/{sid}", json={"gpa": 3.9})
        assert updated.status_code == 200
        assert updated.json()["gpa"] == 3.9
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
