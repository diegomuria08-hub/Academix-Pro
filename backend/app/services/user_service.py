from sqlalchemy.orm import Session
from app.db.models.users import User, UserProfile, AcademicSettings
from app.schemas.user import UserCreate, UserProfileUpdate, AcademicSettingsUpdate
from app.core.security import get_password_hash
from fastapi import HTTPException

def create_user(db: Session, user_in: UserCreate) -> User:
    # Check if email exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create User
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(db_user)
    db.flush() # To get the db_user.id
    
    # Create Profile
    db_profile = UserProfile(
        user_id=db_user.id,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        student_type=user_in.student_type,
        institution_name=user_in.institution_name,
    )
    db.add(db_profile)
    
    # Create default Academic Settings (0-20 scale, passing 10)
    is_liceo = str(user_in.student_type) in ["high_school", "StudentType.high_school"]
    db_settings = AcademicSettings(
        user_id=db_user.id,
        min_grade=0.0,
        max_grade=20.0,
        passing_grade=10.0,
        evaluation_mode="liceo" if is_liceo else "university",
        default_eval_count=4 if is_liceo else 5,
        total_lapsos=3 if is_liceo else 1,
        current_lapso=1,
    )
    db.add(db_settings)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user: User, profile_in: UserProfileUpdate) -> User:
    """Actualiza los datos del perfil del usuario y sincroniza su modalidad académica."""
    profile = user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
    
    old_type = profile.student_type
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    # Si cambió la modalidad entre Liceo y Universidad
    new_type = profile.student_type
    if old_type != new_type:
        new_st_str = new_type.value if hasattr(new_type, "value") else str(new_type)
        is_liceo = new_st_str in ["high_school", "StudentType.high_school"]
        if user.settings:
            user.settings.evaluation_mode = "liceo" if is_liceo else "university"
            if is_liceo:
                user.settings.total_lapsos = 3
                user.settings.current_lapso = 1
                user.settings.default_eval_count = 4
            else:
                user.settings.total_lapsos = 1
                user.settings.current_lapso = 1
                user.settings.default_eval_count = 5
            db.add(user.settings)
        
        # Sincronizar y activar el periodo adecuado de esa modalidad conservando el historial
        from app.services.academic_service import get_or_create_active_period
        get_or_create_active_period(db, user.id, new_st_str)

    db.add(profile)
    db.commit()
    db.refresh(user)
    return user

def update_academic_settings(db: Session, user: User, settings_in: AcademicSettingsUpdate) -> User:
    """Actualiza la configuración académica (escala de notas) del usuario."""
    settings = user.settings
    if not settings:
        # Si no tiene settings, las creamos con los valores proporcionados
        settings = AcademicSettings(user_id=user.id)
        db.add(settings)
    
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.add(settings)
    db.commit()
    db.refresh(user)
    return user
