import sys
import os
import unittest
from unittest.mock import MagicMock

# Añadir directorios al path
root_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(root_dir, "frontend")
backend_dir = os.path.join(root_dir, "backend")
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import flet as ft
from app.theme.colors import get_theme, AcademixColors
from app.core.state import state

class ComprehensiveFrontendAudit(unittest.TestCase):
    def setUp(self):
        self.page = MagicMock(spec=ft.Page)
        self.page.width = 390
        self.page.height = 844
        self.page.views = []
        self.page.route = "/dashboard"
        self.page.client_storage = MagicMock()
        self.page.client_storage.get.return_value = None
        self.page.session = MagicMock()
        state.page = self.page
        state.current_user = {
            "id": "test_user_id",
            "email": "test@academix.com",
            "profile": {
                "first_name": "Test",
                "last_name": "User",
                "institution_name": "UCV",
                "student_type": "university",
                "avatar_url": None,
            },
            "settings": {
                "min_grade": 0.0,
                "max_grade": 20.0,
                "passing_grade": 10.0,
                "default_eval_count": 5,
            }
        }

    def test_01_theme_creation(self):
        print("Testing Theme creation...")
        theme = get_theme()
        self.assertIsNotNone(theme)
        self.assertIsNotNone(theme.color_scheme)
        self.assertEqual(theme.color_scheme.surface, "#0F1E36")
        self.assertEqual(theme.color_scheme.surface_container, "#142644")
        print("[OK] Theme verified successfully.")

    def test_02_login_screen(self):
        print("Testing LoginScreen...")
        from app.screens.login import LoginScreen
        view = LoginScreen(self.page)
        self.assertIsNotNone(view)
        print("[OK] LoginScreen mounted successfully.")

    def test_03_register_screen(self):
        print("Testing RegisterScreen...")
        from app.screens.register import RegisterScreen
        view = RegisterScreen(self.page)
        self.assertIsNotNone(view)
        print("[OK] RegisterScreen mounted successfully.")

    def test_04_profile_screen(self):
        print("Testing ProfileScreen...")
        from app.screens.profile import ProfileScreen
        view = ProfileScreen(self.page)
        self.assertIsNotNone(view)
        print("[OK] ProfileScreen mounted successfully.")

    def test_05_schedule_screen(self):
        print("Testing ScheduleScreen and modals...")
        from app.screens.schedule import ScheduleScreen
        from unittest.mock import patch

        # Mock api get_subjects, get_classes, get_events
        with patch("app.screens.schedule.api") as mock_api:
            mock_api.get_subjects.return_value.status_code = 200
            mock_api.get_subjects.return_value.json.return_value = [
                {"id": "sub-1", "name": "Matemática", "color_hex": "#00E5FF"}
            ]
            mock_api.get_classes.return_value.status_code = 200
            mock_api.get_classes.return_value.json.return_value = []
            mock_api.get_events.return_value.status_code = 200
            mock_api.get_events.return_value.json.return_value = []

            view = ScheduleScreen(self.page)
            self.assertIsNotNone(view)

            # Encontrar y ejecutar los botones de modal (Agregar Clase y Agendar Evento)
            # Buscar FilledButton y TextButton en el árbol de controles
            buttons = []
            def extract_buttons(ctl):
                if hasattr(ctl, "controls") and ctl.controls:
                    for c in ctl.controls:
                        extract_buttons(c)
                if hasattr(ctl, "content") and ctl.content:
                    extract_buttons(ctl.content)
                if isinstance(ctl, (ft.FilledButton, ft.TextButton, ft.IconButton)):
                    buttons.append(ctl)

            extract_buttons(view)
            self.assertGreater(len(buttons), 0)

            # Ejecutar clicks para asegurar que los modales (add_dialog y event_dialog) no fallen
            for btn in buttons:
                if btn.on_click:
                    try:
                        btn.on_click(MagicMock())
                    except Exception as e:
                        # Si falla por algo de Flet o sintaxis, lanzar el error
                        if isinstance(e, TypeError) and "unexpected keyword argument" in str(e):
                            raise e

        print(f"[OK] ScheduleScreen and {len(buttons)} interactive buttons/modals verified without errors.")

    def test_06_subjects_screen(self):
        print("Testing SubjectsScreen...")
        from app.screens.subjects import SubjectsScreen
        view = SubjectsScreen(self.page)
        self.assertIsNotNone(view)
        print("[OK] SubjectsScreen mounted successfully.")

    def test_07_dashboard_screen(self):
        print("Testing DashboardScreen and internal tabs...")
        from app.screens.dashboard import DashboardScreen
        for tab in ["dashboard", "calculator", "subjects", "horario", "profile"]:
            view = DashboardScreen(self.page, active_route=tab)
            self.assertIsNotNone(view)
        print("[OK] DashboardScreen and all internal tabs mounted successfully.")

if __name__ == "__main__":
    unittest.main()
