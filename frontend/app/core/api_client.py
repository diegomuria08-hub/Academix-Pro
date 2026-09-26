import httpx
from typing import Optional

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

class ApiClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ApiClient, cls).__new__(cls)
            cls._instance.client = httpx.Client(base_url=API_BASE_URL, timeout=10.0)
            cls._instance.token = None
        return cls._instance

    def set_token(self, token: str):
        self.token = token
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    def clear_token(self):
        self.token = None
        if "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]

    def login(self, email: str, password: str):
        return self.client.post("/auth/login", data={"username": email, "password": password})

    def register(self, data: dict):
        return self.client.post("/auth/register", json=data)

    def get_me(self):
        return self.client.get("/auth/me")

    # Métodos de Perfil (Fase 6)
    def update_profile(self, data: dict):
        return self.client.put("/users/me/profile", json=data)

    def get_settings(self):
        return self.client.get("/users/me/settings")

    def update_settings(self, data: dict):
        return self.client.put("/users/me/settings", json=data)

    # Métodos Académicos y Calificaciones (CRUD)
    def get_stats(self):
        return self.client.get("/academic/stats")

    def get_subjects(self):
        return self.client.get("/academic/subjects")

    def create_subject(self, data: dict):
        return self.client.post("/academic/subjects", json=data)

    def update_subject(self, subject_id: str, data: dict):
        return self.client.put(f"/academic/subjects/{subject_id}", json=data)

    def delete_subject(self, subject_id: str):
        return self.client.delete(f"/academic/subjects/{subject_id}")

    def create_evaluation(self, subject_id: str, data: dict):
        return self.client.post(f"/academic/subjects/{subject_id}/evaluations", json=data)

    def update_evaluation(self, eval_id: str, data: dict):
        return self.client.put(f"/academic/evaluations/{eval_id}", json=data)

    def delete_evaluation(self, eval_id: str):
        return self.client.delete(f"/academic/evaluations/{eval_id}")

    # Métodos de Horario de Clases y Agenda Académica
    def get_classes(self):
        return self.client.get("/schedule/classes")

    def create_class(self, data: dict):
        return self.client.post("/schedule/classes", json=data)

    def update_class(self, sched_id: str, data: dict):
        return self.client.put(f"/schedule/classes/{sched_id}", json=data)

    def delete_class(self, sched_id: str):
        return self.client.delete(f"/schedule/classes/{sched_id}")

    def get_events(self):
        return self.client.get("/schedule/events")

    def create_event(self, data: dict):
        return self.client.post("/schedule/events", json=data)

    def delete_event(self, event_id: str):
        return self.client.delete(f"/schedule/events/{event_id}")

    # Métodos de Calculadora Predictiva de Notas
    def simulate_grade(self, data: dict):
        return self.client.post("/academic/calculator/simulate", json=data)

    def get_prediction_history(self, limit: int = 10):
        return self.client.get(f"/academic/calculator/history?limit={limit}")

api = ApiClient()
