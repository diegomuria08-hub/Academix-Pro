import os
import json
from app.core.api_client import api

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".academix_session.json")

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.current_user = None
            cls._instance.page = None
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
        
        # 1. Guardar en client_storage si está disponible
        if self.page:
            try:
                self.page.client_storage.set("token", token)
                if user_data:
                    self.page.client_storage.set("user", user_data)
            except Exception:
                pass

        # 2. Guardar en archivo local persistente (inmune a cierres de app en Android)
        try:
            payload = {"token": token, "user": user_data or self.current_user}
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f)
        except Exception:
            pass

    def _update_session_file(self, user_data: dict):
        try:
            token = api.token
            if not token and os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    token = data.get("token")
            if token:
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    json.dump({"token": token, "user": user_data}, f)
        except Exception:
            pass

    def load_session(self) -> tuple:
        """Retorna (token, user_data) persistidos si existen"""
        token = None
        user_data = None

        # 1. Intentar archivo local persistente
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    token = data.get("token")
                    user_data = data.get("user")
        except Exception:
            pass

        # 2. Intentar client_storage si el archivo local no tenía el token
        if not token and self.page:
            try:
                token = self.page.client_storage.get("token")
                user_data = self.page.client_storage.get("user")
            except Exception:
                pass

        return token, user_data

    def logout(self):
        self.current_user = None
        api.clear_token()
        
        if self.page:
            try:
                self.page.client_storage.remove("token")
                self.page.client_storage.remove("user")
            except Exception:
                pass
            try:
                self.page.session.store.remove("token")
            except Exception:
                pass

        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except Exception:
            pass
        
state = AppState()
