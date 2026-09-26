import flet as ft
from app.core.state import state
from app.core.api_client import api
from app.theme.colors import AcademixColors
from app.screens.subjects import SubjectsScreen
from app.screens.profile import ProfileScreen
from app.screens.schedule import ScheduleScreen


# ────────────────────────────────────────────────────────────────
# HELPER: Tarjeta de Stat Glassmorphism con indicador de neón
# ────────────────────────────────────────────────────────────────
def _stat_glass_card(title: str, value: str, icon, accent: str, progress: float = 0.0, is_gradient_bar: bool = False, subtitle: str = None):
    # Clamp de progreso entre 0.0 y 1.0
    safe_prog = max(0.0, min(1.0, progress))
    fill_flex = max(1, int(safe_prog * 100)) if safe_prog > 0 else 0
    empty_flex = max(1, 100 - fill_flex)

    if fill_flex > 0:
        if is_gradient_bar:
            bar_fill = ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.CENTER_LEFT,
                    end=ft.Alignment.CENTER_RIGHT,
                    colors=[AcademixColors.PRIMARY_PURPLE, AcademixColors.CYAN_NEON],
                ),
                border_radius=4,
                height=4,
                expand=fill_flex,
            )
        else:
            bar_fill = ft.Container(
                bgcolor=accent,
                border_radius=4,
                height=4,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.5, accent)),
                expand=fill_flex,
            )
        bar_controls = [bar_fill]
        if empty_flex > 0:
            bar_controls.append(
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    border_radius=4,
                    height=4,
                    expand=empty_flex,
                )
            )
    else:
        bar_controls = [
            ft.Container(
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                border_radius=4,
                height=4,
                expand=100,
            )
        ]

    card_content = [
        ft.Row(
            [
                ft.Icon(icon=icon, color=accent, size=20),
                ft.Text(title, size=12, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
            ],
            spacing=8,
        ),
        ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
    ]

    if subtitle:
        card_content.append(ft.Text(subtitle, size=11, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)))

    card_content.append(ft.Row(bar_controls, spacing=0))

    return ft.Container(
        content=ft.Column(card_content, spacing=8),
        padding=18,
        border_radius=18,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.25, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
            offset=ft.Offset(0, 8),
        ),
    )


# ────────────────────────────────────────────────────────────────
# VISTA: Inicio / Resumen con DATOS REALES DE LA BASE DE DATOS
# ────────────────────────────────────────────────────────────────
def _section_home(page: ft.Page, user_name: str):
    # Consultar estadísticas reales a la API
    stats_data = None
    try:
        resp = api.get_stats()
        if resp.status_code == 200:
            stats_data = resp.json()
    except Exception:
        stats_data = None

    # Lógica de Negocio Real:
    if stats_data:
        gpa = stats_data.get("gpa")
        max_scale = stats_data.get("max_scale", 20.0)
        active_count = stats_data.get("active_subjects_count", 0)
        passed_count = stats_data.get("passed_count", 0)
        failed_count = stats_data.get("failed_count", 0)

        if gpa is not None:
            gpa_text = f"{gpa:.2f}/{int(max_scale)}"
            gpa_prog = min(1.0, gpa / max_scale) if max_scale > 0 else 0.0
            gpa_sub = "Promedio ponderado acumulado"
        else:
            gpa_text = f"--/{int(max_scale)}"
            gpa_prog = 0.0
            gpa_sub = "Sin notas registradas aún"

        active_text = str(active_count)
        active_prog = min(1.0, active_count / 8.0)  # Asume máx típico de 8 materias
        active_sub = "Materias inscritas"

        passed_text = str(passed_count)
        passed_prog = (passed_count / active_count) if active_count > 0 else 0.0
        passed_sub = f">= {stats_data.get('passing_grade', 10.0):.0f} puntos"

        failed_text = str(failed_count)
        failed_prog = (failed_count / active_count) if active_count > 0 else 0.0
        failed_sub = f"< {stats_data.get('passing_grade', 10.0):.0f} puntos"
    else:
        # Estado inicial limpio si no hay conexión o no hay datos
        gpa_text = "--/20"
        gpa_prog = 0.0
        gpa_sub = "Sin notas registradas aún"
        active_text = "0"
        active_prog = 0.0
        active_sub = "Sin materias agregadas"
        passed_text = "0"
        passed_prog = 0.0
        passed_sub = "0 materias"
        failed_text = "0"
        failed_prog = 0.0
        failed_sub = "0 materias"
        active_count = 0

    # 2x2 Grid de estadísticas reales
    row_top = ft.Row(
        [
            _stat_glass_card(
                "Promedio General",
                gpa_text,
                ft.Icons.SHOW_CHART,
                AcademixColors.CYAN_NEON,
                progress=gpa_prog,
                is_gradient_bar=True,
                subtitle=gpa_sub,
            ),
            _stat_glass_card(
                "Materias Activas",
                active_text,
                ft.Icons.CALENDAR_MONTH_OUTLINED,
                AcademixColors.CYAN_NEON,
                progress=active_prog,
                subtitle=active_sub,
            ),
        ],
        spacing=16,
    )

    row_bottom = ft.Row(
        [
            _stat_glass_card(
                "Aprobadas",
                passed_text,
                ft.Icons.CHECK_CIRCLE,
                AcademixColors.SUCCESS,
                progress=passed_prog,
                subtitle=passed_sub,
            ),
            _stat_glass_card(
                "Reprobadas",
                failed_text,
                ft.Icons.CANCEL,
                AcademixColors.ERROR,
                progress=failed_prog,
                subtitle=failed_sub,
            ),
        ],
        spacing=16,
    )

    # Tarjeta de Bienvenida / Llamado a la Acción si no tiene materias agregadas
    empty_notice = None
    if active_count == 0:
        empty_notice = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon=ft.Icons.INFO_OUTLINE, color=AcademixColors.CYAN_NEON, size=24),
                    ft.Column(
                        [
                            ft.Text("Aún no has agregado materias a tu periodo actual", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Dirígete a 'Notas' o 'Horario' para registrar tus asignaturas y ver tus cálculos automáticos.", size=11, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.FilledButton(
                        "Agregar Materia",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: page.navigate("/notas"),
                        style=ft.ButtonStyle(
                            bgcolor=AcademixColors.CYAN_NEON,
                            color=ft.Colors.BLACK,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=16,
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.25, AcademixColors.CYAN_NEON)),
        )

    # Tarjeta: Consejo del día académico (real y coherente)
    advice_card = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(
                        icon=ft.Icons.LIGHTBULB_OUTLINE,
                        color=AcademixColors.CYAN_NEON,
                        size=32,
                    ),
                    shadow=ft.BoxShadow(
                        blur_radius=16,
                        color=ft.Colors.with_opacity(0.6, AcademixColors.CYAN_NEON),
                    ),
                    padding=ft.Padding(4, 4, 8, 4),
                ),
                ft.Column(
                    [
                        ft.Text("Consejo Académico del Día", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(
                            "Distribuye las ponderaciones de cada corte y anticipa las notas mínimas que necesitas para aprobar con nuestra calculadora.",
                            size=12,
                            color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                        ),
                    ],
                    spacing=3,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=18,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
            offset=ft.Offset(0, 8),
        ),
    )

    # Acceso Rápido a la Calculadora Predictiva
    quick_calc_card = ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon=ft.Icons.CALCULATE_OUTLINED, color=AcademixColors.YELLOW_NEON, size=24),
                ft.Column(
                    [
                        ft.Text("Calculadora Predictiva", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Simula cuánto necesitas sacar en tus próximos exámenes para aprobar", size=11, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE)),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.OutlinedButton(
                    "Calcular",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=lambda _: page.navigate("/calculator"),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.2, AcademixColors.CYAN_NEON),
                        color=AcademixColors.CYAN_NEON,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, AcademixColors.CYAN_NEON)),
    )

    content_children = [
        # Saludo con nombre real
        ft.Row(
            [
                ft.Text("¡Hola, ", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(
                    f"{user_name}!",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=AcademixColors.CYAN_NEON,
                    style=ft.TextStyle(
                        shadow=ft.BoxShadow(
                            blur_radius=16,
                            color=ft.Colors.with_opacity(0.6, AcademixColors.CYAN_NEON),
                        )
                    ),
                ),
                ft.Text(" 👋", size=28),
            ],
            spacing=0,
        ),
        ft.Text(
            "Académix - Asistente y gestor de notas estudiantil",
            size=13,
            color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
        ),
        ft.Container(height=12),
    ]

    if empty_notice:
        content_children.append(empty_notice)
        content_children.append(ft.Container(height=12))

    content_children.extend([
        row_top,
        ft.Container(height=8),
        row_bottom,
        ft.Container(height=12),
        advice_card,
        ft.Container(height=10),
        quick_calc_card,
    ])

    return ft.Column(
        content_children,
        spacing=0,
        expand=True,
    )


# ────────────────────────────────────────────────────────────────
# VISTA: Calculadora Predictiva
# ────────────────────────────────────────────────────────────────
def _section_calculator(page: ft.Page):
    # ─── 1. Obtener Configuración Global y Materias del Usuario ───
    user_settings = (state.current_user or {}).get("settings", {})
    global_max = float(user_settings.get("max_grade", 20.0))
    global_pass = float(user_settings.get("passing_grade", 10.0))
    global_total_evals = int(user_settings.get("default_eval_count", 5))

    subjects = []
    try:
        resp = api.get_subjects()
        if resp.status_code == 200:
            subjects = resp.json()
    except Exception:
        subjects = []

    # ─── Validación Obligatoria: Estado Vacío ───
    if not subjects:
        return ft.Column(
            [
                ft.Text("Calculadora Predictiva 🧮", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Simula con exactitud matemática las notas que necesitas para superar tus materias.", size=13, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE)),
                ft.Container(height=24),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=56, color=AcademixColors.CYAN_NEON),
                                padding=18,
                                border_radius=50,
                                bgcolor=ft.Colors.with_opacity(0.12, AcademixColors.CYAN_NEON),
                                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.35, AcademixColors.CYAN_NEON)),
                            ),
                            ft.Text("No tienes materias cargadas aún", size=19, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(
                                "Agrega una materia primero para poder simular tus notas y proyectar tu rendimiento académico.",
                                size=13,
                                color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=10),
                            ft.FilledButton(
                                "Agregar Mi Primera Materia",
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                on_click=lambda _: page.navigate("/notas"),
                                style=ft.ButtonStyle(
                                    bgcolor=AcademixColors.CYAN_NEON,
                                    color=ft.Colors.BLACK,
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    padding=ft.Padding(20, 12, 20, 12),
                                ),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                    ),
                    padding=48,
                    border_radius=24,
                    bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.WHITE)),
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            spacing=0,
        )

    # ─── Helper de Estilo para Inputs ───
    def _calc_field(label: str, value: str = "", hint_text: str = "", keyboard_type=ft.KeyboardType.NUMBER):
        return ft.TextField(
            label=label,
            value=value,
            hint_text=hint_text,
            keyboard_type=keyboard_type,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.14, "#0D1B2A"),
            color=ft.Colors.WHITE,
            label_style=ft.TextStyle(color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE), size=12),
            border=ft.OutlineInputBorder(
                border_radius=12,
                side=ft.BorderSide(color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE), width=1.2),
            ),
            focused_border_color=AcademixColors.CYAN_NEON,
            focused_border_width=1.8,
            dense=True,
        )

    # Estado y Selección
    selected_subject_id = subjects[0]["id"]

    def find_subject(s_id: str):
        for s in subjects:
            if s["id"] == s_id:
                return s
        return subjects[0]

    initial_s = find_subject(selected_subject_id)
    init_max = float(initial_s.get("max_grade_override") or global_max)
    init_pass = float(initial_s.get("passing_grade_override") or global_pass)
    init_target = float(initial_s.get("target_grade") or init_pass)

    # Controles de Entrada (Personalización en Caliente)
    pass_grade_field = _calc_field("Nota Mínima Aprobatoria", value=str(round(init_pass, 1)), hint_text=f"Ej: {init_pass:.0f}")
    max_scale_field = _calc_field("Nota Máxima de Escala", value=str(round(init_max, 1)), hint_text=f"Ej: {init_max:.0f}")
    total_evals_field = _calc_field("Total Evaluaciones Periodo", value=str(global_total_evals), hint_text="Ej: 5")
    desired_grade_field = _calc_field("Nota Meta que Deseas", value=str(round(init_target, 1)), hint_text=f"Ej: {init_target:.0f}")

    # Resumen Dinámico de Evaluaciones Realizadas
    eval_stats_container = ft.Container()

    def update_eval_stats(s):
        completed_evals = [e for e in s.get("evaluations", []) if e.get("grade") and e["grade"].get("score") is not None]
        n_completed = len(completed_evals)
        try:
            total_e = int(total_evals_field.value or global_total_evals)
        except ValueError:
            total_e = global_total_evals
        n_remaining = max(0, total_e - n_completed)
        accum_pts = float(s.get("accumulated_points", 0.0))
        eval_pct = float(s.get("accumulated_percent", 0.0))

        eval_stats_container.content = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=AcademixColors.SUCCESS, size=16),
                                ft.Text(f"Realizadas: {n_completed}/{total_e}", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                            ],
                            spacing=6,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
                        padding=ft.Padding(10, 6, 10, 6),
                        border_radius=8,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.HOURGLASS_EMPTY, color=AcademixColors.WARNING, size=16),
                                ft.Text(f"Restantes: {n_remaining}", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                            ],
                            spacing=6,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
                        padding=ft.Padding(10, 6, 10, 6),
                        border_radius=8,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.STAR, color=AcademixColors.CYAN_NEON, size=16),
                                ft.Text(f"Acumulado: {accum_pts:.2f} pts ({eval_pct:.0f}%)", size=12, weight=ft.FontWeight.W_600, color=AcademixColors.CYAN_NEON),
                            ],
                            spacing=6,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
                        padding=ft.Padding(10, 6, 10, 6),
                        border_radius=8,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                    ),
                ],
                wrap=True,
                spacing=8,
            ),
            padding=ft.Padding(0, 4, 0, 8),
        )

    update_eval_stats(initial_s)

    # Selector de Materia
    def on_subject_changed(e):
        nonlocal selected_subject_id
        selected_subject_id = e.control.value or subject_dd.value
        s = find_subject(selected_subject_id)
        s_max = float(s.get("max_grade_override") or global_max)
        s_pass = float(s.get("passing_grade_override") or global_pass)
        s_target = float(s.get("target_grade") or s_pass)

        pass_grade_field.value = str(round(s_pass, 1))
        max_scale_field.value = str(round(s_max, 1))
        desired_grade_field.value = str(round(s_target, 1))
        update_eval_stats(s)
        result_card.visible = False
        page.update()

    subject_options = [
        ft.dropdown.Option(
            s["id"],
            f"{s['name']}" + (f" ({s.get('code')})" if s.get('code') else "")
        )
        for s in subjects
    ]

    subject_dd = ft.Dropdown(
        label="Materia a Evaluar",
        value=selected_subject_id,
        options=subject_options,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=AcademixColors.CYAN_NEON, size=13, weight=ft.FontWeight.BOLD),
        border=ft.OutlineInputBorder(
            border_radius=14,
            side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.5),
        ),
        on_select=on_subject_changed,
    )

    # Botón Rápido: "Solo quiero aprobar"
    def set_only_pass(e):
        try:
            val = float(pass_grade_field.value or global_pass)
            desired_grade_field.value = str(round(val, 1))
        except ValueError:
            desired_grade_field.value = str(round(global_pass, 1))
        page.update()

    quick_pass_btn = ft.OutlinedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=15, color=AcademixColors.CYAN_NEON),
                ft.Text("Solo quiero aprobar", size=12, color=AcademixColors.CYAN_NEON, weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            side=ft.BorderSide(1.2, AcademixColors.CYAN_NEON),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.Colors.with_opacity(0.1, AcademixColors.CYAN_NEON),
            padding=ft.Padding(12, 8, 12, 8),
        ),
        on_click=set_only_pass,
    )

    # Tarjeta de Resultado Predictivo
    result_card = ft.Container(visible=False)

    # Cálculo y Persistencia
    calc_button_text = ft.Text("Calcular Proyección Predictiva", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    calc_button_icon = ft.Icon(ft.Icons.CALCULATE_ROUNDED, color=ft.Colors.WHITE, size=18)

    def calculate(e):
        try:
            target = float(desired_grade_field.value or init_pass)
            min_g = float(pass_grade_field.value or init_pass)
            max_g = float(max_scale_field.value or init_max)
            tot_e = int(total_evals_field.value or global_total_evals)
        except ValueError:
            result_card.content = ft.Text("Por favor ingresa valores numéricos válidos en todos los campos.", color=AcademixColors.ERROR)
            result_card.visible = True
            page.update()
            return

        if target < 0 or target > max_g:
            result_card.content = ft.Text(f"La nota deseada debe estar entre 0 y la nota máxima ({max_g:.0f}).", color=AcademixColors.ERROR)
            result_card.visible = True
            page.update()
            return

        # Indicar estado de carga
        calc_button_text.value = "Calculando y Persistiendo..."
        calc_button_icon.name = ft.Icons.HOURGLASS_TOP
        page.update()

        payload = {
            "subject_id": selected_subject_id,
            "target_grade": target,
            "total_evaluaciones": tot_e,
            "min_grade": min_g,
            "max_grade": max_g,
        }

        try:
            resp = api.simulate_grade(payload)
            if resp.status_code == 200:
                data = resp.json()
                estado = data.get("estado", "posible")
                es_posible = data.get("es_posible", True)
                req_val = data.get("nota_requerida_por_evaluacion")
                max_pos = data.get("nota_maxima_posible", max_g)
                msg = data.get("mensaje_resultado", "")
                restantes = data.get("evaluaciones_restantes", 0)

                # Tarjetas según Caso de Negocio
                if estado == "meta_alcanzada":
                    card_border = AcademixColors.SUCCESS
                    title_text = "¡Meta Alcanzada / Aprobada! 🎉"
                    score_main = "0.0 pts requeridos"
                    badge_info = "Ya tienes los puntos necesarios asegurados."
                    card_icon = ft.Icons.VERIFIED_ROUNDED
                elif estado == "completada":
                    card_border = AcademixColors.CYAN_NEON
                    title_text = "Materia Completada al 100%"
                    score_main = f"{data.get('puntos_actuales_acumulados', 0.0):.2f} pts"
                    badge_info = "Nota Definitiva Final"
                    card_icon = ft.Icons.TASK_ALT_ROUNDED
                elif not es_posible or estado == "imposible":
                    card_border = AcademixColors.ERROR
                    title_text = "Meta fuera de rango matemático ⚠️"
                    score_main = f"{req_val:.2f} pts" if req_val else "Excede límite"
                    badge_info = f"Nota máxima alcanzable ahora: {max_pos:.2f} / {max_g:.0f}"
                    card_icon = ft.Icons.REPORT_PROBLEM_ROUNDED
                else:
                    card_border = AcademixColors.CYAN_NEON
                    title_text = "Nota requerida por evaluación restante:"
                    score_main = f"{req_val:.2f} / {max_g:.0f}" if req_val is not None else "0.0"
                    badge_info = f"En cada una de las {restantes} evaluaciones que te faltan"
                    card_icon = ft.Icons.AUTO_GRAPH_ROUNDED

                result_card.content = ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(card_icon, color=card_border, size=24),
                                ft.Text(title_text, size=15, weight=ft.FontWeight.BOLD, color=card_border),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(score_main, size=32, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                        ft.Container(
                            content=ft.Text(badge_info, size=12, weight=ft.FontWeight.W_600, color=card_border),
                            padding=ft.Padding(10, 4, 10, 4),
                            border_radius=8,
                            bgcolor=ft.Colors.with_opacity(0.15, card_border),
                            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, card_border)),
                        ),
                        ft.Container(height=4),
                        ft.Text(msg, size=13, color=ft.Colors.with_opacity(0.88, ft.Colors.WHITE), weight=ft.FontWeight.W_400),
                    ],
                    spacing=8,
                )
                result_card.bgcolor = ft.Colors.with_opacity(0.25, "#0D1B2A")
                result_card.border = ft.Border.all(1.5, card_border)
                result_card.padding = 22
                result_card.border_radius = 18
                result_card.shadow = ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.35, card_border))
                result_card.visible = True
            else:
                err_msg = resp.json().get("detail", "Error al procesar la simulación.")
                result_card.content = ft.Text(f"Error: {err_msg}", color=AcademixColors.ERROR)
                result_card.visible = True
        except Exception as ex:
            result_card.content = ft.Text(f"Error de conexión: {ex}", color=AcademixColors.ERROR)
            result_card.visible = True
        finally:
            calc_button_text.value = "Calcular Proyección Predictiva"
            calc_button_icon.name = ft.Icons.CALCULATE_ROUNDED
            page.update()

    calc_btn = ft.Container(
        content=ft.Row(
            [calc_button_icon, calc_button_text],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[AcademixColors.PRIMARY_PURPLE, AcademixColors.PRIMARY],
        ),
        border_radius=14,
        height=50,
        alignment=ft.Alignment.CENTER,
        on_click=calculate,
        shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.4, AcademixColors.PRIMARY_PURPLE)),
    )

    return ft.Column(
        [
            ft.Text("Calculadora Predictiva 🧮", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(
                "Calcula con exactitud matemática cuánto necesitas sacar en tus evaluaciones restantes para alcanzar tu meta.",
                size=13,
                color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE),
            ),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    [
                        # 1. Selector de Materia
                        ft.Text("1. Selecciona la Materia a Evaluar", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        subject_dd,
                        eval_stats_container,
                        ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=14),

                        # 2. Configuración en Caliente
                        ft.Text("2. Parámetros de Escala y Evaluaciones (Confirmar o Modificar)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Row(
                            [
                                ft.Container(pass_grade_field, expand=1),
                                ft.Container(max_scale_field, expand=1),
                                ft.Container(total_evals_field, expand=1),
                            ],
                            spacing=10,
                        ),
                        ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=14),

                        # 3. Definición de la Meta
                        ft.Text("3. Define tu Meta", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Row(
                            [
                                ft.Container(desired_grade_field, expand=2),
                                ft.Container(quick_pass_btn, expand=1),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=8),

                        # 4. Botón de Acción
                        calc_btn,

                        # 5. Tarjeta de Resultado
                        ft.Container(height=6),
                        result_card,
                    ],
                    spacing=12,
                ),
                padding=24,
                border_radius=22,
                bgcolor=ft.Colors.with_opacity(0.24, "#0D1B2A"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            ),
        ],
        spacing=0,
    )



# ────────────────────────────────────────────────────────────────
# PANTALLA PRINCIPAL: Dashboard Shell (Estética Refinada)
# ────────────────────────────────────────────────────────────────
def DashboardScreen(page: ft.Page, active_route: str = "dashboard"):
    # Normalizar ruta activa
    clean_route = active_route.strip("/") if active_route else "dashboard"
    if clean_route == "":
        clean_route = "dashboard"

    # Obtener nombre real y avatar real del usuario
    user_name = "Diego"
    avatar_url = None
    if state.current_user:
        p = state.current_user.get("profile", {})
        if p.get("first_name"):
            user_name = p.get("first_name")
        avatar_url = p.get("avatar_url")

    # Definir cada elemento de navegación con su RUTA ÚNICA e independiente
    nav_items = [
        ("Inicio", ft.Icons.HOME_ROUNDED, "dashboard"),
        ("Horario", ft.Icons.ACCESS_TIME_ROUNDED, "horario"),
        ("Notas", ft.Icons.ARTICLE_OUTLINED, "notas"),
        ("Calculadora", ft.Icons.CALCULATE_OUTLINED, "calculator"),
        ("Perfil", ft.Icons.PERSON_OUTLINE, "profile"),
        ("Configuración", ft.Icons.SETTINGS_OUTLINED, "settings"),
    ]

    # Construir botones de navegación asegurando selección MUTUAMENTE EXCLUSIVA
    nav_controls = []
    for label, icon, route_target in nav_items:
        # Solo se marca si la ruta actual es exactamente esta ruta
        is_selected = (clean_route == route_target)

        if is_selected:
            btn = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon=icon, color=AcademixColors.CYAN_NEON, size=18),
                        ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=AcademixColors.CYAN_NEON),
                    ],
                    spacing=12,
                ),
                padding=ft.Padding(14, 10, 14, 10),
                border_radius=12,
                bgcolor=ft.Colors.with_opacity(0.22, AcademixColors.CYAN_NEON),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.35, AcademixColors.CYAN_NEON)),
                on_click=lambda _, r=route_target: page.navigate(f"/{r}"),
            )
        else:
            btn = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon=icon, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE), size=18),
                        ft.Text(label, size=13, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ],
                    spacing=12,
                ),
                padding=ft.Padding(14, 10, 14, 10),
                border_radius=12,
                on_click=lambda _, r=route_target: page.navigate(f"/{r}"),
            )
        nav_controls.append(btn)

    # ─── Logo / Birrete Superior Refinado y Proporcional ──────────
    # Más compacto, estético y sin el bloque gigante que rompía la jerarquía
    sidebar_brand = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon=ft.Icons.SCHOOL_ROUNDED, color=AcademixColors.CYAN_NEON, size=22),
                    width=38,
                    height=38,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
                    border=ft.Border.all(1.2, AcademixColors.CYAN_NEON),
                    alignment=ft.Alignment.CENTER,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.4, AcademixColors.CYAN_NEON)),
                ),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("ACADÉMIX", size=13, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                                ft.Container(
                                    content=ft.Text("PRO", size=9, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
                                    padding=ft.Padding(4, 1, 4, 1),
                                    border_radius=4,
                                    bgcolor=ft.Colors.with_opacity(0.2, AcademixColors.CYAN_NEON),
                                ),
                            ],
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text("Smart Study", size=10, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                    ],
                    spacing=1,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(12, 16, 12, 18),
        alignment=ft.Alignment.CENTER_LEFT,
    )

    # ─── Tarjeta Inferior de Usuario con AVATAR REAL O INICIALES ──
    # Si el usuario NO ha subido foto, muestra sus iniciales reales, NUNCA una foto de stock falsa
    if avatar_url and avatar_url.strip():
        avatar_content = ft.CircleAvatar(
            foreground_image_src=avatar_url.strip(),
            radius=22,
            bgcolor=AcademixColors.PRIMARY,
        )
    else:
        user_initial = user_name[:1].upper() if user_name else "D"
        avatar_content = ft.CircleAvatar(
            content=ft.Text(user_initial, size=18, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
            radius=22,
            bgcolor=ft.Colors.with_opacity(0.3, "#0D1B2A"),
        )

    user_profile_card = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=avatar_content,
                    border=ft.Border.all(2, AcademixColors.CYAN_NEON),
                    shape=ft.BoxShape.CIRCLE,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.4, AcademixColors.CYAN_NEON)),
                ),
                ft.Text(user_name, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.GestureDetector(
                    content=ft.Text("Cerrar Sesión", size=11, color=AcademixColors.CYAN_NEON),
                    on_tap=lambda _: [state.logout(), page.navigate("/login")],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        width=154,
        padding=ft.Padding(10, 12, 10, 12),
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.28, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK)),
    )

    # ─── Panel Izquierdo Completo (Sidebar) ────────────────────
    sidebar = ft.Container(
        content=ft.Column(
            [
                sidebar_brand,
                ft.Column(nav_controls, spacing=6),
                ft.Container(expand=True),
                user_profile_card,
                ft.Container(height=6),
            ],
            spacing=0,
            expand=True,
        ),
        width=196,
        padding=ft.Padding(10, 0, 10, 10),
    )

    # ─── Selector de Vista Interna ─────────────────────────────
    if clean_route == "dashboard":
        content_view = _section_home(page, user_name)
    elif clean_route == "calculator":
        content_view = _section_calculator(page)
    elif clean_route == "horario":
        content_view = ScheduleScreen(page)
    elif clean_route in ["notas", "subjects"]:
        content_view = SubjectsScreen(page, view_mode="notas")
    elif clean_route == "profile":
        content_view = ProfileScreen(page, focus_settings=False)
    elif clean_route == "settings":
        content_view = ProfileScreen(page, focus_settings=True)
    else:
        content_view = _section_home(page, user_name)

    # ─── Detección de Plataforma y Tamaño Responsive ───────────
    # Móvil Primero: Si width es menor a 768px (o None en el primer frame móvil)
    is_mobile = page.width is None or page.width < 768

    # ─── DISPOSICIÓN 1: MÓVIL (Celulares y Tablets en vertical) ─
    if is_mobile:
        # 1. Barra Superior Móvil (Top App Bar)
        mobile_top_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon=ft.Icons.SCHOOL_ROUNDED, color=AcademixColors.CYAN_NEON, size=20),
                                width=32,
                                height=32,
                                border_radius=8,
                                bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
                                border=ft.Border.all(1.2, AcademixColors.CYAN_NEON),
                                alignment=ft.Alignment.CENTER,
                                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.4, AcademixColors.CYAN_NEON)),
                            ),
                            ft.Row(
                                [
                                    ft.Text("ACADÉMIX", size=13, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                                    ft.Container(
                                        content=ft.Text("PRO", size=8, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
                                        padding=ft.Padding(3, 1, 3, 1),
                                        border_radius=4,
                                        bgcolor=ft.Colors.with_opacity(0.2, AcademixColors.CYAN_NEON),
                                    ),
                                ],
                                spacing=3,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.GestureDetector(
                                content=avatar_content,
                                on_tap=lambda _: page.navigate("/profile"),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT_ROUNDED,
                                icon_color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                icon_size=18,
                                tooltip="Cerrar Sesión",
                                on_click=lambda _: [state.logout(), page.navigate("/login")],
                            ),
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(14, 10, 14, 10),
            bgcolor=ft.Colors.with_opacity(0.45, "#0D1B2A"),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE))),
        )

        # 2. Barra Inferior de Navegación Móvil (Bottom Navigation Bar)
        mobile_nav_items = [
            ("Inicio", ft.Icons.HOME_ROUNDED, "dashboard"),
            ("Horario", ft.Icons.ACCESS_TIME_ROUNDED, "horario"),
            ("Notas", ft.Icons.ARTICLE_OUTLINED, "notas"),
            ("Calculadora", ft.Icons.CALCULATE_OUTLINED, "calculator"),
            ("Perfil", ft.Icons.PERSON_OUTLINE, "profile"),
        ]

        def _make_mobile_nav_btn(lbl, ic, r_target):
            active = (clean_route == r_target or (r_target == "notas" and clean_route == "subjects"))
            return ft.GestureDetector(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                icon=ic,
                                color=AcademixColors.CYAN_NEON if active else ft.Colors.with_opacity(0.55, ft.Colors.WHITE),
                                size=20,
                            ),
                            ft.Text(
                                lbl,
                                size=10,
                                weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL,
                                color=AcademixColors.CYAN_NEON if active else ft.Colors.with_opacity(0.55, ft.Colors.WHITE),
                            ),
                            # Indicador de luz neón activo
                            ft.Container(
                                width=12,
                                height=2,
                                border_radius=1,
                                bgcolor=AcademixColors.CYAN_NEON if active else ft.Colors.TRANSPARENT,
                                shadow=ft.BoxShadow(blur_radius=6, color=AcademixColors.CYAN_NEON) if active else None,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    padding=ft.Padding(4, 4, 4, 4),
                ),
                on_tap=lambda _, rt=r_target: page.navigate(f"/{rt}"),
            )

        mobile_bottom_bar = ft.Container(
            content=ft.Row(
                [_make_mobile_nav_btn(lbl, ic, r) for lbl, ic, r in mobile_nav_items],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(4, 6, 4, 6),
            bgcolor=ft.Colors.with_opacity(0.75, "#0A1322"),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE))),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
                offset=ft.Offset(0, -4),
            ),
        )

        # 3. Contenedor de Contenido Principal a Ancho Completo
        mobile_main_container = ft.Container(
            content=ft.Column(
                [content_view],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=ft.Padding(12, 12, 12, 12),
            expand=True,
        )

        return ft.Stack(
            [
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[AcademixColors.BG_START, AcademixColors.BG_END],
                    ),
                ),
                ft.Column(
                    [
                        mobile_top_bar,
                        mobile_main_container,
                        mobile_bottom_bar,
                    ],
                    spacing=0,
                    expand=True,
                ),
            ],
            expand=True,
        )

    # ─── DISPOSICIÓN 2: TABLETS HORIZONTALES Y PANTALLAS ANCHAS ─
    main_glass_panel = ft.Container(
        content=ft.Column(
            [content_view],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        padding=24,
        border_radius=24,
        bgcolor=ft.Colors.with_opacity(0.28, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            blur_radius=40,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            offset=ft.Offset(0, 16),
        ),
    )

    return ft.Stack(
        [
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=[AcademixColors.BG_START, AcademixColors.BG_END],
                ),
            ),
            ft.Container(
                content=ft.Row(
                    [
                        sidebar,
                        main_glass_panel,
                    ],
                    spacing=16,
                    expand=True,
                ),
                padding=16,
                expand=True,
            ),
        ],
        expand=True,
    )
