import flet as ft
from datetime import datetime, timedelta
from app.core.api_client import api
from app.core.state import state
from app.theme.colors import AcademixColors

DAYS_OF_WEEK = [
    (0, "Lunes", "LUN"),
    (1, "Martes", "MAR"),
    (2, "Miércoles", "MIÉ"),
    (3, "Jueves", "JUE"),
    (4, "Viernes", "VIE"),
    (5, "Sábado", "SÁB"),
    (6, "Domingo", "DOM"),
]

def ScheduleScreen(page: ft.Page):
    """
    Módulo de Horario y Agenda Académica Inteligente:
    - Cronograma Semanal de Clases conectado a MySQL.
    - Agenda de Evaluaciones y Alertas de Recordatorio.
    - Soporte interactivo y Mobile-First con vista de Día y Semana.
    """
    view_mode = ["week"] # "week" o "day"
    selected_day = [datetime.today().weekday()] # 0=Lunes

    classes_cache = []
    events_cache = []
    subjects_cache = []

    content_container = ft.Column(spacing=16)
    loading_bar = ft.ProgressBar(visible=False, color=AcademixColors.CYAN_NEON)

    def show_snack(message: str, error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_900 if error else ft.Colors.BLUE_GREY_900,
        )
        page.show_dialog(snack)

    def load_data():
        loading_bar.visible = True
        page.update()
        try:
            # 1. Cargar materias para los selects
            r_sub = api.get_subjects()
            if r_sub.status_code == 200:
                subjects_cache.clear()
                subjects_cache.extend(r_sub.json())

            # 2. Cargar clases del horario
            r_cls = api.get_classes()
            if r_cls.status_code == 200:
                classes_cache.clear()
                classes_cache.extend(r_cls.json())

            # 3. Cargar eventos agendados
            r_ev = api.get_events()
            if r_ev.status_code == 200:
                events_cache.clear()
                events_cache.extend(r_ev.json())

            render_view()
        except Exception as ex:
            show_snack(f"Error al sincronizar agenda: {ex}", error=True)
        finally:
            loading_bar.visible = False
            page.update()

    # ─── Modal para Agregar Clase al Horario ───────────────────────
    def open_add_class_modal():
        if not subjects_cache:
            show_snack("Primero debes registrar materias en la sección 'Notas'", error=True)
            return

        modal_error = ft.Text("", color=AcademixColors.ERROR, size=12, visible=False)

        subject_options = [
            ft.dropdown.Option(s["id"], s["name"]) for s in subjects_cache
        ]
        subject_dd = ft.Dropdown(
            label="Materia",
            options=subject_options,
            value=subject_options[0].key if subject_options else None,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
        )

        day_options = [
            ft.dropdown.Option(str(d_num), d_name) for d_num, d_name, _ in DAYS_OF_WEEK
        ]
        day_dd = ft.Dropdown(
            label="Día de la Semana",
            options=day_options,
            value=str(selected_day[0]),
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        start_time_field = ft.TextField(
            label="Hora de Inicio",
            value="08:00",
            hint_text="Ej: 08:00 o 14:00",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        end_time_field = ft.TextField(
            label="Hora de Fin",
            value="10:00",
            hint_text="Ej: 10:00 o 16:00",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        classroom_field = ft.TextField(
            label="Aula / Salón (Opcional)",
            hint_text="Ej: Aula 204, Laboratorio B",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        professor_field = ft.TextField(
            label="Profesor / Docente (Opcional)",
            hint_text="Ej: Prof. García",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        def save_class(e):
            modal_error.visible = False
            if not subject_dd.value:
                modal_error.value = "Selecciona una materia"
                modal_error.visible = True
                page.update()
                return

            if not start_time_field.value or not end_time_field.value:
                modal_error.value = "Las horas de inicio y fin son obligatorias"
                modal_error.visible = True
                page.update()
                return

            payload = {
                "subject_id": subject_dd.value,
                "day_of_week": int(day_dd.value),
                "start_time": start_time_field.value.strip(),
                "end_time": end_time_field.value.strip(),
                "classroom": classroom_field.value.strip() if classroom_field.value else None,
                "professor": professor_field.value.strip() if professor_field.value else None,
            }

            try:
                resp = api.create_class(payload)
                if resp.status_code in [200, 201]:
                    page.pop_dialog()
                    show_snack("✅ Clase agregada al horario con éxito")
                    load_data()
                else:
                    detail = resp.json().get("detail", "Error al guardar clase")
                    modal_error.value = str(detail)
                    modal_error.visible = True
                    page.update()
            except Exception as ex:
                modal_error.value = f"Error: {ex}"
                modal_error.visible = True
                page.update()

        add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar Clase al Horario 📅", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            content=ft.Container(
                content=ft.Column(
                    [
                        modal_error,
                        subject_dd,
                        day_dd,
                        ft.Row([ft.Container(start_time_field, expand=1), ft.Container(end_time_field, expand=1)], spacing=10),
                        classroom_field,
                        professor_field,
                    ],
                    spacing=12,
                    tight=True,
                ),
                width=380,
                padding=10,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Guardar Clase",
                    on_click=save_class,
                    style=ft.ButtonStyle(
                        bgcolor=AcademixColors.CYAN_NEON,
                        color=ft.Colors.BLACK,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
        )
        page.show_dialog(add_dialog)

    # ─── Modal para Agendar Evaluación / Recordatorio ─────────────
    def open_add_event_modal():
        if not subjects_cache:
            show_snack("Primero debes registrar materias", error=True)
            return

        modal_error = ft.Text("", color=AcademixColors.ERROR, size=12, visible=False)

        subject_options = [ft.dropdown.Option("", "Sin materia específica")] + [
            ft.dropdown.Option(s["id"], s["name"]) for s in subjects_cache
        ]
        subject_dd = ft.Dropdown(
            label="Materia Asociada",
            options=subject_options,
            value=subjects_cache[0]["id"] if subjects_cache else "",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        title_field = ft.TextField(
            label="Título de la Evaluación o Tarea",
            hint_text="Ej: Parcial 2 de Física, Entrega Proyecto",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        topic_field = ft.TextField(
            label="Tema / Contenido a Evaluar",
            hint_text="Ej: Leyes de Newton, Dinámica y Energía",
            multiline=True,
            min_lines=2,
            max_lines=3,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        date_field = ft.TextField(
            label="Fecha (AAAA-MM-DD)",
            value=(datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d"),
            hint_text="Ej: 2026-10-15",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        time_field = ft.TextField(
            label="Hora (HH:MM)",
            value="09:00",
            hint_text="Ej: 09:00 o 15:30",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        reminder_options = [
            ft.dropdown.Option("12", "12 horas antes"),
            ft.dropdown.Option("24", "24 horas antes (1 día)"),
            ft.dropdown.Option("48", "48 horas antes (2 días)"),
            ft.dropdown.Option("72", "3 días antes"),
        ]
        reminder_dd = ft.Dropdown(
            label="Alerta / Recordatorio Previo",
            options=reminder_options,
            value="24",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        def save_event(e):
            modal_error.visible = False
            title = title_field.value.strip() if title_field.value else ""
            if not title:
                modal_error.value = "El título es obligatorio"
                modal_error.visible = True
                page.update()
                return

            try:
                date_str = date_field.value.strip()
                time_str = time_field.value.strip() or "09:00"
                full_dt_str = f"{date_str}T{time_str}:00"
                # Validar parseo
                datetime.fromisoformat(full_dt_str)
            except Exception:
                modal_error.value = "Formato de fecha u hora no válido (usa AAAA-MM-DD y HH:MM)"
                modal_error.visible = True
                page.update()
                return

            payload = {
                "subject_id": subject_dd.value if subject_dd.value else None,
                "title": title,
                "description": topic_field.value.strip() if topic_field.value else None,
                "event_date": full_dt_str,
                "reminder_lead_time_hours": int(reminder_dd.value),
            }

            try:
                resp = api.create_event(payload)
                if resp.status_code in [200, 201]:
                    page.pop_dialog()
                    show_snack("✅ Evaluación agendada con éxito")
                    load_data()
                else:
                    detail = resp.json().get("detail", "Error al agendar evento")
                    modal_error.value = str(detail)
                    modal_error.visible = True
                    page.update()
            except Exception as ex:
                modal_error.value = f"Error: {ex}"
                modal_error.visible = True
                page.update()

        event_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agendar Evaluación / Recordatorio 🔔", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            content=ft.Container(
                content=ft.Column(
                    [
                        modal_error,
                        subject_dd,
                        title_field,
                        topic_field,
                        ft.Row([ft.Container(date_field, expand=1), ft.Container(time_field, expand=1)], spacing=10),
                        reminder_dd,
                    ],
                    spacing=12,
                    tight=True,
                ),
                width=380,
                padding=10,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Agendar",
                    on_click=save_event,
                    style=ft.ButtonStyle(
                        bgcolor=AcademixColors.CYAN_NEON,
                        color=ft.Colors.BLACK,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
        )
        page.show_dialog(event_dialog)

    # ─── Eliminación de Clases y Eventos ──────────────────────────
    def delete_class_item(class_id: str, sub_name: str):
        def delete(e):
            try:
                api.delete_class(class_id)
                page.pop_dialog()
                show_snack(f"Clase de '{sub_name}' eliminada")
                load_data()
            except Exception as ex:
                page.pop_dialog()
                show_snack(f"Error: {ex}", error=True)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar Clase?"),
            content=ft.Text(f"¿Estás seguro de eliminar este bloque de '{sub_name}' del horario?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton("Eliminar", style=ft.ButtonStyle(bgcolor=AcademixColors.ERROR, color=ft.Colors.WHITE), on_click=delete),
            ],
        )
        page.show_dialog(dlg)

    def delete_event_item(event_id: str, title: str):
        def delete(e):
            try:
                api.delete_event(event_id)
                page.pop_dialog()
                show_snack(f"Evento '{title}' eliminado")
                load_data()
            except Exception as ex:
                page.pop_dialog()
                show_snack(f"Error: {ex}", error=True)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar de la Agenda?"),
            content=ft.Text(f"¿Deseas quitar '{title}' de tus recordatorios?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton("Eliminar", style=ft.ButtonStyle(bgcolor=AcademixColors.ERROR, color=ft.Colors.WHITE), on_click=delete),
            ],
        )
        page.show_dialog(dlg)

    # ─── Renderizado de la Interfaz ───────────────────────────────
    def render_view():
        content_container.controls.clear()

        # 1. Pestañas de Selector de Día (Para Modo Día y Modo Semana)
        day_tabs = []
        for d_num, d_name, d_short in DAYS_OF_WEEK:
            is_active = (selected_day[0] == d_num)
            btn = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(d_short, size=11, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON if is_active else ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                        ft.Text(d_name[:3], size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                padding=ft.Padding(12, 8, 12, 8),
                border_radius=12,
                bgcolor=ft.Colors.with_opacity(0.25, AcademixColors.CYAN_NEON) if is_active else ft.Colors.with_opacity(0.08, "#0D1B2A"),
                border=ft.Border.all(1.2, AcademixColors.CYAN_NEON if is_active else ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                on_click=lambda _, num=d_num: [selected_day.__setitem__(0, num), render_view(), page.update()],
            )
            day_tabs.append(btn)

        day_selector_row = ft.Row(day_tabs, scroll=ft.ScrollMode.AUTO, spacing=8)

        # 2. Clases del Día Seleccionado
        day_classes = [c for c in classes_cache if c["day_of_week"] == selected_day[0]]
        day_name_str = next(d_name for d_num, d_name, _ in DAYS_OF_WEEK if d_num == selected_day[0])

        class_cards = []
        if day_classes:
            for cls in day_classes:
                sub_color = cls.get("color_hex") or AcademixColors.CYAN_NEON
                card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=6, height=54, bgcolor=sub_color, border_radius=3),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(f"{cls['start_time']} - {cls['end_time']}", size=13, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
                                            ft.Container(
                                                content=ft.Text(cls.get("classroom") or "Aula por asignar", size=11, color=ft.Colors.WHITE),
                                                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                                                padding=ft.Padding(8, 2, 8, 2),
                                                border_radius=6,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    ft.Text(cls["subject_name"], size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text(f"Profesor: {cls.get('professor') or 'No especificado'}", size=12, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE)),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=AcademixColors.ERROR,
                                tooltip="Eliminar bloque de clase",
                                on_click=lambda _, c_id=cls["id"], s_name=cls["subject_name"]: delete_class_item(c_id, s_name),
                            ),
                        ],
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=16,
                    border_radius=16,
                    bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                )
                class_cards.append(card)
        else:
            class_cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.EVENT_AVAILABLE_OUTLINED, size=40, color=ft.Colors.with_opacity(0.4, AcademixColors.CYAN_NEON)),
                            ft.Text(f"No tienes clases programadas para el {day_name_str}", size=14, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                            ft.TextButton("+ Agregar clase a este día", icon=ft.Icons.ADD, on_click=lambda _: open_add_class_modal()),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=26,
                    alignment=ft.Alignment.CENTER,
                    border_radius=16,
                    bgcolor=ft.Colors.with_opacity(0.12, "#0D1B2A"),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
                )
            )

        # 3. Sección de Agenda y Próximas Evaluaciones / Alertas
        event_cards = []
        if events_cache:
            for ev in events_cache:
                ev_color = ev.get("color_hex") or AcademixColors.YELLOW_NEON
                try:
                    dt = datetime.fromisoformat(ev["event_date"])
                    date_display = dt.strftime("%d %b - %H:%M")
                except Exception:
                    date_display = str(ev["event_date"])[:16]

                ev_card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=AcademixColors.YELLOW_NEON, size=20),
                                padding=10,
                                border_radius=12,
                                bgcolor=ft.Colors.with_opacity(0.15, AcademixColors.YELLOW_NEON),
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(date_display, size=12, weight=ft.FontWeight.BOLD, color=AcademixColors.YELLOW_NEON),
                                            ft.Container(
                                                content=ft.Text(ev.get("subject_name") or "General", size=10, color=ft.Colors.WHITE),
                                                bgcolor=ft.Colors.with_opacity(0.18, ev_color),
                                                padding=ft.Padding(6, 2, 6, 2),
                                                border_radius=6,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    ft.Text(ev["title"], size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text(
                                        ev.get("description") or "Sin temas detallados",
                                        size=12,
                                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(f"🔔 Alerta programada: {ev.get('reminder_lead_time_hours', 24)}h antes", size=11, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=AcademixColors.ERROR,
                                tooltip="Eliminar de agenda",
                                on_click=lambda _, e_id=ev["id"], t=ev["title"]: delete_event_item(e_id, t),
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=14,
                    border_radius=16,
                    bgcolor=ft.Colors.with_opacity(0.2, "#0D1B2A"),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.15, AcademixColors.YELLOW_NEON)),
                )
                event_cards.append(ev_card)
        else:
            event_cards.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.EVENT_NOTE_OUTLINED, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                            ft.Text("No tienes evaluaciones agendadas próximas. ¡Agrega tus fechas de examen!", size=13, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE)),
                        ],
                        spacing=10,
                    ),
                    padding=16,
                    border_radius=14,
                    bgcolor=ft.Colors.with_opacity(0.1, "#0D1B2A"),
                )
            )

        # Montar el panel principal
        content_container.controls.extend([
            # Selector de Día Interactivo
            ft.Text("Selecciona el Día:", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.with_opacity(0.75, ft.Colors.WHITE)),
            day_selector_row,
            ft.Container(height=8),
            # Clases del día
            ft.Row(
                [
                    ft.Text(f"Clases del {day_name_str} 📚", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.TextButton(
                        "+ Agregar Clase",
                        icon=ft.Icons.ADD_ROUNDED,
                        on_click=lambda _: open_add_class_modal(),
                        style=ft.ButtonStyle(color=AcademixColors.CYAN_NEON),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Column(class_cards, spacing=10),
            ft.Container(height=16),
            ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=10),
            # Próximas Evaluaciones y Alertas
            ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ALARM, color=AcademixColors.YELLOW_NEON, size=20),
                            ft.Text("Agenda de Evaluaciones & Recordatorios 🔔", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    ),
                    ft.FilledButton(
                        "+ Agendar Evaluación",
                        icon=ft.Icons.ADD_ALERT_OUTLINED,
                        on_click=lambda _: open_add_event_modal(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, AcademixColors.YELLOW_NEON),
                            color=AcademixColors.YELLOW_NEON,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Column(event_cards, spacing=10),
        ])

    load_data()

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Agenda y Horario Académico ⏰", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Gestiona tus clases semanales y programa alertas previas a tus exámenes.", size=13, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.FilledButton(
                        "+ Clase",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: open_add_class_modal(),
                        style=ft.ButtonStyle(
                            bgcolor=AcademixColors.CYAN_NEON,
                            color=ft.Colors.BLACK,
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.Padding(16, 10, 16, 10),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=10),
            loading_bar,
            content_container,
        ],
        spacing=0,
        expand=True,
    )
