import flet as ft
from app.theme.colors import AcademixColors

AUTHOR_NAME = "Diego Muria"
AUTHOR_DEGREE = "Ingeniería de Sistemas"
AUTHOR_INSTITUTE = "Instituto Universitario Politécnico Santiago Mariño (IUPSM)"
COPYRIGHT_TEXT = "Derechos reservados para Diego Muria, estudiante de Ingeniería de Sistemas del IUPSM"
ANTI_COPY_NOTICE = "Propiedad Intelectual Protegida © 2026 • Prohibida la reproducción total o parcial sin autorización del autor."

def open_author_rights_dialog(page: ft.Page):
    """Muestra el Certificado Oficial de Propiedad Intelectual y Derechos de Autor."""
    dialog = ft.AlertDialog(
        modal=True,
        bgcolor="#0B132B",
        title=ft.Row(
            [
                ft.Icon(ft.Icons.VERIFIED_USER_ROUNDED, color=AcademixColors.CYAN_NEON, size=24),
                ft.Text("Derechos de Autor & Propiedad Intelectual", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ],
            spacing=10,
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.CircleAvatar(
                                    content=ft.Text("DM", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, size=16),
                                    bgcolor=AcademixColors.CYAN_NEON,
                                    radius=24,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(AUTHOR_NAME, weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.WHITE),
                                        ft.Text(f"Estudiante de {AUTHOR_DEGREE}", size=12, color=AcademixColors.CYAN_NEON),
                                        ft.Text(AUTHOR_INSTITUTE, size=11, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                        padding=12,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.2, "#1C2541"),
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, AcademixColors.CYAN_NEON)),
                    ),
                    ft.Text(
                        "Certificado de Autoría y Licencia de Software:",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        "Esta aplicación (Académix Pro), su arquitectura tecnológica, diseño visual "
                        "y su motor adaptativo de cálculo de calificaciones por lapsos y semestres "
                        "han sido desarrollados de manera original y exclusiva por Diego Muria.",
                        size=12,
                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.SHIELD_ROUNDED, color=AcademixColors.PRIMARY_PURPLE, size=18),
                                ft.Text(
                                    "Seguridad Anti-Copia: Todos los derechos reservados. Prohibida la copia o duplicación de esta solución.",
                                    size=11,
                                    color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                                    expand=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=10,
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.15, AcademixColors.PRIMARY_PURPLE),
                    ),
                    ft.Text(
                        "Firma Digital Verificada: IUPSM-SYS-2026-DM-PRO",
                        size=10,
                        font_family="monospace",
                        color=AcademixColors.CYAN_NEON,
                    ),
                ],
                spacing=12,
                tight=True,
            ),
            width=360,
            padding=10,
        ),
        actions=[
            ft.TextButton(
                "Entendido",
                on_click=lambda _: page.pop_dialog(),
                style=ft.ButtonStyle(color=AcademixColors.CYAN_NEON),
            )
        ],
    )
    page.show_dialog(dialog)

def build_copyright_footer(page: ft.Page, is_compact: bool = False):
    """
    Footer 100% responsivo y Mobile-First que presenta los derechos reservados
    de Diego Muria organizados coherentemente uno debajo de otro para evitar cualquier
    desbordamiento de pantalla en cualquier dispositivo móvil o tablet.
    """
    if is_compact:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.VERIFIED_ROUNDED, color=AcademixColors.CYAN_NEON, size=12),
                            ft.Text(
                                "Derechos reservados — Diego Muria",
                                size=10,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    ft.Text(
                        "Ing. de Sistemas IUPSM • © 2026",
                        size=9,
                        color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(4, 6, 4, 6),
            on_click=lambda _: open_author_rights_dialog(page),
            tooltip="Ver certificado de derechos de autor de Diego Muria",
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.VERIFIED_USER_ROUNDED, color=AcademixColors.CYAN_NEON, size=13),
                        ft.Text(
                            "Derechos reservados para Diego Muria",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                ft.Text(
                    "Estudiante de Ingeniería de Sistemas — IUPSM",
                    size=10,
                    weight=ft.FontWeight.W_500,
                    color=AcademixColors.CYAN_NEON,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Académix Pro © 2026 • Propiedad Intelectual Protegida",
                    size=8.5,
                    color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(6, 8, 6, 8),
        alignment=ft.Alignment.CENTER,
        on_click=lambda _: open_author_rights_dialog(page),
        tooltip="Haz clic para ver el certificado de autoría y derechos reservados",
    )

def build_author_sidebar_card(page: ft.Page):
    """Tarjeta de Desarrollador Oficial para el sidebar de escritorio."""
    return ft.Container(
        content=ft.Row(
            [
                ft.CircleAvatar(
                    content=ft.Text("DM", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    bgcolor=AcademixColors.CYAN_NEON,
                    radius=14,
                ),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Diego Muria", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Icon(ft.Icons.VERIFIED_ROUNDED, size=12, color=AcademixColors.CYAN_NEON),
                            ],
                            spacing=3,
                        ),
                        ft.Text("Ing. Sistemas IUPSM", size=9.5, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                        ft.Text("Derechos Reservados", size=8.5, color=AcademixColors.CYAN_NEON),
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(10, 8, 10, 8),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.18, "#0D1B2A"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, AcademixColors.CYAN_NEON)),
        on_click=lambda _: open_author_rights_dialog(page),
        tooltip="Autor Oficial: Diego Muria (IUPSM)",
    )
