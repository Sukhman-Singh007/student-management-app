from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class StudentBase(BaseModel):
    student_number: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    major: str = Field(min_length=2, max_length=100)
    gpa: float = Field(ge=0.0, le=4.0)
    status: str = Field(default="Active", pattern="^(Active|Inactive|Graduated)$")

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    # Fields are typed WITHOUT "| None" on purpose: an explicit null
    # in a partial update used to slip through (exclude_unset keeps
    # it) and crash the endpoint with a 500 — None was assigned to a
    # NOT NULL column, or .lower() was called on it. With the plain
    # type, a provided null fails validation with a 422 instead, while
    # an omitted field still defaults to None and is excluded.
    student_number: str = Field(default=None, min_length=3, max_length=20)
    first_name: str = Field(default=None, min_length=1, max_length=60)
    last_name: str = Field(default=None, min_length=1, max_length=60)
    email: EmailStr = Field(default=None)
    major: str = Field(default=None, min_length=2, max_length=100)
    gpa: float = Field(default=None, ge=0.0, le=4.0)
    status: str = Field(default=None, pattern="^(Active|Inactive|Graduated)$")

class StudentOut(StudentBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
