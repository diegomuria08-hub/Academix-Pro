import flet as ft
from app.core.api_client import api
from app.core.state import state
from app.theme.colors import AcademixColors
from app.theme.copyright import build_copyright_footer, open_author_rights_dialog


def _glass_field(label: str, value: str = "", hint_text: str = "", keyboard_type=None, password: bool = False, can_reveal_password: bool = False):
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint_text,
        keyboard_type=keyboard_type,
        password=password,
        can_reveal_password=can_reveal_password,
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
            ft.dropdown.Option("high_school", "🏫  Liceo / Bachillerato"),
            ft.dropdown.Option("university", "🎓  Universidad"),
        ],
        filled=True,
        bgcolor="#0F1E36",
        color=ft.Colors.WHITE,
        border=ft.OutlineInputBorder(
            border_radius=14,
            side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.5),
        ),
        label_style=ft.TextStyle(color=AcademixColors.CYAN_NEON, size=13, weight=ft.FontWeight.BOLD),
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
    # ─── Campos de Configuración Académica ──────────────────────
    min_grade_field = _glass_field("Nota Mínima", value=str(settings_data.get("min_grade", 0.0)), keyboard_type=ft.KeyboardType.NUMBER)
    max_grade_field = _glass_field("Nota Máxima", value=str(settings_data.get("max_grade", 20.0)), keyboard_type=ft.KeyboardType.NUMBER)
    passing_grade_field = _glass_field("Nota para Aprobar", value=str(settings_data.get("passing_grade", 10.0)), keyboard_type=ft.KeyboardType.NUMBER)
    default_evals_field = _glass_field("Evaluaciones por Lapso/Periodo", value=str(settings_data.get("default_eval_count", 4 if profile.get("student_type") == "high_school" else 5)), keyboard_type=ft.KeyboardType.NUMBER, hint_text="Ej: 4")

    total_lapsos_dd = ft.Dropdown(
        label="Cantidad de Lapsos / Periodos Anuales",
        value=str(settings_data.get("total_lapsos", 3)),
        options=[
            ft.dropdown.Option("2", "2 Lapsos / Semestres"),
            ft.dropdown.Option("3", "3 Lapsos (Estándar Liceo Venezuela 🇻🇪)"),
            ft.dropdown.Option("4", "4 Periodos / Trimestres"),
        ],
        filled=True,
        bgcolor="#0F1E36",
        color=ft.Colors.WHITE,
        border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
        label_style=ft.TextStyle(color=AcademixColors.CYAN_NEON, size=12),
    )

    current_lapso_dd = ft.Dropdown(
        label="Lapso Cursando Actualmente",
        value=str(settings_data.get("current_lapso", 1)),
        options=[
            ft.dropdown.Option("1", "Primer Lapso (1)"),
            ft.dropdown.Option("2", "Segundo Lapso (2)"),
            ft.dropdown.Option("3", "Tercer Lapso (3)"),
            ft.dropdown.Option("4", "Cuarto Lapso (4)"),
        ],
        filled=True,
        bgcolor="#0F1E36",
        color=ft.Colors.WHITE,
        border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
        label_style=ft.TextStyle(color=AcademixColors.CYAN_NEON, size=12),
    )

    # ─── Handlers ───────────────────────────────────────────────
    def save_profile(e):
        st_val = student_type_dd.value
        data = {
            "first_name": first_name_field.value.strip() if first_name_field.value else "",
            "last_name": last_name_field.value.strip() if last_name_field.value else "",
            "institution_name": institution_field.value.strip() if institution_field.value else "",
            "student_type": st_val,
            "avatar_url": avatar_url_field.value.strip() if avatar_url_field.value else None,
        }
        try:
            resp = api.update_profile(data)
            if resp.status_code == 200:
                updated_user = resp.json()
                state.set_user(updated_user)
                # Actualizar también modo de evaluación según tipo
                api.update_settings({"evaluation_mode": "liceo" if st_val == "high_school" else "university"})
                show_snack("✅ Perfil y modo académico guardados en la base de datos")
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
                "default_eval_count": int(default_evals_field.value or 4),
                "total_lapsos": int(total_lapsos_dd.value or 3),
                "current_lapso": int(current_lapso_dd.value or 1),
                "evaluation_mode": "liceo" if student_type_dd.value == "high_school" else "university",
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
                show_snack("✅ Escala académica y configuración de lapsos guardada")
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
        padding=18,
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
                        ft.Text("Escala de Calificaciones", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=10,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=14),
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
                    spacing=10,
                ),
                ft.Row(
                    [
                        ft.Container(passing_grade_field, expand=1),
                        ft.Container(default_evals_field, expand=1),
                    ],
                    spacing=10,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=14),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SCHOOL, color=AcademixColors.YELLOW_NEON, size=18),
                        ft.Text("Lapsos Escolares (Liceo / Bachillerato)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "En Venezuela se cursan 3 lapsos por año escolar. Las materias se mantienen todo el año y al culminar los lapsos se calcula la definitiva final.",
                    size=11.5,
                    color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE),
                ),
                ft.Row(
                    [
                        ft.Container(total_lapsos_dd, expand=1),
                        ft.Container(current_lapso_dd, expand=1),
                    ],
                    spacing=10,
                ),
                ft.Container(height=4),
                ft.FilledButton(
                    "Guardar Escala Académica y Lapsos",
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
        padding=18,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
    )

    # ─── Tarjeta de Derechos de Autor & Desarrollador Oficial ───
    author_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon=ft.Icons.VERIFIED_USER_ROUNDED, color=AcademixColors.CYAN_NEON, size=22),
                        ft.Text("Derechos de Autor y Desarrollador Oficial", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=10,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=14),
                ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Text("DM", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, size=14),
                            bgcolor=AcademixColors.CYAN_NEON,
                            radius=20,
                        ),
                        ft.Column(
                            [
                                ft.Text("Diego Muria", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text("Estudiante de Ingeniería de Sistemas", size=12, color=AcademixColors.CYAN_NEON),
                                ft.Text("Instituto Universitario Politécnico Santiago Mariño (IUPSM)", size=11, color=ft.Colors.with_opacity(0.75, ft.Colors.WHITE)),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Text(
                    "Todos los derechos reservados. Esta solución tecnológica y su lógica adaptativa de notas fueron creadas y firmadas por Diego Muria. Sistema anti-copia activo.",
                    size=11,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                ),
                ft.OutlinedButton(
                    "Ver Certificado de Derechos de Autor",
                    icon=ft.Icons.SHIELD_ROUNDED,
                    on_click=lambda _: open_author_rights_dialog(page),
                    style=ft.ButtonStyle(
                        color=AcademixColors.CYAN_NEON,
                        side=ft.BorderSide(1, AcademixColors.CYAN_NEON),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            spacing=10,
        ),
        padding=18,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.2, "#07101C"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.25, AcademixColors.CYAN_NEON)),
    )

    # ─── Tarjeta de Credenciales y Seguridad de Acceso ──────────
    curr_user = state.current_user or {}
    username_val = curr_user.get("username") or curr_user.get("email", "")
    username_field = _glass_field("Nombre de Usuario", value=username_val, hint_text="Ej: Stefania_Martinez")
    email_cred_field = _glass_field("Correo Electrónico", value=curr_user.get("email", ""), hint_text="ejemplo@academix.com")
    password_cred_field = _glass_field("Nueva Contraseña", password=True, hint_text="Déjalo vacío para no cambiar tu contraseña actual")

    def save_credentials(e):
        data = {}
        if username_field.value and username_field.value.strip():
            data["username"] = username_field.value.strip()
        if email_cred_field.value and email_cred_field.value.strip():
            data["email"] = email_cred_field.value.strip()
        if password_cred_field.value and password_cred_field.value.strip():
            data["password"] = password_cred_field.value.strip()

        if not data:
            show_snack("No se especificaron cambios en las credenciales", error=True)
            return

        try:
            resp = api.update_credentials(data)
            if resp.status_code == 200:
                updated_user = resp.json()
                state.set_user(updated_user)
                if api.token:
                    state.save_session(api.token, updated_user)
                password_cred_field.value = ""
                show_snack("✅ Credenciales actualizadas exitosamente en la base de datos")
                page.update()
            else:
                detail = resp.json().get("detail", "Error al actualizar credenciales")
                show_snack(str(detail), error=True)
        except Exception as ex:
            show_snack(f"Error de conexión: {ex}", error=True)

    credentials_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon=ft.Icons.SECURITY_ROUNDED, color=AcademixColors.YELLOW_NEON, size=22),
                        ft.Text("Credenciales y Seguridad de Acceso", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=10,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), height=14),
                ft.Text(
                    "Edita tu nombre de usuario, correo o contraseña en cualquier momento sin afectar tus materias, notas ni horarios.",
                    size=12,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                ),
                username_field,
                email_cred_field,
                password_cred_field,
                ft.Container(height=4),
                ft.FilledButton(
                    "Actualizar Credenciales",
                    icon=ft.Icons.LOCK_RESET,
                    on_click=save_credentials,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.25, AcademixColors.YELLOW_NEON),
                        color=AcademixColors.YELLOW_NEON,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding(16, 12, 16, 12),
                    ),
                ),
            ],
            spacing=12,
        ),
        padding=18,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.22, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.14, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
    )

    page_title = "Configuración del Sistema ⚙️" if focus_settings else "Mi Perfil 👤"
    page_subtitle = "Ajusta tus parámetros académicos y escala de notas." if focus_settings else "Gestiona tu identidad y credenciales en Académix."

    def do_logout(e):
        state.logout()
        page.navigate("/login")

    logout_btn = ft.Container(
        content=ft.OutlinedButton(
            "Cerrar Sesión",
            icon=ft.Icons.LOGOUT,
            on_click=do_logout,
            style=ft.ButtonStyle(
                color=AcademixColors.ERROR,
                side=ft.BorderSide(1.2, ft.Colors.with_opacity(0.5, AcademixColors.ERROR)),
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(16, 10, 16, 10),
            ),
        ),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding(0, 8, 0, 16),
    )

    return ft.Column(
        [
            ft.Text(page_title, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(page_subtitle, size=13, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
            ft.Container(height=16),
            personal_card,
            ft.Container(height=10),
            credentials_card,
            ft.Container(height=10),
            settings_card,
            ft.Container(height=10),
            author_card,
            ft.Container(height=12),
            logout_btn,
            ft.Container(height=8),
            build_copyright_footer(page),
        ],
        spacing=0,
    )
