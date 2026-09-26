from app.core.api_client import api

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

    def logout(self):
        self.current_user = None
        api.clear_token()
        if self.page:
            try:
                self.page.client_storage.remove("token")
            except Exception:
                pass
            try:
                self.page.session.store.remove("token")
            except Exception:
                pass
        
state = AppState()
