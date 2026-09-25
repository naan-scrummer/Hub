from typing import Literal, Union, Annotated
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class BaseUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True

class StudentProfileResponse(BaseModel):
    id: int
    student_id: str
    department: str | None
    semester: int | None
    section: str | None

    class Config:
        from_attributes = True

class TeacherProfileResponse(BaseModel):
    id: int
    employee_id: str
    department: str
    designation: str
    office_location: str | None

    class Config:
        from_attributes = True

class StudentUserResponse(BaseUserResponse):
    role: Literal["student"]
    profile: StudentProfileResponse | None = None

class TeacherUserResponse(BaseUserResponse):
    role: Literal["teacher"]
    profile: TeacherProfileResponse | None = None

class AdminUserResponse(BaseUserResponse):
    role: Literal["admin"]

UserResponse = Annotated[Union[StudentUserResponse, TeacherUserResponse, AdminUserResponse], Field(discriminator="role")]

