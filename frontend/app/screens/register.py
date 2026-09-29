import flet as ft
from app.core.api_client import api
from app.theme.colors import AcademixColors
from app.theme.copyright import build_copyright_footer


def _glass_input(label: str, hint: str = "", password: bool = False, reveal: bool = False, prefix_icon=None):
    return ft.TextField(
        label=label,
        hint_text=hint,
        password=password,
        can_reveal_password=reveal,
        prefix_icon=prefix_icon,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.1, "#0D1B2A"),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE), size=13),
        cursor_color=AcademixColors.CYAN_NEON,
        border=ft.OutlineInputBorder(
            border_radius=14,
            side=ft.BorderSide(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE), width=1.2),
        ),
        focused_border_color=AcademixColors.CYAN_NEON,
        focused_border_width=2,
        height=52,
    )


def RegisterScreen(page: ft.Page):
    first_name_field = _glass_input("Nombre", prefix_icon=ft.Icons.BADGE_OUTLINED)
    last_name_field  = _glass_input("Apellido", prefix_icon=ft.Icons.BADGE_OUTLINED)
    email_field      = _glass_input("Correo Electrónico", hint="ejemplo@academix.com", prefix_icon=ft.Icons.EMAIL_OUTLINED)
    password_field   = _glass_input("Contraseña", password=True, reveal=True, prefix_icon=ft.Icons.LOCK_OUTLINE)

    student_type = ft.Dropdown(
        label="¿Dónde estudias?",
        options=[
            ft.dropdown.Option("high_school", "🏫  Liceo / Educación Media"),
            ft.dropdown.Option("university",  "🎓  Universidad"),
        ],
        value="high_school",
        filled=True,
        bgcolor="#0F1E36",
        color=ft.Colors.WHITE,
        border=ft.OutlineInputBorder(
            border_radius=14,
            side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.5),
        ),
        label_style=ft.TextStyle(color=AcademixColors.CYAN_NEON, size=13, weight=ft.FontWeight.BOLD),
    )

    error_text = ft.Text("", color=AcademixColors.ERROR, visible=False, size=12, text_align=ft.TextAlign.CENTER)

    def register_click(e):
        error_text.visible = False
        if not email_field.value or not password_field.value or not first_name_field.value:
            error_text.value = "Por favor completa todos los campos requeridos"
            error_text.visible = True
            page.update()
            return

        data = {
            "email": email_field.value,
            "password": password_field.value,
            "first_name": first_name_field.value,
            "last_name": last_name_field.value or "",
            "student_type": student_type.value,
            "institution_name": "",
        }
        try:
            resp = api.register(data)
            if resp.status_code == 201:
                page.navigate("/login")
            else:
                error_text.value = resp.json().get("detail", "Error al registrar")
                error_text.visible = True
                page.update()
        except Exception:
            error_text.value = "Error de conexión con el servidor"
            error_text.visible = True
            page.update()

    # ─── Logo Neón ─────────────────────────────────────────────
    header_logo = ft.Row(
        [
            ft.Container(
                content=ft.Icon(icon=ft.Icons.SCHOOL, color=AcademixColors.CYAN_NEON, size=32),
                shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.65, AcademixColors.CYAN_NEON)),
            ),
            ft.Row(
                [
                    ft.Text("Académix ", size=24, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE),
                    ft.Text("Pro", size=24, weight=ft.FontWeight.W_800, color=AcademixColors.YELLOW_NEON),
                ],
                spacing=0,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
    )

    # ─── Botón con Degradado Púrpura Neón ──────────────────────
    create_btn = ft.Container(
        content=ft.Text("Crear Cuenta", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[AcademixColors.PRIMARY_PURPLE, AcademixColors.PRIMARY],
        ),
        border_radius=16,
        height=48,
        alignment=ft.Alignment.CENTER,
        on_click=register_click,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.with_opacity(0.4, AcademixColors.PRIMARY_PURPLE),
            offset=ft.Offset(0, 6),
        ),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
    )

    card = ft.Container(
        content=ft.Column(
            [
                header_logo,
                ft.Text("Crea tu cuenta", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Accede a tu asistente de notas inteligente", size=12, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                ft.Container(height=4),
                ft.Row([ft.Container(first_name_field, expand=1), ft.Container(last_name_field, expand=1)], spacing=10),
                student_type,
                email_field,
                password_field,
                error_text,
                ft.Container(height=4),
                create_btn,
                ft.Container(height=4),
                ft.Row(
                    [
                        ft.Text("¿Ya tienes una cuenta?", size=12, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                        ft.GestureDetector(
                            content=ft.Text("Inicia sesión", size=12, weight=ft.FontWeight.BOLD, color=AcademixColors.CYAN_NEON),
                            on_tap=lambda _: page.navigate("/login"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=440,
        padding=ft.Padding(32, 32, 32, 28),
        border_radius=22,
        bgcolor=ft.Colors.with_opacity(0.35, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            blur_radius=50,
            color=ft.Colors.with_opacity(0.55, ft.Colors.BLACK),
            offset=ft.Offset(0, 20),
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
                content=ft.Column(
                    [
                        card,
                        ft.Container(height=8),
                        build_copyright_footer(page),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=ft.Padding(0, 16, 0, 16),
            ),
        ],
        expand=True,
    )
