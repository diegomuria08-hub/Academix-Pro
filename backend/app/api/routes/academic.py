from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models.users import User
from app.api.dependencies.auth import get_current_user
from app.schemas.academic import (
    AcademicStatsResponse,
    SubjectResponse,
    SubjectCreate,
    SubjectUpdate,
    EvaluationResponse,
    EvaluationCreate,
    EvaluationUpdate,
    PredictionRequest,
    PredictionResponse,
)
from app.services import academic_service

router = APIRouter()

@router.get("/stats", response_model=AcademicStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna las estadísticas reales del usuario en base a sus materias y notas."""
    return academic_service.get_academic_stats(db, current_user)

@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las materias activas del periodo actual con sus evaluaciones y notas."""
    return academic_service.get_user_subjects(db, current_user)

@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva materia."""
    return academic_service.create_subject(db, current_user, subject_in)

@router.put("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: str,
    subject_in: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una materia existente."""
    return academic_service.update_subject(db, current_user, subject_id, subject_in)

@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una materia y todas sus evaluaciones."""
    return academic_service.delete_subject(db, current_user, subject_id)

@router.post("/subjects/{subject_id}/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    subject_id: str,
    eval_in: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registra una nueva evaluación con ponderación y calificación opcional."""
    return academic_service.create_evaluation(db, current_user, subject_id, eval_in)

@router.put("/evaluations/{eval_id}", response_model=EvaluationResponse)
def update_evaluation(
    eval_id: str,
    eval_in: EvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una evaluación existente o asigna/modifica su nota."""
    return academic_service.update_evaluation(db, current_user, eval_id, eval_in)

@router.delete("/evaluations/{eval_id}")
def delete_evaluation(
    eval_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una evaluación."""
    return academic_service.delete_evaluation(db, current_user, eval_id)


# ─── Calculadora Predictiva ───
@router.post("/calculator/simulate", response_model=PredictionResponse)
def simulate_prediction(
    req: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calcula y persiste una proyección predictiva de notas para una materia."""
    return academic_service.calculate_grade_prediction(db, current_user, req)


@router.get("/calculator/history", response_model=List[PredictionResponse])
def get_prediction_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna las últimas simulaciones guardadas por el usuario."""
    return academic_service.get_user_predictions(db, current_user, limit=limit)
