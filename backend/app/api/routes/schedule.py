from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models.users import User
from app.api.dependencies.auth import get_current_user
from app.schemas.academic import (
    ClassScheduleCreate,
    ClassScheduleUpdate,
    ClassScheduleResponse,
    AcademicEventCreate,
    AcademicEventUpdate,
    AcademicEventResponse,
)
from app.services import academic_service

router = APIRouter()

# ─── Horario Semanal de Clases ───
@router.get("/classes", response_model=List[ClassScheduleResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna las clases semanales del usuario organizadas por día."""
    return academic_service.get_user_class_schedules(db, current_user)

@router.post("/classes", response_model=ClassScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    sched_in: ClassScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registra una nueva clase semanal en el horario."""
    return academic_service.create_class_schedule(db, current_user, sched_in)

@router.put("/classes/{sched_id}", response_model=ClassScheduleResponse)
def update_class(
    sched_id: str,
    sched_in: ClassScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una clase en el horario."""
    return academic_service.update_class_schedule(db, current_user, sched_id, sched_in)

@router.delete("/classes/{sched_id}")
def delete_class(
    sched_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una clase del horario."""
    return academic_service.delete_class_schedule(db, current_user, sched_id)


# ─── Agenda y Eventos / Recordatorios Académicos ───
@router.get("/events", response_model=List[AcademicEventResponse])
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene la lista cronológica de eventos y recordatorios académicos."""
    return academic_service.get_user_academic_events(db, current_user)

@router.post("/events", response_model=AcademicEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: AcademicEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Agenda una nueva evaluación o recordatorio académico."""
    return academic_service.create_academic_event(db, current_user, event_in)

@router.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un evento o recordatorio agendado."""
    return academic_service.delete_academic_event(db, current_user, event_id)
