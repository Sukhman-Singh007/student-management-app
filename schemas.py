from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, ConfigDict, StringConstraints

class StudentBase(BaseModel):
    # strip_whitespace: a value pasted with leading/trailing spaces
    # ("  Data Science  ") used to be stored padded, so the major
    # filter — which compares the exact lowercased string — could
    # never find it. Values are trimmed before the length checks.
    student_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=20)]
    first_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
    last_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
    email: EmailStr
    major: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
    gpa: float = Field(ge=0.0, le=4.0)
    status: Annotated[str, StringConstraints(strip_whitespace=True, pattern="^(Active|Inactive|Graduated)$")] = Field(default="Active")

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    # Fields are typed WITHOUT "| None" on purpose: an explicit null
    # in a partial update used to slip through (exclude_unset keeps
    # it) and crash the endpoint with a 500 — None was assigned to a
    # NOT NULL column, or .lower() was called on it. With the plain
    # type, a provided null fails validation with a 422 instead, while
    # an omitted field still defaults to None and is excluded.
    student_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=20)] = Field(default=None)
    first_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)] = Field(default=None)
    last_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)] = Field(default=None)
    email: EmailStr = Field(default=None)
    major: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)] = Field(default=None)
    gpa: float = Field(default=None, ge=0.0, le=4.0)
    status: Annotated[str, StringConstraints(strip_whitespace=True, pattern="^(Active|Inactive|Graduated)$")] = Field(default=None)

class StudentOut(StudentBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
