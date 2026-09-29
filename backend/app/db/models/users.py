from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base
import enum

class StudentType(str, enum.Enum):
    high_school = "high_school"
    university = "university"

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    settings = relationship("AcademicSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    periods = relationship("AcademicPeriod", back_populates="user", cascade="all, delete-orphan")
    events = relationship("AcademicEvent", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("PrediccionNota", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    student_type = Column(Enum(StudentType), nullable=False)
    institution_name = Column(String(255), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="profile")

class AcademicSettings(Base):
    __tablename__ = "academic_settings"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    min_grade = Column(Float, default=0.0)
    max_grade = Column(Float, default=20.0)
    passing_grade = Column(Float, default=10.0)
    evaluation_mode = Column(String(30), default="university") # "university" (ponderado) o "liceo" (equitativo/simple)
    default_eval_count = Column(Integer, default=5)
    total_lapsos = Column(Integer, default=3, nullable=False)
    current_lapso = Column(Integer, default=1, nullable=False)
    
    user = relationship("User", back_populates="settings")
