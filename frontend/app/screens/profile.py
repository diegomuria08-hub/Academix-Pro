import flet as ft
from app.core.api_client import api
from app.core.state import state
from app.theme.colors import AcademixColors


def _glass_field(label: str, value: str = "", hint_text: str = "", keyboard_type=None):
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint_text,
        keyboard_type=keyboard_type,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.with_opacity(0.75, ft.Colors.WHITE)),
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        ),
        focused_border_color=AcademixColors.CYAN_NEON,
        focused_border_width=1.5,
    )


def ProfileScreen(page: ft.Page, focus_settings: bool = False):
    profile = state.current_user.get("profile", {}) if state.current_user else {}
    settings_data = state.current_user.get("settings", {}) if state.current_user else {}

    def show_snack(message: str, error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_900 if error else ft.Colors.BLUE_GREY_900,
        )
        page.show_dialog(snack)

    # ─── Campos de Datos Personales ─────────────────────────────
    first_name_field = _glass_field("Nombre", value=profile.get("first_name", ""), hint_text="Tu nombre")
    last_name_field = _glass_field("Apellido", value=profile.get("last_name", ""), hint_text="Tu apellido")
    institution_field = _glass_field("Institución / Universidad", value=profile.get("institution_name", "") or "", hint_text="Ej: UCV, USB, UCAB, Liceo...")
    avatar_url_field = _glass_field("URL de Foto de Perfil (Opcional)", value=profile.get("avatar_url", "") or "", hint_text="Pega aquí el enlace directo a tu foto de perfil")

    student_type_dd = ft.Dropdown(
        label="Tipo de Estudiante",
        value=profile.get("student_type", "university"),
        options=[
            ft.dropdown.Option("high_school", "Liceo / Bachillerato"),
            ft.dropdown.Option("university", "Universidad"),
        ],
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.15, "#0D1B2A"),
        color=ft.Colors.WHITE,
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        ),
        focused_border_color=AcademixColors.CYAN_NEON,
    )

    # ─── Avatar Preview ─────────────────────────────────────────
    def build_avatar_widget(url: str, name: str):
        if url and url.strip():
            return ft.CircleAvatar(
                foreground_image_src=url.strip(),
                radius=36,
                bgcolor=AcademixColors.PRIMARY_PURPLE,
            )
        initial = name[:1].upper() if name else "D"
        return ft.CircleAvatar(
            content=ft.Text(initial, size=24, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
            radius=36,
            bgcolor=ft.Colors.with_opacity(0.25, "#0D1B2A"),
        )

    avatar_preview_container = ft.Container(
        content=build_avatar_widget(profile.get("avatar_url"), profile.get("first_name", "Diego")),
        border=ft.Border.all(2, AcademixColors.CYAN_NEON),
        shape=ft.BoxShape.CIRCLE,
        shadow=ft.BoxShadow(blur_radius=14, color=ft.Colors.with_opacity(0.5, AcademixColors.CYAN_NEON)),
    )

    def on_avatar_changed(e):
        name = first_name_field.value or "D"
        avatar_preview_container.content = build_avatar_widget(avatar_url_field.value, name)
        page.update()

    avatar_url_field.on_change = on_avatar_changed
    first_name_field.on_change = on_avatar_changed

    # ─── Campos de Configuración Académica ──────────────────────
    min_grade_field = _glass_field("Nota Mínima", value=str(settings_data.get("min_grade", 0.0)), keyboard_type=ft.KeyboardType.NUMBER)
    max_grade_field = _glass_field("Nota Máxima", value=str(settings_data.get("max_grade", 20.0)), keyboard_type=ft.KeyboardType.NUMBER)
    passing_grade_field = _glass_field("Nota para Aprobar", value=str(settings_data.get("passing_grade", 10.0)), keyboard_type=ft.KeyboardType.NUMBER)
    default_evals_field = _glass_field("Evaluaciones Estándar por Periodo", value=str(settings_data.get("default_eval_count", 5)), keyboard_type=ft.KeyboardType.NUMBER, hint_text="Ej: 5")

    # ─── Handlers ───────────────────────────────────────────────
    def save_profile(e):
        data = {
            "first_name": first_name_field.value.strip() if first_name_field.value else "",
            "last_name": last_name_field.value.strip() if last_name_field.value else "",
            "institution_name": institution_field.value.strip() if institution_field.value else "",
            "student_type": student_type_dd.value,
            "avatar_url": avatar_url_field.value.strip() if avatar_url_field.value else None,
        }
        try:
            resp = api.update_profile(data)
            if resp.status_code == 200:
                updated_user = resp.json()
                state.set_user(updated_user)
                show_snack("✅ Perfil guardado correctamente en la base de datos")
            else:
                show_snack(resp.json().get("detail", "Error al guardar perfil"), error=True)
        except Exception as ex:
            show_snack(f"Error de conexión: {ex}", error=True)

    def save_settings(e):
        try:
            data = {
                "min_grade": float(min_grade_field.value or 0),
                "max_grade": float(max_grade_field.value or 20),
                "passing_grade": float(passing_grade_field.value or 10),
                "default_eval_count": int(default_evals_field.value or 5),
            }
        except ValueError:
            show_snack("Las notas y cantidad de evaluaciones deben ser números válidos", error=True)
            return

        if data["passing_grade"] < data["min_grade"] or data["passing_grade"] > data["max_grade"]:
            show_snack("La nota para aprobar debe estar entre el mínimo y el máximo", error=True)
            return

        if data["default_eval_count"] < 1 or data["default_eval_count"] > 30:
            show_snack("La cantidad estándar de evaluaciones debe estar entre 1 y 30", error=True)
            return

        try:
            resp = api.update_settings(data)
            if resp.status_code == 200:
                if state.current_user:
                    state.current_user["settings"] = resp.json()
                show_snack("✅ Configuración de escala y evaluaciones actualizada")
            else:
                show_snack(resp.json().get("detail", "Error al guardar escala"), error=True)
        except Exception as ex:
            show_snack(f"Error de conexión: {ex}", error=True)

    # ─── Tarjeta de Datos Personales ────────────────────────────
    personal_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        avatar_preview_container,
                        ft.Column(
                            [
                                ft.Text("Tu Avatar y Datos Personales", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text("Si no especificas foto, se mostrarán tus iniciales reales.", size=12, color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE)),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=18),
                ft.Row([ft.Container(first_name_field, expand=1), ft.Container(last_name_field, expand=1)], spacing=12),
                institution_field,
                student_type_dd,
                avatar_url_field,
                ft.Container(height=4),
                ft.FilledButton(
                    "Guardar Datos de Perfil",
                    icon=ft.Icons.SAVE,
                    on_click=save_profile,
                    style=ft.ButtonStyle(
                        bgcolor=AcademixColors.CYAN_NEON,
                        color=ft.Colors.BLACK,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding(16, 12, 16, 12),
                    ),
                ),
            ],
            spacing=12,
        ),
        padding=24,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
    )

    # ─── Tarjeta de Configuración Académica ─────────────────────
    settings_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon=ft.Icons.TUNE, color=AcademixColors.CYAN_NEON, size=22),
                        ft.Text("Escala de Calificaciones Institucional", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=10,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=18),
                ft.Text(
                    "Define la escala que utiliza tu universidad o liceo y la cantidad habitual de evaluaciones por periodo (lapso, semestre o año).",
                    size=12,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                ),
                ft.Row(
                    [
                        ft.Container(max_grade_field, expand=1),
                        ft.Container(min_grade_field, expand=1),
                    ],
                    spacing=12,
                ),
                ft.Row(
                    [
                        ft.Container(passing_grade_field, expand=1),
                        ft.Container(default_evals_field, expand=1),
                    ],
                    spacing=12,
                ),
                ft.Container(height=4),
                ft.FilledButton(
                    "Guardar Escala Académica",
                    icon=ft.Icons.CHECK,
                    on_click=save_settings,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.25, AcademixColors.CYAN_NEON),
                        color=AcademixColors.CYAN_NEON,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding(16, 12, 16, 12),
                    ),
                ),
            ],
            spacing=12,
        ),
        padding=24,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
    )

    page_title = "Configuración del Sistema ⚙️" if focus_settings else "Mi Perfil 👤"
    page_subtitle = "Ajusta tus parámetros académicos y escala de notas." if focus_settings else "Gestiona tu identidad y credenciales en Académix."

    return ft.Column(
        [
            ft.Text(page_title, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(page_subtitle, size=13, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
            ft.Container(height=16),
            settings_card if focus_settings else personal_card,
            ft.Container(height=8),
            personal_card if focus_settings else settings_card,
        ],
        spacing=0,
    )
