# Diseño de Base de Datos - Académix (Fase 2)

## 1. Diagrama Conceptual y Entidades Principales

Hemos diseñado las entidades para asegurar que los promedios y escalas puedan variar por usuario y por materia, sin redundancia innecesaria. 

### Entidades y Propósito:
- **`users`**: Datos de acceso y seguridad (email, password).
- **`user_profiles`**: Datos públicos del estudiante (tipo de estudiante, institución).
- **`academic_settings`**: Escala de notas por defecto del usuario (ej. max: 20, aprueba: 10).
- **`academic_periods`**: Semestres o lapsos (ej. "Semestre 1 2024").
- **`subjects`**: Materias. Tienen configuración para anular (override) la escala de notas si una materia específica califica distinto (ej. base 100).
- **`evaluations`**: Exámenes, talleres, parciales. Guardan su peso porcentual.
- **`grades`**: La nota definitiva obtenida en una evaluación.

## 2. Relaciones y Multiplicidades
- `users` 1 <--> 1 `user_profiles`
- `users` 1 <--> 1 `academic_settings`
- `users` 1 <--> N `academic_periods`
- `academic_periods` 1 <--> N `subjects`
- `subjects` 1 <--> N `evaluations`
- `evaluations` 1 <--> 1 `grades` (Si se anula una nota, se actualiza, no se crea otra. Si existe "recuperativo", lo manejaremos en la entidad `evaluations` como tipo especial para mantener integridad).

## 3. Modelo Físico (Columnas y Restricciones)

### Tabla `users`
- `id`: CHAR(36) UUID, Primary Key.
- `email`: VARCHAR(255), Unique, Not Null, Index.
- `hashed_password`: VARCHAR(255), Not Null.
- `is_active`: BOOLEAN, Default True.
- `created_at`: TIMESTAMP, Default NOW.

### Tabla `user_profiles`
- `id`: CHAR(36) UUID, Primary Key.
- `user_id`: CHAR(36), Foreign Key (`users.id`), Unique, Not Null, Index.
- `first_name`: VARCHAR(100), Not Null.
- `last_name`: VARCHAR(100), Not Null.
- `student_type`: ENUM('high_school', 'university'), Not Null.
- `institution_name`: VARCHAR(255).
- `avatar_url`: VARCHAR(255).

### Tabla `academic_settings`
- `id`: CHAR(36) UUID, Primary Key.
- `user_id`: CHAR(36), Foreign Key (`users.id`), Unique, Not Null, Index.
- `min_grade`: FLOAT, Default 0.
- `max_grade`: FLOAT, Default 20.
- `passing_grade`: FLOAT, Default 10.

### Tabla `academic_periods`
- `id`: CHAR(36) UUID, Primary Key.
- `user_id`: CHAR(36), Foreign Key (`users.id`), Not Null, Index.
- `name`: VARCHAR(100), Not Null (Ej. "Semestre I", "Lapso 2").
- `start_date`: DATE.
- `end_date`: DATE.
- `is_active`: BOOLEAN, Default True.

### Tabla `subjects`
- `id`: CHAR(36) UUID, Primary Key.
- `period_id`: CHAR(36), Foreign Key (`academic_periods.id`), Not Null, Index.
- `name`: VARCHAR(100), Not Null.
- `color_hex`: VARCHAR(7), Default '#3B82F6'.
- `passing_grade_override`: FLOAT, Nullable (Si es NULL, usa la de `academic_settings`).
- `max_grade_override`: FLOAT, Nullable.
- `credits`: INT, Default 0 (Para universidades).
- `is_archived`: BOOLEAN, Default False.

### Tabla `evaluations`
- `id`: CHAR(36) UUID, Primary Key.
- `subject_id`: CHAR(36), Foreign Key (`subjects.id`), Not Null, Index.
- `name`: VARCHAR(100), Not Null (Ej. "Parcial 1").
- `eval_type`: ENUM('exam', 'quiz', 'project', 'homework', 'other'), Default 'exam'.
- `weight_percent`: FLOAT, Not Null (Ej. 25.0).
- `date`: DATE, Nullable.

### Tabla `grades`
- `id`: CHAR(36) UUID, Primary Key.
- `evaluation_id`: CHAR(36), Foreign Key (`evaluations.id`), Unique, Not Null, Index.
- `score`: FLOAT, Not Null.
- `notes`: TEXT, Nullable.

## 4. Estrategia de Borrado e Integridad (ON DELETE)
- Si se borra un `user`, se borra TODO en cascada.
- Si se borra un `period`, se borran las `subjects` asociadas.
- *Nota:* Se priorizará "Soft Delete" en la API, pero en BD configuraremos `ON DELETE CASCADE` para mantener integridad referencial limpia si hacemos hard deletes.

## 5. SQL Inicial (Generado pero no ejecutado aún)
(Ver archivo `database/init.sql` cuando se requiera).
