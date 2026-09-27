from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models.users import StudentType

# Schemas para el Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Schemas para Creación de Usuario
class UserCreate(BaseModel):
    email: str
    username: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    student_type: StudentType
    institution_name: Optional[str] = None

# Schemas de Salida
class UserProfileResponse(BaseModel):
    first_name: str
    last_name: str
    student_type: StudentType
    institution_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    student_type: Optional[StudentType] = None
    institution_name: Optional[str] = None
    avatar_url: Optional[str] = None

class AcademicSettingsResponse(BaseModel):
    min_grade: float
    max_grade: float
    passing_grade: float
    evaluation_mode: str = "university"
    default_eval_count: int = 5

    class Config:
        from_attributes = True

class AcademicSettingsUpdate(BaseModel):
    min_grade: Optional[float] = None
    max_grade: Optional[float] = None
    passing_grade: Optional[float] = None
    evaluation_mode: Optional[str] = None
    default_eval_count: Optional[int] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    is_active: bool
    profile: Optional[UserProfileResponse] = None
    settings: Optional[AcademicSettingsResponse] = None

    class Config:
        from_attributes = True

class UserCredentialsUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class AccountRecoveryRequest(BaseModel):
    identifier: str
    new_password: str
