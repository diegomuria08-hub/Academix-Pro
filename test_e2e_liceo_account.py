import os
import sys
import uuid

root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_liceo_flow():
    # 1. Crear cuenta de prueba de Liceo
    test_id = str(uuid.uuid4())[:8]
    test_email = f"estudiante_liceo_{test_id}@academix.com"
    test_pass = "Password123!"

    print(f"[*] Registrando usuario de Liceo: {test_email}...")
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": test_pass,
        "first_name": "Pedro",
        "last_name": "Perez",
        "student_type": "high_school",
        "institution_name": "Liceo Bolivariano"
    })
    assert reg_resp.status_code == 201, f"Fallo al registrar: {reg_resp.text}"
    user_data = reg_resp.json()
    print("[OK] Usuario registrado con éxito.")

    # 2. Login
    print("[*] Iniciando sesión...")
    login_resp = client.post("/api/v1/auth/login", data={
        "username": test_email,
        "password": test_pass
    })
    assert login_resp.status_code == 200, f"Fallo al hacer login: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Sesión iniciada y token JWT obtenido.")

    # 3. Verificar Me y Settings de Liceo
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["profile"]["student_type"] == "high_school"
    assert me_data["settings"]["evaluation_mode"] == "liceo"
    assert me_data["settings"]["total_lapsos"] == 3
    assert me_data["settings"]["current_lapso"] == 1
    print(f"[OK] Configuración verificada: total_lapsos={me_data['settings']['total_lapsos']}, mode={me_data['settings']['evaluation_mode']}.")

    # 4. Crear Materia
    sub_resp = client.post("/api/v1/academic/subjects", headers=headers, json={
        "name": "Matemática",
        "credits": 4,
        "color_hex": "#00E5FF"
    })
    assert sub_resp.status_code == 201, f"Fallo al crear materia: {sub_resp.text}"
    subject_id = sub_resp.json()["id"]
    print(f"[OK] Materia 'Matemática' creada con ID: {subject_id}")

    # 5. Registrar Evaluaciones en Lapsos 1, 2 y 3
    # Lapso 1: Examen 1 (50%, nota 18), Examen 2 (50%, nota 16) -> Promedio L1 = 17.0
    client.post(f"/api/v1/academic/subjects/{subject_id}/evaluations", headers=headers, json={
        "name": "Examen 1 - L1",
        "weight_percent": 50.0,
        "eval_type": "exam",
        "lapso_number": 1,
        "score": 18.0
    })
    client.post(f"/api/v1/academic/subjects/{subject_id}/evaluations", headers=headers, json={
        "name": "Examen 2 - L1",
        "weight_percent": 50.0,
        "eval_type": "exam",
        "lapso_number": 1,
        "score": 16.0
    })

    # Lapso 2: Taller (50%, nota 14), Examen (50%, nota 20) -> Promedio L2 = 17.0
    client.post(f"/api/v1/academic/subjects/{subject_id}/evaluations", headers=headers, json={
        "name": "Taller - L2",
        "weight_percent": 50.0,
        "eval_type": "homework",
        "lapso_number": 2,
        "score": 14.0
    })
    client.post(f"/api/v1/academic/subjects/{subject_id}/evaluations", headers=headers, json={
        "name": "Examen - L2",
        "weight_percent": 50.0,
        "eval_type": "exam",
        "lapso_number": 2,
        "score": 20.0
    })

    # Lapso 3: Proyecto (100%, nota 15) -> Promedio L3 = 15.0
    client.post(f"/api/v1/academic/subjects/{subject_id}/evaluations", headers=headers, json={
        "name": "Proyecto Final - L3",
        "weight_percent": 100.0,
        "eval_type": "project",
        "lapso_number": 3,
        "score": 15.0
    })
    print("[OK] Evaluaciones creadas para los 3 lapsos.")

    # 6. Consultar Materias y verificar Lapsos y Definitiva Anual
    subjects_resp = client.get("/api/v1/academic/subjects", headers=headers)
    assert subjects_resp.status_code == 200
    sub_data = subjects_resp.json()[0]

    assert sub_data["lapsos_summary"] is not None
    assert len(sub_data["lapsos_summary"]) == 3
    l1 = sub_data["lapsos_summary"][0]
    l2 = sub_data["lapsos_summary"][1]
    l3 = sub_data["lapsos_summary"][2]

    print(f"[OK] L1: {l1['accumulated_points']} pts | L2: {l2['accumulated_points']} pts | L3: {l3['accumulated_points']} pts")
    assert l1["accumulated_points"] == 17.0
    assert l2["accumulated_points"] == 17.0
    assert l3["accumulated_points"] == 15.0

    # Definitiva Anual: (17 + 17 + 15) / 3 = 49 / 3 = 16.33 pts
    print(f"[OK] Definitiva Anual calculada en BD: {sub_data['annual_definitiva']} / 20 pts")
    assert sub_data["annual_definitiva"] == 16.33

    # 7. Consultar Estadísticas Generales (Dashboard)
    stats_resp = client.get("/api/v1/academic/stats", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    print(f"[OK] Stats Dashboard -> student_type={stats['student_type']}, annual_gpa={stats['annual_gpa']}")
    assert stats["student_type"] == "high_school"
    assert stats["annual_gpa"] == 16.33
    assert stats["active_subjects_count"] == 1

    print("\n>>> ¡TODO EL FLUJO DE ESTUDIANTE DE LICEO FUNCIONA A LA PERFECCIÓN! <<<")

if __name__ == "__main__":
    test_full_liceo_flow()
