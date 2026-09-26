import flet as ft
from app.core.api_client import api
from app.core.state import state
from app.theme.colors import AcademixColors

COLOR_PALETTE = [
    ("#00E5FF", "Cian Neón"),
    ("#7C4DFF", "Púrpura Neón"),
    ("#00E676", "Verde Esmeralda"),
    ("#FF9100", "Ámbar Neón"),
    ("#FF1744", "Rosa Neón"),
    ("#2979FF", "Azul Eléctrico"),
]

_current_subjects_cache = []
_is_subjects_fetching = False

def SubjectsScreen(page: ft.Page, view_mode: str = "notas"):
    """
    Pantalla interactiva con CRUD completo de Materias y Evaluaciones conectado a Supabase / PostgreSQL.
    """
    subjects_container = ft.Column(spacing=16)
    loading_ring = ft.ProgressBar(visible=False, color=AcademixColors.CYAN_NEON)
    
    current_subjects_cache = _current_subjects_cache
    subject_cards_map = {}

    def recalculate_subject_metrics_locally(sub):
        max_scale = float(sub.get("max_scale", 20.0))
        passing_grade = float(sub.get("passing_grade", 10.0))
        evals = sub.get("evaluations", [])

        accum_pts = 0.0
        accum_pct = 0.0

        for ev in evals:
            grade_obj = ev.get("grade")
            score_val = grade_obj.get("score") if grade_obj else None
            weight = float(ev.get("weight_percent", 0.0))
            if score_val is not None:
                pts_contrib = round(float(score_val) * (weight / 100.0), 2)
                accum_pts += pts_contrib
                accum_pct += weight

        accum_pts = round(accum_pts, 2)
        accum_pct = round(accum_pct, 1)

        is_passed = accum_pts >= passing_grade
        points_needed = round(max(0.0, passing_grade - accum_pts), 2) if not is_passed else 0.0
        remaining_weight = max(0.0, round(100.0 - accum_pct, 1))
        max_possible = min(max_scale, round(accum_pts + max_scale * (remaining_weight / 100.0), 2))

        required_avg = None
        if is_passed:
            required_avg = 0.0
        elif remaining_weight > 0:
            required_avg = round(points_needed / (remaining_weight / 100.0), 2)

        sub["accumulated_points"] = accum_pts
        sub["accumulated_percent"] = accum_pct
        sub["is_passed"] = is_passed
        sub["points_needed_to_pass"] = points_needed
        sub["max_possible_grade"] = max_possible
        sub["required_average_remaining"] = required_avg

    def show_snack(message: str, error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_900 if error else ft.Colors.BLUE_GREY_900,
        )
        page.show_dialog(snack)

    import threading

    def load_data(force: bool = False):
        global _is_subjects_fetching
        if _is_subjects_fetching and not force:
            return

        def _fetch():
            global _is_subjects_fetching
            _is_subjects_fetching = True
            if not current_subjects_cache:
                loading_ring.visible = True
                try:
                    page.update()
                except Exception:
                    pass
            try:
                resp = api.get_subjects()
                if resp.status_code == 200:
                    subjects = resp.json()
                    current_subjects_cache.clear()
                    current_subjects_cache.extend(subjects)
                    state.cached_subjects = current_subjects_cache
                    render_subjects(subjects)
                else:
                    show_snack("Error al cargar materias de la base de datos", error=True)
            except Exception as ex:
                show_snack(f"Error de conexión: {ex}", error=True)
            finally:
                _is_subjects_fetching = False
                loading_ring.visible = False
                try:
                    page.update()
                except Exception:
                    pass

        # Renderizar al instante con datos en memoria
        render_subjects(current_subjects_cache)
        threading.Thread(target=_fetch, daemon=True).start()

    # ─── Modal para Crear / Editar Materia ───────────────────────
    def open_subject_modal(subject_to_edit=None):
        is_edit = subject_to_edit is not None
        title_text = "Editar Materia" if is_edit else "Nueva Materia"

        modal_error = ft.Text("", color=AcademixColors.ERROR, size=12, visible=False)

        name_field = ft.TextField(
            label="Nombre de la Materia",
            value=subject_to_edit.get("name", "") if is_edit else "",
            hint_text="Ej: Cálculo I, Programación Web",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
            color=ft.Colors.WHITE,
        )

        credits_field = ft.TextField(
            label="Unidades de Crédito / Horas",
            value=str(subject_to_edit.get("credits", 3)) if is_edit else "3",
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE))),
            color=ft.Colors.WHITE,
        )

        selected_color = [subject_to_edit.get("color_hex", "#00E5FF") if is_edit else "#00E5FF"]
        color_swatches = []
        color_row = ft.Row(spacing=10)

        def make_select_color(col):
            def select_c(e):
                selected_color[0] = col
                for swatch, c in color_swatches:
                    swatch.border = ft.Border.all(2.5, ft.Colors.WHITE if c == col else ft.Colors.TRANSPARENT)
                page.update()
            return select_c

        for hex_code, color_label in COLOR_PALETTE:
            swatch = ft.Container(
                width=32,
                height=32,
                border_radius=16,
                bgcolor=hex_code,
                border=ft.Border.all(2.5, ft.Colors.WHITE if hex_code == selected_color[0] else ft.Colors.TRANSPARENT),
                tooltip=color_label,
                on_click=make_select_color(hex_code),
            )
            color_swatches.append((swatch, hex_code))
            color_row.controls.append(swatch)

        def save_subject(e):
            modal_error.visible = False
            name = name_field.value.strip() if name_field.value else ""
            if not name:
                modal_error.value = "El nombre de la materia es obligatorio"
                modal_error.visible = True
                page.update()
                return

            try:
                credits_val = int(credits_field.value or 0)
                if credits_val < 0:
                    modal_error.value = "Los créditos no pueden ser negativos"
                    modal_error.visible = True
                    page.update()
                    return
            except ValueError:
                modal_error.value = "Los créditos deben ser un número entero"
                modal_error.visible = True
                page.update()
                return

            payload = {
                "name": name,
                "credits": credits_val,
                "color_hex": selected_color[0],
            }

            try:
                if is_edit:
                    resp = api.update_subject(subject_to_edit["id"], payload)
                else:
                    resp = api.create_subject(payload)

                if resp.status_code in [200, 201]:
                    page.pop_dialog()
                    show_snack("✅ Materia guardada en la base de datos")
                    load_data()
                else:
                    detail = resp.json().get("detail", "Error al guardar la materia")
                    modal_error.value = str(detail)
                    modal_error.visible = True
                    page.update()
            except Exception as ex:
                modal_error.value = f"Error de conexión: {ex}"
                modal_error.visible = True
                page.update()

        subject_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            content=ft.Container(
                content=ft.Column(
                    [
                        modal_error,
                        name_field,
                        credits_field,
                        ft.Text("Color Distintivo:", size=13, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                        color_row,
                    ],
                    spacing=14,
                    tight=True,
                ),
                width=380,
                padding=10,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Guardar",
                    on_click=save_subject,
                    style=ft.ButtonStyle(
                        bgcolor=AcademixColors.CYAN_NEON,
                        color=ft.Colors.BLACK,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
        )
        page.show_dialog(subject_dialog)

    # ─── Validación de Límite y Apertura de Modal ─────────────────
    def check_and_open_eval_modal(subject_id: str):
        sub = next((s for s in current_subjects_cache if s["id"] == subject_id), None)
        if sub:
            max_evals = sub.get("max_evaluations")
            if not max_evals and state.current_user and state.current_user.get("settings"):
                max_evals = state.current_user["settings"].get("default_eval_count", 5)
            if not max_evals:
                max_evals = 5

            existing_evals = sub.get("evaluations", [])
            if len(existing_evals) >= int(max_evals):
                show_snack("Has alcanzado el límite máximo de evaluaciones configuradas para este periodo", error=True)
                return
        open_eval_modal(subject_id)

    # ─── Modal para Agregar / Editar Evaluación ───────────────────
    def open_eval_modal(subject_id: str, eval_to_edit=None):
        is_edit = eval_to_edit is not None
        title_text = "Editar Evaluación" if is_edit else "Nueva Evaluación"

        current_sub = next((s for s in current_subjects_cache if s["id"] == subject_id), None)
        if not is_edit and current_sub:
            max_evals = current_sub.get("max_evaluations")
            if not max_evals and state.current_user and state.current_user.get("settings"):
                max_evals = state.current_user["settings"].get("default_eval_count", 5)
            if not max_evals:
                max_evals = 5

            if len(current_sub.get("evaluations", [])) >= int(max_evals):
                show_snack("Has alcanzado el límite máximo de evaluaciones configuradas para este periodo", error=True)
                return

        modal_error = ft.Text("", color=AcademixColors.ERROR, size=12, visible=False)

        name_field = ft.TextField(
            label="Nombre de la Evaluación",
            value=eval_to_edit.get("name", "") if is_edit else "",
            hint_text="Ej: Parcial 1, Taller Práctico, Tesis",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
            color=ft.Colors.WHITE,
        )

        type_dd = ft.Dropdown(
            label="Tipo de Evaluación",
            value=eval_to_edit.get("eval_type", "exam") if is_edit else "exam",
            options=[
                ft.dropdown.Option("exam", "Examen / Parcial"),
                ft.dropdown.Option("quiz", "Quiz / Corto"),
                ft.dropdown.Option("project", "Proyecto / Trabajo"),
                ft.dropdown.Option("homework", "Tarea / Asignación"),
                ft.dropdown.Option("other", "Otro"),
            ],
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        desc_field = ft.TextField(
            label="Tema / Contenido a Evaluar (Opcional)",
            value=eval_to_edit.get("description", "") if is_edit else "",
            hint_text="Ej: Capítulos 1 al 3, Dinámica y Leyes de Newton",
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            color=ft.Colors.WHITE,
        )

        weight_field = ft.TextField(
            label="Porcentaje de Peso (%)",
            value=str(eval_to_edit.get("weight_percent", 25)) if is_edit else "25",
            hint_text="Ej: 20, 25, 30",
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE))),
            color=ft.Colors.WHITE,
        )

        initial_score = ""
        if is_edit and eval_to_edit.get("grade") and eval_to_edit["grade"].get("score") is not None:
            initial_score = str(eval_to_edit["grade"]["score"])

        score_field = ft.TextField(
            label="Nota Obtenida (Opcional si aún no se ha presentado)",
            value=initial_score,
            hint_text="Ej: 16.5 (dejar vacío si está pendiente)",
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE))),
            color=ft.Colors.WHITE,
        )

        def save_eval(e):
            modal_error.visible = False
            name = name_field.value.strip() if name_field.value else ""
            if not name:
                modal_error.value = "El nombre de la evaluación es obligatorio"
                modal_error.visible = True
                page.update()
                return

            try:
                weight = float(weight_field.value or 0)
                if weight <= 0 or weight > 100:
                    modal_error.value = "La ponderación debe estar entre 1% y 100%"
                    modal_error.visible = True
                    page.update()
                    return
            except ValueError:
                modal_error.value = "Ponderación no válida"
                modal_error.visible = True
                page.update()
                return

            # Validar que la sumatoria acumulada de ponderaciones no exceda el 100%
            current_sub = next((s for s in current_subjects_cache if s["id"] == subject_id), None)
            if current_sub:
                existing_weight = sum(
                    ev["weight_percent"] for ev in current_sub.get("evaluations", [])
                    if not (is_edit and ev["id"] == eval_to_edit["id"])
                )
                if existing_weight + weight > 100.0:
                    modal_error.value = f"La ponderación total ({existing_weight + weight:.1f}%) excedería el 100% permitido."
                    modal_error.visible = True
                    page.update()
                    return

            # Validar escala de notas institucional
            max_scale = 20.0
            if state.current_user and state.current_user.get("settings"):
                max_scale = float(state.current_user["settings"].get("max_grade", 20.0))

            score = None
            if score_field.value and score_field.value.strip() != "":
                try:
                    score = float(score_field.value.strip())
                    if score < 0 or score > max_scale:
                        modal_error.value = f"La nota debe estar entre 0 y {max_scale:.1f}"
                        modal_error.visible = True
                        page.update()
                        return
                except ValueError:
                    modal_error.value = "La nota debe ser un número válido"
                    modal_error.visible = True
                    page.update()
                    return

            payload = {
                "name": name,
                "description": desc_field.value.strip() if desc_field.value else None,
                "eval_type": type_dd.value,
                "weight_percent": weight,
                "score": score,
            }

            try:
                if is_edit:
                    resp = api.update_evaluation(eval_to_edit["id"], payload)
                else:
                    resp = api.create_evaluation(subject_id, payload)

                if resp.status_code in [200, 201]:
                    saved_eval = resp.json()
                    page.pop_dialog()
                    show_snack("✅ Evaluación guardada en la base de datos")
                    sub = next((s for s in current_subjects_cache if s["id"] == subject_id), None)
                    if sub:
                        if is_edit:
                            sub["evaluations"] = [saved_eval if ev["id"] == eval_to_edit["id"] else ev for ev in sub.get("evaluations", [])]
                        else:
                            sub["evaluations"] = sub.get("evaluations", []) + [saved_eval]
                        recalculate_subject_metrics_locally(sub)
                        if subject_id in subject_cards_map:
                            subject_cards_map[subject_id].content = build_subject_card(sub)
                            subject_cards_map[subject_id].update()
                        else:
                            load_data()
                    else:
                        load_data()
                else:
                    detail = resp.json().get("detail", "Error al guardar la evaluación")
                    modal_error.value = str(detail)
                    modal_error.visible = True
                    page.update()
            except Exception as ex:
                modal_error.value = f"Error de conexión: {ex}"
                modal_error.visible = True
                page.update()

        eval_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            content=ft.Container(
                content=ft.Column(
                    [
                        modal_error,
                        name_field,
                        desc_field,
                        type_dd,
                        weight_field,
                        score_field,
                    ],
                    spacing=14,
                    tight=True,
                ),
                width=380,
                padding=10,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Guardar",
                    on_click=save_eval,
                    style=ft.ButtonStyle(
                        bgcolor=AcademixColors.CYAN_NEON,
                        color=ft.Colors.BLACK,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
        )
        page.show_dialog(eval_dialog)

    def confirm_delete_subject(subject_id: str, name: str):
        def delete(e):
            try:
                resp = api.delete_subject(subject_id)
                page.pop_dialog()
                if resp.status_code == 200:
                    show_snack(f"Materia '{name}' eliminada correctamente")
                    load_data()
                else:
                    show_snack("Error al eliminar la materia", error=True)
            except Exception as ex:
                page.pop_dialog()
                show_snack(f"Error: {ex}", error=True)

        del_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar Materia?"),
            content=ft.Text(f"Se borrará '{name}' y todas sus evaluaciones registradas."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Eliminar",
                    style=ft.ButtonStyle(bgcolor=AcademixColors.ERROR, color=ft.Colors.WHITE),
                    on_click=delete,
                ),
            ],
        )
        page.show_dialog(del_dialog)

    def confirm_delete_eval(sub_id: str, eval_id: str, name: str):
        def delete(e):
            try:
                resp = api.delete_evaluation(eval_id)
                page.pop_dialog()
                if resp.status_code in [200, 204]:
                    sub = next((s for s in current_subjects_cache if s["id"] == sub_id), None)
                    if sub:
                        sub["evaluations"] = [ev for ev in sub.get("evaluations", []) if ev["id"] != eval_id]
                        recalculate_subject_metrics_locally(sub)
                        if sub_id in subject_cards_map:
                            subject_cards_map[sub_id].content = build_subject_card(sub)
                            subject_cards_map[sub_id].update()
                    show_snack(f"Evaluación '{name}' eliminada correctamente")
                else:
                    show_snack("Error al eliminar la evaluación", error=True)
            except Exception as ex:
                page.pop_dialog()
                show_snack(f"Error: {ex}", error=True)

        del_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar Evaluación?", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            content=ft.Text(f"¿Estás seguro de eliminar '{name}'?", color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Eliminar",
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_ACCENT, color=ft.Colors.WHITE),
                    on_click=delete,
                ),
            ],
        )
        page.show_dialog(del_dialog)

    # ─── Construcción de Tarjeta Individual de Materia ───────────
    def build_subject_card(sub):
        sub_color = sub.get("color_hex") or AcademixColors.CYAN_NEON
        sub_id = sub["id"]
        evals = sub.get("evaluations", [])

        # Métricas del Motor de Cálculo Adaptativo
        accum_pts = sub.get("accumulated_points", 0.0)
        accum_pct = sub.get("accumulated_percent", 0.0)
        max_scale = sub.get("max_scale", 20.0)
        passing_grade = sub.get("passing_grade", 10.0)
        points_needed = sub.get("points_needed_to_pass", 0.0)
        is_passed = sub.get("is_passed", False)
        max_possible = sub.get("max_possible_grade", max_scale)
        req_avg = sub.get("required_average_remaining")

        # Badge de Puntos Reales sobre 20
        if accum_pct > 0:
            if is_passed:
                avg_badge_text = f"⭐ {accum_pts:.2f} / {int(max_scale)} pts (¡Aprobada!)"
                avg_color = AcademixColors.SUCCESS
            elif max_possible < passing_grade:
                avg_badge_text = f"❌ {accum_pts:.2f} / {int(max_scale)} pts (Reprobada)"
                avg_color = AcademixColors.ERROR
            elif accum_pts >= passing_grade * 0.7:
                avg_badge_text = f"🔥 {accum_pts:.2f} / {int(max_scale)} pts (Faltan {points_needed:.2f})"
                avg_color = AcademixColors.CYAN_NEON
            else:
                avg_badge_text = f"⚠️ {accum_pts:.2f} / {int(max_scale)} pts (Faltan {points_needed:.2f})"
                avg_color = AcademixColors.WARNING
        else:
            avg_badge_text = f"0.00 / {int(max_scale)} pts"
            avg_color = ft.Colors.with_opacity(0.6, ft.Colors.WHITE)

        # Texto descriptivo de proyección
        if is_passed:
            projection_desc = f"🎉 ¡Materia superada! Ya acumulaste {accum_pts:.2f} de los {int(passing_grade)} puntos mínimos requeridos."
            desc_color = AcademixColors.SUCCESS
        elif max_possible < passing_grade:
            projection_desc = f"⚠️ Matemáticamente reprobada. Máximo alcanzable: {max_possible:.2f} pts en el {100 - accum_pct:.0f}% restante."
            desc_color = AcademixColors.ERROR
        else:
            req_txt = f" | Requiere promedio de {req_avg:.2f} pts en lo pendiente" if (req_avg is not None and req_avg > 0) else ""
            projection_desc = f"Faltan {points_needed:.2f} pts para aprobar ({int(passing_grade)} pts). Máx alcanzable: {max_possible:.2f} pts{req_txt}."
            desc_color = ft.Colors.with_opacity(0.85, ft.Colors.WHITE)

        # Barra de puntos ganados sobre 20
        pts_flex = max(1, int((accum_pts / max_scale) * 100)) if accum_pts > 0 else 0
        empty_flex = max(1, 100 - pts_flex)

        # Construir lista de evaluaciones con aporte a la definitiva
        eval_rows = []
        if evals:
            for ev in evals:
                ev_id = ev["id"]
                grade_obj = ev.get("grade")
                score_val = grade_obj.get("score") if grade_obj else None
                weight = ev.get("weight_percent", 0.0)
                topic = ev.get("description")

                if score_val is not None:
                    pts_contrib = round(score_val * (weight / 100.0), 2)
                    score_pill = ft.Container(
                        content=ft.Text(f"{score_val:.1f} / {int(max_scale)}", size=12, weight=ft.FontWeight.BOLD, color=AcademixColors.SUCCESS if score_val >= passing_grade else AcademixColors.ERROR),
                        bgcolor=ft.Colors.with_opacity(0.15, AcademixColors.SUCCESS if score_val >= passing_grade else AcademixColors.ERROR),
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=8,
                    )
                    contrib_pill = ft.Container(
                        content=ft.Text(f"+{pts_contrib:.2f} pts", size=11, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
                        bgcolor=ft.Colors.with_opacity(0.18, AcademixColors.CYAN_NEON),
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=8,
                        tooltip="Puntos ganados aportados a la nota final",
                    )
                else:
                    potential = round(max_scale * (weight / 100.0), 2)
                    score_pill = ft.Container(
                        content=ft.Text("Pendiente", size=12, color=AcademixColors.WARNING),
                        bgcolor=ft.Colors.with_opacity(0.15, AcademixColors.WARNING),
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=8,
                    )
                    contrib_pill = ft.Container(
                        content=ft.Text(f"Hasta +{potential:.2f} pts", size=11, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE)),
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=8,
                        tooltip="Puntos máximos en juego",
                    )

                title_col = [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.FACT_CHECK_OUTLINED, size=16, color=sub_color),
                            ft.Text(ev["name"], size=13, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    )
                ]
                if topic:
                    title_col.append(ft.Text(topic, size=11, color=ft.Colors.with_opacity(0.55, ft.Colors.WHITE), italic=True))

                eval_row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(title_col, spacing=2, expand=True),
                            ft.Container(
                                content=ft.Text(f"{weight:.0f}%", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                padding=ft.Padding(8, 4, 8, 4),
                                border_radius=8,
                            ),
                            score_pill,
                            contrib_pill,
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_size=16,
                                icon_color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                tooltip="Modificar nota o evaluación",
                                on_click=lambda _, s_id=sub_id, e_obj=ev: open_eval_modal(s_id, e_obj),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=16,
                                icon_color=ft.Colors.RED_ACCENT,
                                tooltip="Eliminar evaluación",
                                on_click=lambda _, s_id=sub_id, e_id=ev_id, e_name=ev["name"]: confirm_delete_eval(s_id, e_id, e_name),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(12, 8, 12, 8),
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.1, "#0D1B2A"),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
                )
                eval_rows.append(eval_row)
        else:
            eval_rows.append(
                ft.Text(
                    "No has agregado evaluaciones a esta materia. Haz clic en '+ Evaluación' para registrar el primer examen o tarea.",
                    size=12,
                    color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                    italic=True,
                )
            )

        # Tarjeta de la Materia
        card = ft.Container(
            content=ft.Column(
                [
                    # Cabecera de la Materia (Arquitectura Mobile-First en 2 filas limpias)
                    ft.Column(
                        [
                            # Fila 1: Color de la materia + Nombre + Botones de Acción
                            ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(width=6, height=22, bgcolor=sub_color, border_radius=3),
                                            ft.Text(sub["name"], size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                        ],
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=AcademixColors.CYAN_NEON,
                                                icon_size=18,
                                                padding=4,
                                                tooltip="Editar Materia",
                                                on_click=lambda _, s_obj=sub: open_subject_modal(s_obj),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=AcademixColors.ERROR,
                                                icon_size=18,
                                                padding=4,
                                                tooltip="Eliminar Materia",
                                                on_click=lambda _, s_id=sub_id, s_name=sub["name"]: confirm_delete_subject(s_id, s_name),
                                            ),
                                        ],
                                        spacing=0,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            # Fila 2: Badges (Créditos UC + Estado de Calificación / Promedio)
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(f"{sub.get('credits', 0)} UC", size=10, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                                        padding=ft.Padding(8, 3, 8, 3),
                                        border_radius=6,
                                    ),
                                    ft.Container(
                                        content=ft.Text(avg_badge_text, size=11, weight=ft.FontWeight.BOLD, color=avg_color),
                                        bgcolor=ft.Colors.with_opacity(0.14, avg_color),
                                        padding=ft.Padding(10, 3, 10, 3),
                                        border_radius=8,
                                        border=ft.Border.all(1, ft.Colors.with_opacity(0.35, avg_color)),
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=6,
                    ),
                    # Barra de Progreso de Puntos Reales Ganados
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(f"Puntos Ganados: {accum_pts:.2f} / {int(max_scale)} pts", size=12, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
                                    ft.Text(f"Evaluado: {accum_pct:.0f}% de 100%", size=11, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Container(
                                            gradient=ft.LinearGradient(
                                                colors=[sub_color, AcademixColors.SUCCESS if is_passed else AcademixColors.CYAN_NEON]
                                            ),
                                            height=6,
                                            border_radius=3,
                                            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.4, sub_color)),
                                            expand=pts_flex if pts_flex > 0 else 1,
                                        ),
                                        ft.Container(
                                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                            height=6,
                                            border_radius=3,
                                            expand=empty_flex,
                                        ),
                                    ] if pts_flex > 0 else [
                                        ft.Container(
                                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                            height=6,
                                            border_radius=3,
                                            expand=100,
                                        )
                                    ],
                                    spacing=0,
                                ),
                            ),
                            ft.Text(projection_desc, size=11, color=desc_color),
                        ],
                        spacing=6,
                    ),
                    ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), height=14),
                    # Sub-sección de Evaluaciones
                    ft.Row(
                        [
                            ft.Text("Evaluaciones & Calificaciones:", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                            ft.TextButton(
                                "Evaluación",
                                icon=ft.Icons.ADD,
                                on_click=lambda _, s_id=sub_id: check_and_open_eval_modal(s_id),
                                style=ft.ButtonStyle(color=AcademixColors.CYAN_NEON),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Column(eval_rows, spacing=8),
                ],
                spacing=12,
            ),
            padding=20,
            border_radius=18,
            bgcolor=ft.Colors.with_opacity(0.24, "#0D1B2A"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 6)),
        )
        return card

    # ─── Renderizado de Materias y Evaluaciones ──────────────────
    def render_subjects(subjects):
        subjects_container.controls.clear()
        subject_cards_map.clear()

        if not subjects:
            # Estado Vacío Elegante (Sin Materias Reales aún)
            empty_state = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.AUTO_STORIES_OUTLINED, size=54, color=AcademixColors.CYAN_NEON),
                            padding=16,
                            border_radius=30,
                            bgcolor=ft.Colors.with_opacity(0.12, AcademixColors.CYAN_NEON),
                        ),
                        ft.Text("Aún no tienes materias registradas", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(
                            "Comienza agregando las materias que estás cursando este periodo.\nPodrás registrar tus evaluaciones y notas para que tus promedios se calculen automáticamente.",
                            size=13,
                            color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.FilledButton(
                            "+ Agregar Mi Primera Materia",
                            icon=ft.Icons.ADD_ROUNDED,
                            on_click=lambda _: open_subject_modal(),
                            style=ft.ButtonStyle(
                                bgcolor=AcademixColors.CYAN_NEON,
                                color=ft.Colors.BLACK,
                                padding=ft.Padding(20, 14, 20, 14),
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=50,
                border_radius=22,
                bgcolor=ft.Colors.with_opacity(0.2, "#0D1B2A"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
                alignment=ft.Alignment.CENTER,
            )
            subjects_container.controls.append(empty_state)
            return

        # Si hay materias, renderizamos cada tarjeta de materia
        for sub in subjects:
            card_container = ft.Container(content=build_subject_card(sub))
            subject_cards_map[sub["id"]] = card_container
            subjects_container.controls.append(card_container)

    # Cargar datos al iniciar
    load_data()

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Notas & Asignaturas 📝", size=19, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Puntos acumulados y metas por materia", size=12, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.FilledButton(
                        "+ Materia",
                        icon=ft.Icons.ADD_ROUNDED,
                        on_click=lambda _: open_subject_modal(),
                        style=ft.ButtonStyle(
                            bgcolor=AcademixColors.CYAN_NEON,
                            color=ft.Colors.BLACK,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding(12, 8, 12, 8),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=10),
            loading_ring,
            subjects_container,
        ],
        spacing=0,
    )
