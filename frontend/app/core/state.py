import os
import json
from app.core.api_client import api

SESSION_FILE_HOME = os.path.join(os.path.expanduser("~"), ".academix_session.json")
SESSION_FILE_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json")

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.current_user = None
            cls._instance.page = None
            cls._instance.cached_subjects = []
        return cls._instance

    def set_user(self, user_data: dict):
        self.current_user = user_data
        # Actualizar archivo de sesión si ya hay token
        if user_data:
            self._update_session_file(user_data=user_data)

    def save_session(self, token: str, user_data: dict = None):
        if user_data:
            self.current_user = user_data
        api.set_token(token)
        
        # 1. Guardar en client_storage (Android SharedPreferences / Web LocalStorage)
        if self.page and hasattr(self.page, "client_storage"):
            try:
                self.page.client_storage.set("token", token)
                if user_data:
                    self.page.client_storage.set("user", user_data)
                self.page.client_storage.set("academix_session", {
                    "token": token,
                    "user": user_data or self.current_user
                })
            except Exception:
                pass

        # 2. Guardar en archivos locales persistentes (redundancia total)
        payload = {"token": token, "user": user_data or self.current_user}
        for path in [SESSION_FILE_HOME, SESSION_FILE_LOCAL]:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
            except Exception:
                pass

    def _update_session_file(self, user_data: dict):
        try:
            token = api.token
            if not token:
                for path in [SESSION_FILE_HOME, SESSION_FILE_LOCAL]:
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            token = data.get("token")
                            if token:
                                break
            if token:
                payload = {"token": token, "user": user_data}
                for path in [SESSION_FILE_HOME, SESSION_FILE_LOCAL]:
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(payload, f)
                    except Exception:
                        pass
            if self.page and hasattr(self.page, "client_storage") and token:
                self.page.client_storage.set("user", user_data)
                self.page.client_storage.set("academix_session", {"token": token, "user": user_data})
        except Exception:
            pass

    def load_session(self) -> tuple:
        """Retorna (token, user_data) persistidos si existen"""
        token = None
        user_data = None

        # 1. Prioridad: client_storage nativo
        if self.page and hasattr(self.page, "client_storage"):
            try:
                token = self.page.client_storage.get("token")
                user_data = self.page.client_storage.get("user")
                if not token:
                    sess = self.page.client_storage.get("academix_session")
                    if sess:
                        if isinstance(sess, str):
                            sess = json.loads(sess)
                        if isinstance(sess, dict):
                            token = sess.get("token")
                            user_data = sess.get("user")
            except Exception:
                pass

        # 2. Fallback: archivos locales redundantes
        if not token:
            for path in [SESSION_FILE_HOME, SESSION_FILE_LOCAL]:
                try:
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            token = data.get("token")
                            user_data = data.get("user")
                            if token:
                                break
                except Exception:
                    pass

        return token, user_data

    def logout(self):
        self.current_user = None
        api.clear_token()
        
        if self.page:
            if hasattr(self.page, "client_storage"):
                try:
                    self.page.client_storage.remove("token")
                    self.page.client_storage.remove("user")
                    self.page.client_storage.remove("academix_session")
                except Exception:
                    pass
            try:
                if hasattr(self.page, "session") and hasattr(self.page.session, "store"):
                    self.page.session.store.remove("token")
            except Exception:
                pass

        for path in [SESSION_FILE_HOME, SESSION_FILE_LOCAL]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
        
state = AppState()
