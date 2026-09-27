from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.users import User
from app.schemas.user import UserResponse, UserProfileUpdate, AcademicSettingsResponse, AcademicSettingsUpdate, UserCredentialsUpdate
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

@router.put("/me/credentials", response_model=UserResponse)
def update_my_credentials(
    cred_in: UserCredentialsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza las credenciales de acceso del usuario autenticado (nombre de usuario, correo, contraseña)
    sin modificar ni perjudicar sus periodos, materias, horarios ni evaluaciones.
    """
    from app.core import security

    if cred_in.username:
        new_uname = cred_in.username.strip()
        existing = db.query(User).filter(User.username == new_uname, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ese nombre de usuario ya está registrado.")
        current_user.username = new_uname

    if cred_in.email:
        new_email = cred_in.email.strip()
        existing = db.query(User).filter(User.email == new_email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ese correo electrónico ya está registrado.")
        current_user.email = new_email

    if cred_in.password and cred_in.password.strip():
        current_user.hashed_password = security.get_password_hash(cred_in.password.strip())

    db.commit()
    db.refresh(current_user)
    return current_user

