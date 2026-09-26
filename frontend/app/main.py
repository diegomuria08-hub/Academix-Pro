import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from app.theme.colors import get_theme, AcademixColors
from app.core.state import state
from app.screens.login import LoginScreen
from app.screens.register import RegisterScreen

from app.core.api_client import api

def main(page: ft.Page):
    page.title = "Académix Pro"
    page.theme = get_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = AcademixColors.BG_START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.fonts = {"Roboto": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5g.ttf"}

    state.page = page

    # Restaurar sesión persistida (Archivo local privado + ClientStorage)
    try:
        saved_token, saved_user = state.load_session()
        if saved_token:
            api.set_token(saved_token)
            if saved_user:
                state.set_user(saved_user)
            # Validar con el backend en segundo plano sin congelar la app en el arranque
            import threading
            def _validate_session():
                try:
                    me_resp = api.get_me()
                    if me_resp.status_code == 200:
                        state.set_user(me_resp.json())
                    elif me_resp.status_code == 401:
                        state.logout()
                        if page.route not in ["/login", "/register"]:
                            page.navigate("/login")
                except Exception:
                    pass
            threading.Thread(target=_validate_session, daemon=True).start()
    except Exception:
        pass

    def route_change(e):
        current = page.route.strip("/") if page.route else ""

        # Si el Dashboard ya está montado y navegamos entre pestañas internas, cambiar la pestaña al instante (0ms, sin pantalla negra)
        if current in ["dashboard", "calculator", "subjects", "profile", "horario", "notas", "settings"]:
            if not state.current_user:
                page.views.clear()
                page.navigate("/login")
                return

            if hasattr(state, "switch_tab") and callable(state.switch_tab) and len(page.views) > 0 and page.views[-1].route not in ["/login", "/register"]:
                # Si no es la misma ruta, cambiar pestaña
                state.switch_tab(current)
                return

            page.views.clear()
            from app.screens.dashboard import DashboardScreen
            page.views.append(
                ft.View(
                    route=f"/{current}",
                    controls=[DashboardScreen(page, current)],
                    bgcolor=AcademixColors.BG_START,
                    padding=0,
                )
            )
        elif current == "register":
            page.views.clear()
            page.views.append(
                ft.View(
                    route="/register",
                    controls=[RegisterScreen(page)],
                    bgcolor=AcademixColors.BG_START,
                    padding=0,
                )
            )
        else:
            # Login por defecto si no autenticado; si ya está logueado, ir al dashboard
            if state.current_user and current in ["", "login"]:
                page.navigate("/dashboard")
                return
            page.views.append(
                ft.View(
                    route="/login",
                    controls=[LoginScreen(page)],
                    bgcolor=AcademixColors.BG_START,
                    padding=0,
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.navigate(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Navegación inicial inteligente
    init_path = page.route.strip("/") if page.route else ""
    if state.current_user:
        if init_path in ["dashboard", "calculator", "subjects", "profile", "horario", "notas", "settings"]:
            page.navigate(f"/{init_path}")
        else:
            page.navigate("/dashboard")
    else:
        if init_path == "register":
            page.navigate("/register")
        else:
            page.navigate("/login")

if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
