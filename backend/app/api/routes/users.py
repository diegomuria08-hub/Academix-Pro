from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.users import User
from app.schemas.user import UserResponse, UserProfileUpdate, AcademicSettingsResponse, AcademicSettingsUpdate
from app.services import user_service
from app.api.dependencies.auth import get_current_user

router = APIRouter()

@router.put("/me/profile", response_model=UserResponse)
def update_my_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza los datos personales del usuario autenticado
    (nombre, apellido, institución, tipo de estudiante).
    """
    return user_service.update_user_profile(db, current_user, profile_in)

@router.get("/me/settings", response_model=AcademicSettingsResponse)
def get_my_settings(current_user: User = Depends(get_current_user)):
    """
    Obtiene la configuración académica actual del usuario (escala de notas).
    """
    if not current_user.settings:
        raise HTTPException(status_code=404, detail="Configuración académica no encontrada")
    return current_user.settings

@router.put("/me/settings", response_model=AcademicSettingsResponse)
def update_my_settings(
    settings_in: AcademicSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza la configuración académica del usuario (escala de notas).
    Ejemplo: min=0, max=20, passing=10 para el sistema venezolano.
    """
    user = user_service.update_academic_settings(db, current_user, settings_in)
    return user.settings
