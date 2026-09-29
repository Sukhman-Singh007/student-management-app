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
    student_number: str | None = Field(default=None, min_length=3, max_length=20)
    first_name: str | None = Field(default=None, min_length=1, max_length=60)
    last_name: str | None = Field(default=None, min_length=1, max_length=60)
    email: EmailStr | None = None
    major: str | None = Field(default=None, min_length=2, max_length=100)
    gpa: float | None = Field(default=None, ge=0.0, le=4.0)
    status: str | None = Field(default=None, pattern="^(Active|Inactive|Graduated)$")

class StudentOut(StudentBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
