from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token, AccountRecoveryRequest
from app.services import user_service
from app.db.models.users import User
from app.core import security
from app.api.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo estudiante en Académix.
    """
    user = user_service.create_user(db, user_in)
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, acepta username o email y password como form data.
    """
    user = (
        db.query(User)
        .filter(
            (User.email == form_data.username)
            | (User.username == form_data.username)
        )
        .first()
    )
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token
    access_token = security.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    return current_user

@router.post("/recover")
def recover_account(recovery_in: AccountRecoveryRequest, db: Session = Depends(get_db)):
    """
    Permite recuperar acceso o actualizar contraseña en caso de olvido.
    Busca por nombre de usuario o por correo electrónico.
    """
    ident = recovery_in.identifier.strip()
    user = (
        db.query(User)
        .filter((User.email == ident) | (User.username == ident))
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna cuenta con ese usuario o correo.",
        )

    if not recovery_in.new_password or len(recovery_in.new_password.strip()) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 4 caracteres.",
        )

    user.hashed_password = security.get_password_hash(recovery_in.new_password.strip())
    db.commit()
    db.refresh(user)

    return {
        "message": "Contraseña restablecida exitosamente",
        "username": user.username or user.email,
        "email": user.email,
    }

