import flet as ft
from app.core.api_client import api
from app.core.state import state
from app.theme.colors import AcademixColors


def LoginScreen(page: ft.Page):
    # ─── Campos de entrada Glassmorphism ────────────────────────
    email_field = ft.TextField(
        label="Usuario o Correo Electrónico",
        hint_text="ejemplo@universidad.edu o usuario",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.12, "#0D1B2A"),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE), size=13),
        cursor_color=AcademixColors.CYAN_NEON,
        border=ft.OutlineInputBorder(
            border_radius=16,
            side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.6),
        ),
        focused_border_color=AcademixColors.CYAN_GLOW,
        focused_border_width=2,
        height=54,
    )

    password_field = ft.TextField(
        label="Contraseña",
        hint_text="••••••••",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        filled=True,
        bgcolor=ft.Colors.with_opacity(0.08, "#0D1B2A"),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), size=13),
        cursor_color=AcademixColors.CYAN_NEON,
        border=ft.OutlineInputBorder(
            border_radius=16,
            side=ft.BorderSide(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE), width=1.2),
        ),
        focused_border_color=AcademixColors.CYAN_NEON,
        focused_border_width=2,
        height=54,
    )

    error_text = ft.Text("", color=AcademixColors.ERROR, visible=False, size=12, text_align=ft.TextAlign.CENTER)
    loading_indicator = ft.ProgressRing(width=20, height=20, stroke_width=2.5, color=ft.Colors.WHITE, visible=False)

    login_button_content = ft.Row(
        [
            loading_indicator,
            ft.Text("Iniciar Sesión", size=15, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    def do_login(e):
        error_text.visible = False
        if not email_field.value or not password_field.value:
            error_text.value = "Por favor completa todos los campos"
            error_text.visible = True
            page.update()
            return

        loading_indicator.visible = True
        page.update()

        try:
            resp = api.login(email_field.value.strip(), password_field.value)
            if resp.status_code == 200:
                data = resp.json()
                token = data["access_token"]
                me_data = None
                try:
                    api.set_token(token)
                    me_resp = api.get_me()
                    if me_resp.status_code == 200:
                        me_data = me_resp.json()
                except Exception:
                    pass
                
                # Persistencia permanente reforzada
                state.save_session(token, me_data)
                page.navigate("/dashboard")
            elif resp.status_code in (400, 401):
                error_text.value = "Usuario o contraseña incorrectos"
                error_text.visible = True
            else:
                error_text.value = f"Error del servidor ({resp.status_code}). Intenta de nuevo."
                error_text.visible = True
        except Exception as ex:
            ex_str = str(ex).lower()
            if "timeout" in ex_str:
                error_text.value = "El servidor está iniciando (Render despierta tras reposo). Espera unos 15 segundos y reintenta."
            elif "connect" in ex_str or "network" in ex_str:
                error_text.value = "Error de red. Verifica tu conexión a internet."
            else:
                error_text.value = "Error al conectar con el servidor. Reintentando..."
            error_text.visible = True
        finally:
            loading_indicator.visible = False
            page.update()

    # ─── Logo Birrete Neón Superior ────────────────────────────
    header_logo = ft.Row(
        [
            ft.Container(
                content=ft.Icon(icon=ft.Icons.SCHOOL, color=AcademixColors.CYAN_NEON, size=34),
                shadow=ft.BoxShadow(
                    blur_radius=18,
                    color=ft.Colors.with_opacity(0.65, AcademixColors.CYAN_NEON),
                ),
            ),
            ft.Row(
                [
                    ft.Text("Académix ", size=26, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE),
                    ft.Text(
                        "Pro",
                        size=26,
                        weight=ft.FontWeight.W_800,
                        color=AcademixColors.YELLOW_NEON,
                        style=ft.TextStyle(
                            shadow=ft.BoxShadow(
                                blur_radius=14,
                                color=ft.Colors.with_opacity(0.6, AcademixColors.YELLOW_NEON),
                            )
                        ),
                    ),
                ],
                spacing=0,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    # ─── Botón con Degradado Púrpura/Índigo Neón ────────────────
    login_btn = ft.Container(
        content=login_button_content,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[AcademixColors.PRIMARY_PURPLE, AcademixColors.PRIMARY],
        ),
        border_radius=16,
        height=48,
        alignment=ft.Alignment.CENTER,
        on_click=do_login,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.with_opacity(0.45, AcademixColors.PRIMARY_PURPLE),
            offset=ft.Offset(0, 6),
        ),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
    )

    def show_snack(msg: str, error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.WHITE, size=13),
            bgcolor=AcademixColors.ERROR if error else AcademixColors.SUCCESS,
            duration=3500,
        )
        if hasattr(page, "open"):
            page.open(snack)
        else:
            page.snack_bar = snack
            snack.open = True
            page.update()

    def open_recovery_dialog(e):
        rec_error = ft.Text("", color=AcademixColors.ERROR, size=12, visible=False)
        rec_ident = ft.TextField(
            label="Correo o Nombre de Usuario",
            hint_text="Ej: Stefania_Martinez o correo",
            filled=True,
            bgcolor="#0F1E36",
            color=ft.Colors.WHITE,
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
        )
        rec_new_pass = ft.TextField(
            label="Nueva Contraseña",
            password=True,
            can_reveal_password=True,
            hint_text="Mínimo 4 caracteres",
            filled=True,
            bgcolor="#0F1E36",
            color=ft.Colors.WHITE,
            border=ft.OutlineInputBorder(border_radius=12, side=ft.BorderSide(color=AcademixColors.CYAN_NEON, width=1.2)),
        )

        def submit_recovery(ev):
            rec_error.visible = False
            ident = rec_ident.value.strip() if rec_ident.value else ""
            new_p = rec_new_pass.value.strip() if rec_new_pass.value else ""
            if not ident or not new_p:
                rec_error.value = "Por favor completa ambos campos"
                rec_error.visible = True
                page.update()
                return

            try:
                resp = api.recover_account(ident, new_p)
                if resp.status_code == 200:
                    page.pop_dialog()
                    data = resp.json()
                    user_found = data.get("username") or data.get("email") or ident
                    email_field.value = user_found
                    password_field.value = new_p
                    show_snack("✅ ¡Contraseña restablecida con éxito! Ya puedes iniciar sesión.")
                    page.update()
                else:
                    detail = resp.json().get("detail", "Error al recuperar cuenta")
                    rec_error.value = str(detail)
                    rec_error.visible = True
                    page.update()
            except Exception as ex:
                rec_error.value = f"Error de conexión: {ex}"
                rec_error.visible = True
                page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.LOCK_RESET_ROUNDED, color=AcademixColors.CYAN_NEON, size=22),
                    ft.Text("Recuperar Cuenta", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=18),
                ],
                spacing=8,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        rec_error,
                        ft.Text(
                            "Ingresa tu nombre de usuario o correo junto con tu nueva clave para recuperar tu acceso.",
                            size=12,
                            color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        ),
                        rec_ident,
                        rec_new_pass,
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.ADAPTIVE,
                ),
                width=330,
                height=260,
                padding=6,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.FilledButton(
                    "Restablecer",
                    on_click=submit_recovery,
                    style=ft.ButtonStyle(
                        bgcolor=AcademixColors.CYAN_NEON,
                        color=ft.Colors.BLACK,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
        )
        page.show_dialog(dlg)

    # ─── Tarjeta Central Flotante de Vidrio (Glassmorphism) ─────
    glass_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Bienvenido", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=4),
                email_field,
                # Enlace 'Continuar' en amarillo neón como en la imagen
                ft.Container(
                    content=ft.Text(
                        "Continuar",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=AcademixColors.YELLOW_NEON,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding(0, 2, 0, 4),
                ),
                password_field,
                ft.Container(
                    content=ft.TextButton(
                        "¿Olvidaste tu contraseña o usuario?",
                        on_click=open_recovery_dialog,
                        style=ft.ButtonStyle(
                            color=AcademixColors.CYAN_NEON,
                            padding=ft.Padding(0, 0, 0, 0),
                        ),
                    ),
                    alignment=ft.Alignment.CENTER_RIGHT,
                    padding=ft.Padding(0, 2, 0, 2),
                ),
                ft.Container(height=4),
                login_btn,
                error_text,
                ft.Container(height=2),
                # Enlace a Registro
                ft.Row(
                    [
                        ft.Text(
                            "Registro: ",
                            size=12,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                        ),
                        ft.GestureDetector(
                            content=ft.Text(
                                "Iniciar cuenta",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=AcademixColors.CYAN_NEON,
                            ),
                            on_tap=lambda _: page.navigate("/register"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=2,
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=380,
        padding=ft.Padding(left=32, right=32, top=36, bottom=32),
        border_radius=22,
        bgcolor=ft.Colors.with_opacity(0.35, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            blur_radius=50,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.55, ft.Colors.BLACK),
            offset=ft.Offset(0, 20),
        ),
    )

    # ─── Resplandores suaves de fondo (Acentos de neón) ─────────
    orb_cyan = ft.Container(
        width=320,
        height=320,
        border_radius=160,
        gradient=ft.RadialGradient(
            center=ft.Alignment.CENTER,
            radius=1.0,
            colors=[
                ft.Colors.with_opacity(0.18, AcademixColors.CYAN_NEON),
                ft.Colors.with_opacity(0.0, AcademixColors.BG_START),
            ],
        ),
        top=-50,
        left=-50,
    )

    orb_purple = ft.Container(
        width=320,
        height=320,
        border_radius=160,
        gradient=ft.RadialGradient(
            center=ft.Alignment.CENTER,
            radius=1.0,
            colors=[
                ft.Colors.with_opacity(0.18, AcademixColors.PRIMARY_PURPLE),
                ft.Colors.with_opacity(0.0, AcademixColors.BG_START),
            ],
        ),
        bottom=-50,
        right=-50,
    )

    return ft.Stack(
        [
            # Fondo Degradado Azul Marino Profundo
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=[AcademixColors.BG_START, AcademixColors.BG_END],
                ),
            ),
            orb_cyan,
            orb_purple,
            ft.Container(
                content=ft.Column(
                    [
                        header_logo,
                        ft.Container(height=18),
                        glass_card,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
        ],
        expand=True,
    )
