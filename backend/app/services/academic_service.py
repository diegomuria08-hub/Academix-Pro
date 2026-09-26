from sqlalchemy.orm import Session, joinedload
from app.db.models.academic import (
    AcademicPeriod,
    Subject,
    Evaluation,
    Grade,
    ClassSchedule,
    AcademicEvent,
    PrediccionNota,
)
from app.db.models.users import User, AcademicSettings
from app.schemas.academic import (
    AcademicPeriodCreate,
    SubjectCreate,
    SubjectUpdate,
    EvaluationCreate,
    EvaluationUpdate,
    AcademicStatsResponse,
    SubjectResponse,
    EvaluationResponse,
    GradeResponse,
    ClassScheduleCreate,
    ClassScheduleUpdate,
    ClassScheduleResponse,
    AcademicEventCreate,
    AcademicEventUpdate,
    AcademicEventResponse,
    PredictionRequest,
    PredictionResponse,
)
from fastapi import HTTPException
import uuid


def get_or_create_active_period(db: Session, user_id: str) -> AcademicPeriod:
    """Retorna el periodo académico activo o crea uno por defecto si no existe."""
    period = (
        db.query(AcademicPeriod)
        .filter(AcademicPeriod.user_id == user_id, AcademicPeriod.is_active == True)
        .first()
    )
    if not period:
        period = AcademicPeriod(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name="Periodo Académico Actual",
            is_active=True,
        )
        db.add(period)
        db.commit()
        db.refresh(period)
    return period


def calculate_subject_metrics(
    subject: Subject,
    default_passing: float = 10.0,
    default_max: float = 20.0,
    evaluation_mode: str = "university",
    default_eval_count: int = 5,
):
    """
    Motor de Cálculo Académico Adaptativo:
    - Escala 0 a 20 institucional (o configurada).
    - Cálculo de Puntos Reales Ganados (Aporte a la Definitiva = Nota * Peso%).
    - Proyección matemática: Puntos faltantes para aprobar, nota máxima posible
      y promedio requerido en el porcentaje restante.
    """
    passing_score = subject.passing_grade_override if subject.passing_grade_override is not None else default_passing
    max_score = subject.max_grade_override if subject.max_grade_override is not None else default_max

    accumulated_points = 0.0
    evaluated_weight = 0.0

    eval_responses = []
    for ev in subject.evaluations:
        grade_resp = None
        points_earned = None
        status = ev.status or "pendiente"

        if ev.grade is not None and ev.grade.score is not None:
            grade_resp = GradeResponse(
                id=ev.grade.id,
                evaluation_id=ev.grade.evaluation_id,
                score=ev.grade.score,
                notes=ev.grade.notes,
            )
            status = "calificada"
            # Cálculo de Puntos Reales Ganados hacia los 20 finales
            points_earned = round(ev.grade.score * (ev.weight_percent / 100.0), 2)
            accumulated_points += points_earned
            evaluated_weight += ev.weight_percent

        eval_responses.append(
            EvaluationResponse(
                id=ev.id,
                subject_id=ev.subject_id,
                name=ev.name,
                description=ev.description,
                eval_type=ev.eval_type,
                weight_percent=ev.weight_percent,
                date=ev.date,
                status=status,
                max_grade=ev.max_grade or 20.0,
                points_earned=points_earned,
                grade=grade_resp,
            )
        )

    accumulated_points = round(accumulated_points, 2)
    evaluated_weight = round(evaluated_weight, 1)

    # Rendimiento porcentual normalizado sobre lo evaluado
    if evaluated_weight > 0:
        current_avg = round((accumulated_points / evaluated_weight) * 100.0, 2)
    else:
        current_avg = None

    # Estado de Aprobación y Proyección
    is_passed = accumulated_points >= passing_score
    points_needed = round(max(0.0, passing_score - accumulated_points), 2) if not is_passed else 0.0

    remaining_weight = max(0.0, round(100.0 - evaluated_weight, 1))
    max_possible = min(max_score, round(accumulated_points + max_score * (remaining_weight / 100.0), 2))

    required_avg_remaining = None
    if is_passed:
        required_avg_remaining = 0.0
    elif remaining_weight > 0:
        req = points_needed / (remaining_weight / 100.0)
        required_avg_remaining = round(req, 2)
    else:
        required_avg_remaining = None  # Imposible si ya se evaluó 100% y no llegó a passing_score

    return SubjectResponse(
        id=subject.id,
        period_id=subject.period_id,
        name=subject.name,
        code=subject.code,
        color_hex=subject.color_hex or "#00E5FF",
        passing_grade_override=subject.passing_grade_override,
        max_grade_override=subject.max_grade_override,
        target_grade=subject.target_grade or max_score,
        credits=subject.credits or 0,
        is_archived=subject.is_archived or False,
        accumulated_points=accumulated_points,
        accumulated_percent=evaluated_weight,
        current_average=current_avg,
        max_scale=max_score,
        passing_grade=passing_score,
        points_needed_to_pass=points_needed,
        is_passed=is_passed,
        max_possible_grade=max_possible,
        required_average_remaining=required_avg_remaining,
        evaluations=eval_responses,
    ), accumulated_points, current_avg, passing_score, is_passed


def get_user_subjects(db: Session, user: User) -> list[SubjectResponse]:
    """Obtiene todas las materias del usuario con sus métricas calculadas."""
    period = get_or_create_active_period(db, user.id)
    subjects = (
        db.query(Subject)
        .options(joinedload(Subject.evaluations).joinedload(Evaluation.grade))
        .filter(Subject.period_id == period.id, Subject.is_archived == False)
        .all()
    )

    settings = user.settings or AcademicSettings(max_grade=20.0, passing_grade=10.0)
    default_passing = settings.passing_grade or 10.0
    default_max = settings.max_grade or 20.0
    eval_mode = getattr(settings, "evaluation_mode", "university")
    default_evals = getattr(settings, "default_eval_count", 5)

    result = []
    for s in subjects:
        resp, _, _, _, _ = calculate_subject_metrics(
            s, default_passing, default_max, eval_mode, default_evals
        )
        result.append(resp)
    return result


def create_subject(db: Session, user: User, subject_in: SubjectCreate) -> SubjectResponse:
    period_id = subject_in.period_id
    if not period_id:
        period = get_or_create_active_period(db, user.id)
        period_id = period.id

    db_subject = Subject(
        id=str(uuid.uuid4()),
        period_id=period_id,
        name=subject_in.name,
        code=subject_in.code,
        color_hex=subject_in.color_hex or "#00E5FF",
        passing_grade_override=subject_in.passing_grade_override,
        max_grade_override=subject_in.max_grade_override,
        target_grade=subject_in.target_grade or 20.0,
        credits=subject_in.credits or 0,
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    default_passing = user.settings.passing_grade if user.settings else 10.0
    default_max = user.settings.max_grade if user.settings else 20.0
    resp, _, _, _, _ = calculate_subject_metrics(db_subject, default_passing, default_max)
    return resp


def update_subject(db: Session, user: User, subject_id: str, subject_in: SubjectUpdate) -> SubjectResponse:
    subject = (
        db.query(Subject)
        .join(AcademicPeriod)
        .filter(Subject.id == subject_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)

    db.add(subject)
    db.commit()
    db.refresh(subject)

    default_passing = user.settings.passing_grade if user.settings else 10.0
    default_max = user.settings.max_grade if user.settings else 20.0
    resp, _, _, _, _ = calculate_subject_metrics(subject, default_passing, default_max)
    return resp


def delete_subject(db: Session, user: User, subject_id: str):
    subject = (
        db.query(Subject)
        .join(AcademicPeriod)
        .filter(Subject.id == subject_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    db.delete(subject)
    db.commit()
    return {"status": "success", "message": "Materia eliminada exitosamente"}


def create_evaluation(db: Session, user: User, subject_id: str, eval_in: EvaluationCreate) -> EvaluationResponse:
    subject = (
        db.query(Subject)
        .join(AcademicPeriod)
        .filter(Subject.id == subject_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    status = "calificada" if eval_in.score is not None else "pendiente"

    db_eval = Evaluation(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        name=eval_in.name,
        description=eval_in.description,
        eval_type=eval_in.eval_type,
        weight_percent=eval_in.weight_percent,
        date=eval_in.date,
        status=status,
        max_grade=20.0,
    )
    db.add(db_eval)
    db.flush()

    grade_resp = None
    points_earned = None
    if eval_in.score is not None:
        db_grade = Grade(
            id=str(uuid.uuid4()),
            evaluation_id=db_eval.id,
            score=eval_in.score,
        )
        db.add(db_grade)
        db.flush()
        grade_resp = GradeResponse(
            id=db_grade.id,
            evaluation_id=db_grade.evaluation_id,
            score=db_grade.score,
        )
        points_earned = round(eval_in.score * (eval_in.weight_percent / 100.0), 2)

    db.commit()
    db.refresh(db_eval)

    return EvaluationResponse(
        id=db_eval.id,
        subject_id=db_eval.subject_id,
        name=db_eval.name,
        description=db_eval.description,
        eval_type=db_eval.eval_type,
        weight_percent=db_eval.weight_percent,
        date=db_eval.date,
        status=status,
        max_grade=db_eval.max_grade or 20.0,
        points_earned=points_earned,
        grade=grade_resp,
    )


def update_evaluation(db: Session, user: User, eval_id: str, eval_in: EvaluationUpdate) -> EvaluationResponse:
    evaluation = (
        db.query(Evaluation)
        .join(Subject)
        .join(AcademicPeriod)
        .filter(Evaluation.id == eval_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    if eval_in.name is not None:
        evaluation.name = eval_in.name
    if eval_in.description is not None:
        evaluation.description = eval_in.description
    if eval_in.eval_type is not None:
        evaluation.eval_type = eval_in.eval_type
    if eval_in.weight_percent is not None:
        evaluation.weight_percent = eval_in.weight_percent
    if eval_in.date is not None:
        evaluation.date = eval_in.date

    if eval_in.score is not None:
        evaluation.status = "calificada"
        if evaluation.grade:
            evaluation.grade.score = eval_in.score
        else:
            db_grade = Grade(
                id=str(uuid.uuid4()),
                evaluation_id=evaluation.id,
                score=eval_in.score,
            )
            db.add(db_grade)
            db.flush()

    db.commit()
    db.refresh(evaluation)

    grade_resp = None
    points_earned = None
    if evaluation.grade:
        grade_resp = GradeResponse(
            id=evaluation.grade.id,
            evaluation_id=evaluation.grade.evaluation_id,
            score=evaluation.grade.score,
            notes=evaluation.grade.notes,
        )
        points_earned = round(evaluation.grade.score * (evaluation.weight_percent / 100.0), 2)

    return EvaluationResponse(
        id=evaluation.id,
        subject_id=evaluation.subject_id,
        name=evaluation.name,
        description=evaluation.description,
        eval_type=evaluation.eval_type,
        weight_percent=evaluation.weight_percent,
        date=evaluation.date,
        status=evaluation.status or "pendiente",
        max_grade=evaluation.max_grade or 20.0,
        points_earned=points_earned,
        grade=grade_resp,
    )


def delete_evaluation(db: Session, user: User, eval_id: str):
    evaluation = (
        db.query(Evaluation)
        .join(Subject)
        .join(AcademicPeriod)
        .filter(Evaluation.id == eval_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    db.delete(evaluation)
    db.commit()
    return {"status": "success", "message": "Evaluación eliminada"}


# ─── SERVICIOS PARA HORARIO DE CLASES (ClassSchedule) ───
def get_user_class_schedules(db: Session, user: User) -> list[ClassScheduleResponse]:
    schedules = (
        db.query(ClassSchedule)
        .join(Subject)
        .join(AcademicPeriod)
        .filter(AcademicPeriod.user_id == user.id)
        .order_by(ClassSchedule.day_of_week, ClassSchedule.start_time)
        .all()
    )
    result = []
    for s in schedules:
        result.append(
            ClassScheduleResponse(
                id=s.id,
                subject_id=s.subject_id,
                subject_name=s.subject.name,
                color_hex=s.subject.color_hex or "#00E5FF",
                day_of_week=s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                classroom=s.classroom,
                professor=s.professor,
            )
        )
    return result


def create_class_schedule(db: Session, user: User, sched_in: ClassScheduleCreate) -> ClassScheduleResponse:
    subject = (
        db.query(Subject)
        .join(AcademicPeriod)
        .filter(Subject.id == sched_in.subject_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    sched = ClassSchedule(
        id=str(uuid.uuid4()),
        subject_id=sched_in.subject_id,
        day_of_week=sched_in.day_of_week,
        start_time=sched_in.start_time,
        end_time=sched_in.end_time,
        classroom=sched_in.classroom,
        professor=sched_in.professor,
    )
    db.add(sched)
    db.commit()
    db.refresh(sched)

    return ClassScheduleResponse(
        id=sched.id,
        subject_id=sched.subject_id,
        subject_name=subject.name,
        color_hex=subject.color_hex or "#00E5FF",
        day_of_week=sched.day_of_week,
        start_time=sched.start_time,
        end_time=sched.end_time,
        classroom=sched.classroom,
        professor=sched.professor,
    )


def update_class_schedule(db: Session, user: User, sched_id: str, sched_in: ClassScheduleUpdate) -> ClassScheduleResponse:
    sched = (
        db.query(ClassSchedule)
        .join(Subject)
        .join(AcademicPeriod)
        .filter(ClassSchedule.id == sched_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not sched:
        raise HTTPException(status_code=404, detail="Horario de clase no encontrado")

    update_data = sched_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sched, field, value)

    db.add(sched)
    db.commit()
    db.refresh(sched)

    return ClassScheduleResponse(
        id=sched.id,
        subject_id=sched.subject_id,
        subject_name=sched.subject.name,
        color_hex=sched.subject.color_hex or "#00E5FF",
        day_of_week=sched.day_of_week,
        start_time=sched.start_time,
        end_time=sched.end_time,
        classroom=sched.classroom,
        professor=sched.professor,
    )


def delete_class_schedule(db: Session, user: User, sched_id: str):
    sched = (
        db.query(ClassSchedule)
        .join(Subject)
        .join(AcademicPeriod)
        .filter(ClassSchedule.id == sched_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not sched:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    db.delete(sched)
    db.commit()
    return {"status": "success", "message": "Horario de clase eliminado"}


# ─── SERVICIOS PARA AGENDA Y RECORDATORIOS (AcademicEvent) ───
def get_user_academic_events(db: Session, user: User) -> list[AcademicEventResponse]:
    events = (
        db.query(AcademicEvent)
        .filter(AcademicEvent.user_id == user.id)
        .order_by(AcademicEvent.event_date.asc())
        .all()
    )
    result = []
    for ev in events:
        sub_name = ev.subject.name if ev.subject else None
        color_hex = ev.subject.color_hex if ev.subject else "#00E5FF"
        result.append(
            AcademicEventResponse(
                id=ev.id,
                user_id=ev.user_id,
                subject_id=ev.subject_id,
                subject_name=sub_name,
                color_hex=color_hex,
                evaluation_id=ev.evaluation_id,
                title=ev.title,
                description=ev.description,
                event_date=ev.event_date,
                reminder_lead_time_hours=ev.reminder_lead_time_hours,
                is_notified=ev.is_notified,
            )
        )
    return result


def create_academic_event(db: Session, user: User, event_in: AcademicEventCreate) -> AcademicEventResponse:
    ev = AcademicEvent(
        id=str(uuid.uuid4()),
        user_id=user.id,
        subject_id=event_in.subject_id,
        evaluation_id=event_in.evaluation_id,
        title=event_in.title,
        description=event_in.description,
        event_date=event_in.event_date,
        reminder_lead_time_hours=event_in.reminder_lead_time_hours,
        is_notified=False,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)

    sub_name = ev.subject.name if ev.subject else None
    color_hex = ev.subject.color_hex if ev.subject else "#00E5FF"

    return AcademicEventResponse(
        id=ev.id,
        user_id=ev.user_id,
        subject_id=ev.subject_id,
        subject_name=sub_name,
        color_hex=color_hex,
        evaluation_id=ev.evaluation_id,
        title=ev.title,
        description=ev.description,
        event_date=ev.event_date,
        reminder_lead_time_hours=ev.reminder_lead_time_hours,
        is_notified=ev.is_notified,
    )


def delete_academic_event(db: Session, user: User, event_id: str):
    ev = (
        db.query(AcademicEvent)
        .filter(AcademicEvent.id == event_id, AcademicEvent.user_id == user.id)
        .first()
    )
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    db.delete(ev)
    db.commit()
    return {"status": "success", "message": "Evento eliminado"}


# ─── SERVICIO DE ESTADÍSTICAS GLOBALES DEL DASHBOARD ───
def get_academic_stats(db: Session, user: User) -> AcademicStatsResponse:
    period = get_or_create_active_period(db, user.id)
    subjects = (
        db.query(Subject)
        .options(joinedload(Subject.evaluations).joinedload(Evaluation.grade))
        .filter(Subject.period_id == period.id, Subject.is_archived == False)
        .all()
    )

    settings = user.settings or AcademicSettings(max_grade=20.0, passing_grade=10.0)
    max_scale = settings.max_grade or 20.0
    passing_grade = settings.passing_grade or 10.0
    eval_mode = getattr(settings, "evaluation_mode", "university")
    default_evals = getattr(settings, "default_eval_count", 5)

    subject_responses = []
    grades_list = []
    passed_count = 0
    failed_count = 0
    total_evals = 0

    for s in subjects:
        resp, accum_pts, curr_avg, pass_score, is_pass = calculate_subject_metrics(
            s, passing_grade, max_scale, eval_mode, default_evals
        )
        subject_responses.append(resp)
        total_evals += len(s.evaluations)

        if curr_avg is not None:
            # Para el GPA consideramos el rendimiento de la materia
            grades_list.append(curr_avg)
            if is_pass or (resp.accumulated_percent >= 100.0 and accum_pts >= pass_score):
                passed_count += 1
            elif resp.accumulated_percent >= 100.0 and accum_pts < pass_score:
                failed_count += 1
            elif resp.max_possible_grade < pass_score:
                # Ya es matemáticamente imposible que apruebe
                failed_count += 1

    if grades_list:
        real_gpa = round(sum(grades_list) / len(grades_list), 2)
    else:
        real_gpa = None

    return AcademicStatsResponse(
        gpa=real_gpa,
        max_scale=max_scale,
        passing_grade=passing_grade,
        active_subjects_count=len(subjects),
        passed_count=passed_count,
        failed_count=failed_count,
        total_evaluations_count=total_evals,
        subjects=subject_responses,
    )


# ─── Calculadora Predictiva de Notas y Persistencia ───
def calculate_grade_prediction(
    db: Session, user: User, req: PredictionRequest
) -> PredictionResponse:
    """
    Motor de Cálculo Predictivo Inteligente:
    1. Cruza los datos de la materia con las evaluaciones ya calificadas.
    2. Calcula evaluaciones restantes y peso restante.
    3. Determina la nota exacta requerida por evaluación restante.
    4. Maneja rigurosamente todos los edge cases (meta alcanzada, imposible, completada).
    5. Persiste el cálculo en la tabla 'predicciones_notas'.
    """
    subject = (
        db.query(Subject)
        .options(joinedload(Subject.evaluations).joinedload(Evaluation.grade))
        .join(AcademicPeriod)
        .filter(Subject.id == req.subject_id, AcademicPeriod.user_id == user.id)
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada.")

    settings = db.query(AcademicSettings).filter(AcademicSettings.user_id == user.id).first()
    default_max = settings.max_grade if settings else 20.0
    default_min = settings.passing_grade if settings else 10.0
    default_total_evals = getattr(settings, "default_eval_count", 5) or 5

    max_scale = float(req.max_grade if req.max_grade is not None else (subject.max_grade_override or default_max))
    passing_grade = float(req.min_grade if req.min_grade is not None else (subject.passing_grade_override or default_min))
    tot_val = req.total_evaluations if req.total_evaluations is not None else req.total_evaluaciones
    total_evals = int(tot_val if tot_val is not None else default_total_evals)
    target_grade = float(req.target_grade)

    # Evaluaciones ya calificadas
    completed_evals = [ev for ev in subject.evaluations if ev.grade and ev.grade.score is not None]
    num_completed = len(completed_evals)

    accumulated_points = 0.0
    evaluated_weight = 0.0
    for ev in completed_evals:
        pts = round(ev.grade.score * (ev.weight_percent / 100.0), 2)
        accumulated_points += pts
        evaluated_weight += ev.weight_percent

    accumulated_points = round(accumulated_points, 2)
    evaluated_weight = round(evaluated_weight, 1)

    evaluaciones_restantes = max(0, total_evals - num_completed)
    remaining_weight = max(0.0, round(100.0 - evaluated_weight, 1))

    # Puntos máximos teóricos alcanzables
    max_possible_grade = min(max_scale, round(accumulated_points + max_scale * (remaining_weight / 100.0), 2))
    points_needed = round(max(0.0, target_grade - accumulated_points), 2)

    # Análisis de Casos de Negocio
    if evaluaciones_restantes == 0 or remaining_weight <= 0:
        # Caso: Sin evaluaciones restantes
        estado = "completada"
        es_posible = accumulated_points >= target_grade
        req_per_eval = None
        if accumulated_points >= target_grade:
            msg = (
                f"Esta materia ya tiene todas sus evaluaciones completadas con una nota definitiva de "
                f"{accumulated_points:.2f} pts. ¡Felicidades! Superaste tu meta de {target_grade:.2f} pts."
            )
        else:
            msg = (
                f"Esta materia ya completó el 100% de sus evaluaciones. Tu nota definitiva es "
                f"{accumulated_points:.2f} pts (meta de {target_grade:.2f} pts no alcanzada)."
            )

    elif accumulated_points >= target_grade:
        # Caso: Meta ya alcanzada
        estado = "meta_alcanzada"
        es_posible = True
        req_per_eval = 0.0
        msg = (
            f"¡Excelente noticia! Ya alcanzaste tu meta de {target_grade:.2f} pts. "
            f"Llevas {accumulated_points:.2f} pts acumulados ({evaluated_weight}% evaluado), "
            f"por lo que tienes la meta asegurada sin depender de las {evaluaciones_restantes} evaluaciones restantes."
        )

    elif target_grade > max_possible_grade:
        # Caso: Meta matemáticamente imposible
        estado = "imposible"
        es_posible = False
        raw_req = points_needed / (remaining_weight / 100.0) if remaining_weight > 0 else 999.0
        req_per_eval = round(raw_req, 2)
        msg = (
            f"Matemáticamente ya no puedes alcanzar {target_grade:.2f} pts, incluso sacando la nota máxima "
            f"({max_scale:.0f} pts) en las {evaluaciones_restantes} evaluaciones restantes. "
            f"Tu nota máxima posible ahora es {max_possible_grade:.2f} pts."
        )

    else:
        # Caso: Meta Posible
        estado = "posible"
        es_posible = True
        raw_req = points_needed / (remaining_weight / 100.0)
        req_per_eval = round(raw_req, 2)
        req_per_eval = max(0.0, min(max_scale, req_per_eval))
        msg = (
            f"Necesitas sacar un promedio de {req_per_eval:.2f} / {max_scale:.0f} pts en cada una de las "
            f"{evaluaciones_restantes} evaluaciones restantes ({remaining_weight}% por evaluar) "
            f"para alcanzar tu meta de {target_grade:.2f} pts."
        )

    # Persistencia en BD (Mantiene únicamente la última simulación de la materia sin acumular)
    existing_pred = (
        db.query(PrediccionNota)
        .filter(PrediccionNota.user_id == user.id, PrediccionNota.subject_id == subject.id)
        .first()
    )
    if existing_pred:
        existing_pred.nota_minima_usada = passing_grade
        existing_pred.nota_maxima_usada = max_scale
        existing_pred.total_evaluaciones_usadas = total_evals
        existing_pred.evaluaciones_realizadas_momento = num_completed
        existing_pred.evaluaciones_restantes = evaluaciones_restantes
        existing_pred.nota_deseada = target_grade
        existing_pred.nota_requerida_por_evaluacion = req_per_eval
        existing_pred.es_posible = es_posible
        existing_pred.mensaje_resultado = msg
        pred_record = existing_pred
    else:
        pred_record = PrediccionNota(
            id=str(uuid.uuid4()),
            user_id=user.id,
            subject_id=subject.id,
            nota_minima_usada=passing_grade,
            nota_maxima_usada=max_scale,
            total_evaluaciones_usadas=total_evals,
            evaluaciones_realizadas_momento=num_completed,
            evaluaciones_restantes=evaluaciones_restantes,
            nota_deseada=target_grade,
            nota_requerida_por_evaluacion=req_per_eval,
            es_posible=es_posible,
            mensaje_resultado=msg,
        )
        db.add(pred_record)
    db.commit()
    db.refresh(pred_record)

    return PredictionResponse(
        id=pred_record.id,
        subject_id=subject.id,
        subject_name=subject.name,
        color_hex=subject.color_hex or "#00E5FF",
        nota_minima_usada=passing_grade,
        nota_maxima_usada=max_scale,
        total_evaluaciones_usadas=total_evals,
        evaluaciones_realizadas_momento=num_completed,
        evaluaciones_restantes=evaluaciones_restantes,
        nota_deseada=target_grade,
        nota_requerida_por_evaluacion=req_per_eval,
        puntos_actuales_acumulados=accumulated_points,
        porcentaje_actual_evaluado=evaluated_weight,
        nota_maxima_posible=max_possible_grade,
        es_posible=es_posible,
        mensaje_resultado=msg,
        estado=estado,
        created_at=pred_record.created_at,
    )


def get_user_predictions(db: Session, user: User, limit: int = 10) -> list[PredictionResponse]:
    """Retorna el historial de predicciones/simulaciones del usuario."""
    records = (
        db.query(PrediccionNota)
        .options(joinedload(PrediccionNota.subject))
        .filter(PrediccionNota.user_id == user.id)
        .order_by(PrediccionNota.created_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for r in records:
        subj_name = r.subject.name if r.subject else "Materia"
        subj_color = r.subject.color_hex if r.subject else "#00E5FF"
        results.append(
            PredictionResponse(
                id=r.id,
                subject_id=r.subject_id,
                subject_name=subj_name,
                color_hex=subj_color,
                nota_minima_usada=r.nota_minima_usada,
                nota_maxima_usada=r.nota_maxima_usada,
                total_evaluaciones_usadas=r.total_evaluaciones_usadas,
                evaluaciones_realizadas_momento=r.evaluaciones_realizadas_momento,
                evaluaciones_restantes=r.evaluaciones_restantes,
                nota_deseada=r.nota_deseada,
                nota_requerida_por_evaluacion=r.nota_requerida_por_evaluacion,
                puntos_actuales_acumulados=0.0,
                porcentaje_actual_evaluado=0.0,
                nota_maxima_posible=r.nota_maxima_usada,
                es_posible=r.es_posible,
                mensaje_resultado=r.mensaje_resultado or "",
                estado="posible" if r.es_posible else "imposible",
                created_at=r.created_at,
            )
        )
    return results

