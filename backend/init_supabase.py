import sys
import os

# Configurar stdout a UTF-8 para evitar errores de codificación en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Asegurar que el backend esté en el sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from sqlalchemy import text, inspect
from app.core.config import settings
from app.db.database import engine, SessionLocal, Base
# Importar todos los modelos para registrarlos en Base.metadata
from app.db.models.users import User, UserProfile, AcademicSettings, StudentType
from app.db.models.academic import AcademicPeriod, Subject, Evaluation, Grade, ClassSchedule, AcademicEvent, PrediccionNota, EvalType
from app.core.security import get_password_hash

def init_supabase():
    print("=" * 60)
    print("[*] INICIALIZADOR DE BASE DE DATOS SUPABASE - ACADEMIX PRO")
    print("=" * 60)
    
    masked_url = settings.sync_database_url
    if "@" in masked_url:
        proto_user, host_db = masked_url.split("@", 1)
        masked_url = f"{proto_user.split(':')[0]}://****:****@{host_db}"
    print(f"[*] Conectando a: {masked_url}")

    # 1. Test de conexión
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version_row = result.fetchone()
            print(f"[OK] Conexion exitosa a la base de datos Supabase!")
            if version_row:
                print(f"[OK] Version: {version_row[0]}")
    except Exception as e:
        print(f"\n[ERROR] Error al conectar a la base de datos:")
        print(f"   {e}")
        print("\nSugerencia:")
        print("   Verifica que la contrasena de Supabase sea correcta y que la IP tenga acceso.")
        sys.exit(1)

    # 2. Crear todas las tablas
    print("\n[*] Creando tablas en Supabase si no existen...")
    try:
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"[OK] Tablas detectadas en la base de datos ({len(tables)}):")
        for t in sorted(tables):
            print(f"   - {t}")
    except Exception as e:
        print(f"[ERROR] Error al crear tablas: {e}")
        sys.exit(1)

    # 3. Sembrar usuario administrador inicial
    print("\n[*] Verificando usuario Administrador inicial...")
    db = SessionLocal()
    try:
        admin_username = settings.ADMIN_USERNAME
        admin_password = settings.ADMIN_PASSWORD
        admin_email = os.getenv("ADMIN_EMAIL", "admin@academix.com")

        existing_user = db.query(User).filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()

        if existing_user:
            print(f"[INFO] El usuario administrador '{admin_username}' ya existe (ID: {existing_user.id}).")
        else:
            print(f"[*] Creando usuario administrador '{admin_username}'...")
            admin_user = User(
                email=admin_email,
                username=admin_username,
                hashed_password=get_password_hash(admin_password),
                is_active=True
            )
            db.add(admin_user)
            db.flush()

            # Perfil
            admin_profile = UserProfile(
                user_id=admin_user.id,
                first_name="Diego",
                last_name="Administrador",
                student_type=StudentType.university,
                institution_name="Academix Pro",
                avatar_url=None
            )
            db.add(admin_profile)

            # Ajustes académicos
            admin_settings = AcademicSettings(
                user_id=admin_user.id,
                min_grade=0.0,
                max_grade=20.0,
                passing_grade=10.0,
                evaluation_mode="university",
                default_eval_count=5
            )
            db.add(admin_settings)

            db.commit()
            print(f"[OK] Administrador creado exitosamente:")
            print(f"   Usuario: {admin_username}")
            print(f"   Email:   {admin_email}")
            print(f"   Clave:   {admin_password}")

        print("\n[SUCCESS] Base de datos en Supabase lista y sincronizada con Academix Pro!")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al crear usuario administrador: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_supabase()
