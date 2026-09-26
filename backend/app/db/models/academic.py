from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Float, Enum, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base
import enum

class EvalType(str, enum.Enum):
    exam = "exam"
    quiz = "quiz"
    project = "project"
    homework = "homework"
    other = "other"

class AcademicPeriod(Base):
    __tablename__ = "academic_periods"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="periods")
    subjects = relationship("Subject", back_populates="period", cascade="all, delete-orphan")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    period_id = Column(String(36), ForeignKey("academic_periods.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=True)
    color_hex = Column(String(7), default="#00E5FF")
    passing_grade_override = Column(Float, nullable=True)
    max_grade_override = Column(Float, nullable=True)
    target_grade = Column(Float, default=20.0)
    credits = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    
    period = relationship("AcademicPeriod", back_populates="subjects")
    evaluations = relationship("Evaluation", back_populates="subject", cascade="all, delete-orphan")
    schedules = relationship("ClassSchedule", back_populates="subject", cascade="all, delete-orphan")
    events = relationship("AcademicEvent", back_populates="subject", cascade="all, delete-orphan")
    predictions = relationship("PrediccionNota", back_populates="subject", cascade="all, delete-orphan")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    eval_type = Column(Enum(EvalType), default=EvalType.exam)
    weight_percent = Column(Float, nullable=False)
    date = Column(Date, nullable=True)
    status = Column(String(20), default="pendiente")
    max_grade = Column(Float, default=20.0)
    
    subject = relationship("Subject", back_populates="evaluations")
    grade = relationship("Grade", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")
    events = relationship("AcademicEvent", back_populates="evaluation", cascade="all, delete-orphan")

class Grade(Base):
    __tablename__ = "grades"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id = Column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), unique=True, nullable=False)
    score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    
    evaluation = relationship("Evaluation", back_populates="grade")

class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False) # 0=Lunes, 1=Martes, 2=Miercoles, 3=Jueves, 4=Viernes, 5=Sabado, 6=Domingo
    start_time = Column(String(10), nullable=False) # ej: "08:00"
    end_time = Column(String(10), nullable=False)   # ej: "10:00"
    classroom = Column(String(100), nullable=True)  # ej: "Aula 302", "Lab Redes"
    professor = Column(String(100), nullable=True)  # ej: "Prof. Ramírez"
    
    subject = relationship("Subject", back_populates="schedules")

class AcademicEvent(Base):
    __tablename__ = "academic_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    reminder_lead_time_hours = Column(Integer, default=24)
    is_notified = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="events")
    subject = relationship("Subject", back_populates="events")
    evaluation = relationship("Evaluation", back_populates="events")

class PrediccionNota(Base):
    __tablename__ = "predicciones_notas"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    nota_minima_usada = Column(Float, nullable=False)
    nota_maxima_usada = Column(Float, nullable=False)
    total_evaluaciones_usadas = Column(Integer, nullable=False)
    evaluaciones_realizadas_momento = Column(Integer, nullable=False)
    evaluaciones_restantes = Column(Integer, nullable=False)
    nota_deseada = Column(Float, nullable=False)
    nota_requerida_por_evaluacion = Column(Float, nullable=True)
    es_posible = Column(Boolean, nullable=False)
    mensaje_resultado = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="predictions")
    subject = relationship("Subject", back_populates="predictions")
