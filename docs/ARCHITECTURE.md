# Arquitectura de Académix (Fase 1)

## 1. Arquitectura General
Académix utiliza una arquitectura cliente-servidor desacoplada:
- **Cliente (Frontend):** Aplicación móvil renderizada con Flet (Python), que maneja estado local y vistas.
- **Servidor (Backend):** API RESTful desarrollada en FastAPI, responsable de la seguridad, lógica de negocio y comunicación con la BD.
- **Base de Datos:** MySQL, conectada al backend mediante SQLAlchemy 2.x (ORM).

## 2. Flujo de Información
`Frontend (Flet) -> HTTP POST/GET (JSON) -> FastAPI -> Pydantic Schema -> Service/Domain -> SQLAlchemy -> MySQL`

## 3. Estructura de Carpetas del Repositorio
```text
academix-pro/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/  # Inyección (ej. get_current_user, get_db)
│   │   │   └── routes/        # Endpoints por dominio (auth, subjects, grades)
│   │   ├── core/              # Configuración (settings, JWT, security)
│   │   ├── db/                # Conexión MySQL, base models (DeclarativeBase)
│   │   │   └── models/        # Entidades SQLAlchemy (Tablas)
│   │   ├── domain/            # Motor de cálculo de notas puro
│   │   ├── schemas/           # Pydantic In/Out / Validaciones
│   │   └── services/          # Lógica de negocio (orquestación)
│   ├── alembic/               # Migraciones de esquema
│   ├── tests/                 # Pytest
│   ├── main.py                # Entrada FastAPI
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── api/               # Cliente HTTP (encapsula requests a FastAPI)
│   │   ├── core/              # Estado, Auth local
│   │   ├── models/            # Modelos de datos del frontend
│   │   ├── screens/           # Vistas (Login, Dashboard, SubjectDetail)
│   │   ├── theme/             # Sistema de diseño, colores, fuentes
│   │   └── widgets/           # Componentes reutilizables (Cards, Botones)
│   ├── assets/                # Imágenes, íconos
│   ├── main.py                # Entrada Flet
│   └── requirements.txt
│
├── database/                  # Documentación BD, ERD, scripts manuales
├── docs/                      # ARCHITECTURE.md, DATABASE.md, API.md
├── .env.example
├── .gitignore
└── README.md
```

## 4. Decisiones Tecnológicas
- **Python:** Lenguaje unificado en Backend y Frontend.
- **FastAPI:** Velocidad y validación de tipos automática.
- **Flet:** Permite UI fluida y nativa desde Python, ideal para el stack unificado.
- **Passlib/Bcrypt:** Hashing estándar y seguro para contraseñas.

## 5. Estrategia de Despliegue (Render)
El backend se expondrá como un "Web Service". La aplicación leerá variables como `DATABASE_URL` y `SECRET_KEY` del entorno de Render. El comando de inicio será:
`alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
