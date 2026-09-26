from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.db.models.academic import EvalType


# ─── Schemas para AcademicPeriod ───
class AcademicPeriodCreate(BaseModel):
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True

class AcademicPeriodResponse(BaseModel):
    id: str
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool

    class Config:
        from_attributes = True


# ─── Schemas para Grade ───
class GradeCreate(BaseModel):
    score: float
    notes: Optional[str] = None

class GradeResponse(BaseModel):
    id: str
    evaluation_id: str
    score: float
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Schemas para Evaluation ───
class EvaluationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    eval_type: EvalType = EvalType.exam
    weight_percent: float = Field(..., gt=0, le=100)
    date: Optional[date] = None
    score: Optional[float] = None  # Nota opcional al crear

class EvaluationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    eval_type: Optional[EvalType] = None
    weight_percent: Optional[float] = None
    date: Optional[date] = None
    score: Optional[float] = None
    status: Optional[str] = None

class EvaluationResponse(BaseModel):
    id: str
    subject_id: str
    name: str
    description: Optional[str] = None
    eval_type: EvalType
    weight_percent: float
    date: Optional[date] = None
    status: str = "pendiente"
    max_grade: float = 20.0
    points_earned: Optional[float] = None  # Aporte real a la definitiva: score * (weight / 100)
    grade: Optional[GradeResponse] = None

    class Config:
        from_attributes = True


# ─── Schemas para Subject ───
class SubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None
    color_hex: Optional[str] = "#00E5FF"
    passing_grade_override: Optional[float] = None
    max_grade_override: Optional[float] = None
    target_grade: Optional[float] = 20.0
    credits: Optional[int] = 0
    max_evaluations: Optional[int] = None
    period_id: Optional[str] = None

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    color_hex: Optional[str] = None
    passing_grade_override: Optional[float] = None
    max_grade_override: Optional[float] = None
    target_grade: Optional[float] = None
    credits: Optional[int] = None
    max_evaluations: Optional[int] = None
    is_archived: Optional[bool] = None

class SubjectResponse(BaseModel):
    id: str
    period_id: str
    name: str
    code: Optional[str] = None
    color_hex: str
    passing_grade_override: Optional[float] = None
    max_grade_override: Optional[float] = None
    target_grade: float = 20.0
    credits: int
    max_evaluations: Optional[int] = None
    is_archived: bool
    # Métricas de Cálculo Adaptativo:
    accumulated_points: float = 0.0          # Ej: 9.40 / 20 pts ganados
    accumulated_percent: float = 0.0         # Ej: 60.0% evaluado
    current_average: Optional[float] = None  # Rendimiento sobre lo evaluado (ej: 15.67)
    max_scale: float = 20.0                  # Escala máxima (ej: 20.0)
    passing_grade: float = 10.0              # Nota mínima para aprobar (ej: 10.0 o 9.5)
    points_needed_to_pass: float = 0.0       # Puntos que faltan para aprobar (ej: 0.60)
    is_passed: bool = False                  # True si ya alcanzó la nota aprobatoria
    max_possible_grade: float = 20.0         # Nota máxima alcanzable si saca 20 en lo restante
    required_average_remaining: Optional[float] = None # Nota promedio requerida en lo que falta
    evaluations: List[EvaluationResponse] = []

    class Config:
        from_attributes = True


# ─── Schemas para Horario de Clases (ClassSchedule) ───
class ClassScheduleCreate(BaseModel):
    subject_id: str
    day_of_week: int = Field(..., ge=0, le=6) # 0=Lunes, 6=Domingo
    start_time: str
    end_time: str
    classroom: Optional[str] = None
    professor: Optional[str] = None

class ClassScheduleUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    classroom: Optional[str] = None
    professor: Optional[str] = None

class ClassScheduleResponse(BaseModel):
    id: str
    subject_id: str
    subject_name: str
    color_hex: str
    day_of_week: int
    start_time: str
    end_time: str
    classroom: Optional[str] = None
    professor: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Schemas para Agenda y Eventos Académicos (AcademicEvent) ───
class AcademicEventCreate(BaseModel):
    subject_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    event_date: datetime
    reminder_lead_time_hours: int = 24

class AcademicEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    reminder_lead_time_hours: Optional[int] = None
    is_notified: Optional[bool] = None

class AcademicEventResponse(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None
    color_hex: Optional[str] = None
    evaluation_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    event_date: datetime
    reminder_lead_time_hours: int
    is_notified: bool

    class Config:
        from_attributes = True


# ─── Schemas para Estadísticas Reales del Dashboard ───
class AcademicStatsResponse(BaseModel):
    gpa: Optional[float] = None
    max_scale: float = 20.0
    passing_grade: float = 10.0
    active_subjects_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    total_evaluations_count: int = 0
    subjects: List[SubjectResponse] = []


# ─── Schemas para la Calculadora Predictiva de Notas ───
class PredictionRequest(BaseModel):
    subject_id: str
    target_grade: float
    total_evaluations: Optional[int] = None
    total_evaluaciones: Optional[int] = None
    min_grade: Optional[float] = None
    max_grade: Optional[float] = None

class PredictionResponse(BaseModel):
    id: str
    subject_id: str
    subject_name: str
    color_hex: str
    nota_minima_usada: float
    nota_maxima_usada: float
    total_evaluaciones_usadas: int
    evaluaciones_realizadas_momento: int
    evaluaciones_restantes: int
    nota_deseada: float
    nota_requerida_por_evaluacion: Optional[float] = None
    puntos_actuales_acumulados: float
    porcentaje_actual_evaluado: float
    nota_maxima_posible: float
    es_posible: bool
    mensaje_resultado: str
    estado: str  # "meta_alcanzada", "posible", "imposible", "completada"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
