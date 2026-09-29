<<<<<<< HEAD
# Student Management Web Application

**Developed by Sukhman Singh**

A full-stack academic record management application built with Python, FastAPI, PostgreSQL, SQLAlchemy, JavaScript, HTML/CSS, and Git.

## Features
- Create, read, update, and delete student records
- Search students by name, email, or student ID
- Filter by academic status
- Dashboard statistics for students, GPA, and majors
- PostgreSQL persistence with SQLAlchemy
- Pydantic request validation
- Structured HTTP error handling (404, 409, 422, 500)
- Database rollback on failed writes
- RESTful API with interactive FastAPI documentation
- Automated CRUD and validation tests
- Responsive JavaScript dashboard

## Local Setup

### 1. Create the PostgreSQL database
```sql
CREATE DATABASE student_management;
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the database
```bash
cp .env.example .env
```
Export your connection string before starting:
```bash
export DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/student_management"
```

### 5. Add sample records
```bash
python seed.py
```

### 6. Run the application
```bash
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

API documentation: `http://127.0.0.1:8000/docs`

### 7. Run tests
```bash
pytest -v
```

## REST API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/students` | List/search students |
| GET | `/api/students/{id}` | Get one student |
| POST | `/api/students` | Add student |
| PUT | `/api/students/{id}` | Update student |
| DELETE | `/api/students/{id}` | Delete student |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/benchmark` | Measure DB query latency |

## Resume accuracy
The application genuinely implements FastAPI, PostgreSQL, REST APIs, structured error handling, validation, transactions, rollback behavior, and automated integration-style API tests.

Do not claim a specific performance improvement such as “40% faster” until you have measured a baseline and compared it with this implementation. Likewise, phrase reliability claims around the tests actually performed rather than claiming production outcomes that were not measured.
=======
# student-management-app
Full-stack student management application built with FastAPI, PostgreSQL, JavaScript, and REST APIs.
>>>>>>> 5ef46121bd0075e8649002097779c893d4c1c409
