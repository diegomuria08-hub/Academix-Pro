from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Configuración dinámica del pool según motor (PostgreSQL/Supabase o MySQL)
db_url = settings.sync_database_url
engine_kwargs = {
    "pool_pre_ping": True,
}

if db_url.startswith("mysql"):
    engine_kwargs["pool_recycle"] = 3600
else:
    # Optimización para Supabase / PostgreSQL
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Dependencia para inyectar la sesión en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
