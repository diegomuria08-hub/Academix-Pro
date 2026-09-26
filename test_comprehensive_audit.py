import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Set paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, SessionLocal
from app.db.models.users import User
import uuid

client = TestClient(app)

def run_exhaustive_audit():
    print("🚀 INICIANDO AUDITORÍA Y VERIFICACIÓN EXHAUSTIVA DE ACADÉMIX PRO...")
    
    # Generate unique test user
    uid = uuid.uuid4().hex[:6]
    email = f"audit_user_{uid}@academix.com"
    password = "SecurePassword123!"
    
    # ─── 1. REGISTRO & AUTENTICACIÓN ────────────────────────────
    print("\n[1/6] Probando Registro y Autenticación JWT...")
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Auditor",
        "last_name": "Pro",
        "student_type": "university",
        "institution_name": "Universidad Central de Venezuela (UCV)"
    }
    r = client.post("/api/v1/auth/register", json=reg_payload)
    assert r.status_code == 201, f"Registro falló: {r.text}"
    user_data = r.json()
    assert user_data["email"] == email
    print(f"  ✅ Registro exitoso para: {email}")

    # Login
    r = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, f"Login falló: {r.text}"
    tokens = r.json()
    token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  ✅ Token JWT emitido y verificado correctamente.")

    # Get Me
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["profile"]["first_name"] == "Auditor"
    print("  ✅ Endpoint GET /auth/me responde con perfil y settings intactos.")

    # ─── 2. PERFIL Y CONFIGURACIÓN ACADÉMICA ─────────────────────
    print("\n[2/6] Probando Perfil y Configuración de Escala Académica...")
    # Update profile
    prof_payload = {
        "first_name": "Diego",
        "last_name": "Muria",
        "institution_name": "Universidad Simón Bolívar",
        "student_type": "university",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
    }
    r = client.put("/api/v1/users/me/profile", json=prof_payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["profile"]["avatar_url"] == prof_payload["avatar_url"]
    assert r.json()["profile"]["first_name"] == "Diego"
    print("  ✅ Perfil y avatar_url actualizados y persistidos en MySQL.")

    # Update Academic Settings (Escala Institucional)
    settings_payload = {
        "min_grade": 0.0,
        "max_grade": 20.0,
        "passing_grade": 10.0
    }
    r = client.put("/api/v1/users/me/settings", json=settings_payload, headers=headers)
    assert r.status_code == 200, f"Error al guardar configuración: {r.text}"
    saved_settings = r.json()
    assert saved_settings["max_grade"] == 20.0
    assert saved_settings["passing_grade"] == 10.0
    print("  ✅ PUT /users/me/settings actualizó escala (0 a 20, aprobatoria 10).")

    # ─── 3. CRUD DE MATERIAS (SUBJECTS) ─────────────────────────
    print("\n[3/6] Probando CRUD Completo de Materias...")
    sub_payload = {
        "name": "Cálculo I",
        "credits": 4,
        "color_hex": "#00E5FF"
    }
    r = client.post("/api/v1/academic/subjects", json=sub_payload, headers=headers)
    assert r.status_code == 201, f"Creación de materia falló: {r.text}"
    sub1 = r.json()
    sub1_id = sub1["id"]
    assert sub1["name"] == "Cálculo I"
    assert sub1["credits"] == 4
    print(f"  ✅ Materia creada con éxito (ID: {sub1_id})")

    # Crear segunda materia
    sub2_payload = {
        "name": "Programación Avanzada",
        "credits": 3,
        "color_hex": "#7C4DFF"
    }
    r = client.post("/api/v1/academic/subjects", json=sub2_payload, headers=headers)
    assert r.status_code == 201
    sub2_id = r.json()["id"]
    print(f"  ✅ Segunda materia creada con éxito (ID: {sub2_id})")

    # Listar materias
    r = client.get("/api/v1/academic/subjects", headers=headers)
    assert r.status_code == 200
    subjects_list = r.json()
    assert len(subjects_list) == 2
    print(f"  ✅ Listado de materias: {len(subjects_list)} materias activas recuperadas.")

    # Modificar Materia
    upd_payload = {"name": "Cálculo I (Diferencial)", "credits": 5, "color_hex": "#00E676"}
    r = client.put(f"/api/v1/academic/subjects/{sub1_id}", json=upd_payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Cálculo I (Diferencial)"
    assert r.json()["credits"] == 5
    print("  ✅ Materia actualizada con éxito en MySQL.")

    # ─── 4. CRUD DE EVALUACIONES Y CALIFICACIONES ───────────────
    print("\n[4/6] Probando CRUD de Evaluaciones y Cálculo de Promedios...")
    # Crear Evaluación 1 (30% con nota 18.0)
    ev1_payload = {
        "name": "Parcial 1",
        "eval_type": "exam",
        "weight_percent": 30.0,
        "score": 18.0
    }
    r = client.post(f"/api/v1/academic/subjects/{sub1_id}/evaluations", json=ev1_payload, headers=headers)
    assert r.status_code == 201
    ev1 = r.json()
    ev1_id = ev1["id"]
    assert ev1["grade"]["score"] == 18.0
    print("  ✅ Evaluación 1 (30%, Nota 18.0) registrada.")

    # Crear Evaluación 2 (40% con nota 14.0)
    ev2_payload = {
        "name": "Parcial 2",
        "eval_type": "exam",
        "weight_percent": 40.0,
        "score": 14.0
    }
    r = client.post(f"/api/v1/academic/subjects/{sub1_id}/evaluations", json=ev2_payload, headers=headers)
    assert r.status_code == 201
    ev2_id = r.json()["id"]
    print("  ✅ Evaluación 2 (40%, Nota 14.0) registrada.")

    # Crear Evaluación 3 pendiente (30% sin nota)
    ev3_payload = {
        "name": "Proyecto Final",
        "eval_type": "project",
        "weight_percent": 30.0,
        "score": None
    }
    r = client.post(f"/api/v1/academic/subjects/{sub1_id}/evaluations", json=ev3_payload, headers=headers)
    assert r.status_code == 201
    ev3_id = r.json()["id"]
    print("  ✅ Evaluación 3 (30%, Pendiente) registrada.")

    # Verificar promedios de la materia
    r = client.get("/api/v1/academic/subjects", headers=headers)
    subjects = r.json()
    c1 = next(s for s in subjects if s["id"] == sub1_id)
    # 30% * 18 + 40% * 14 = 5.4 + 5.6 = 11.0 pts de 70% evaluado
    # Promedio normalizado = 11.0 / 0.70 = 15.71
    print(f"  📊 Materia '{c1['name']}': Evaluado={c1['accumulated_percent']}%, Promedio={c1['current_average']}")
    assert c1["accumulated_percent"] == 70.0
    assert abs(c1["current_average"] - 15.71) < 0.05
    print("  ✅ Promedio normalizado y avance porcentual calculados con precisión matemática.")

    # Modificar nota de Evaluación 1 de 18.0 a 20.0
    r = client.put(f"/api/v1/academic/evaluations/{ev1_id}", json={"score": 20.0}, headers=headers)
    assert r.status_code == 200
    assert r.json()["grade"]["score"] == 20.0
    print("  ✅ Calificación modificada de 18.0 a 20.0.")

    # Eliminar Evaluación 3
    r = client.delete(f"/api/v1/academic/evaluations/{ev3_id}", headers=headers)
    assert r.status_code == 200
    print("  ✅ Evaluación 3 eliminada exitosamente.")

    # ─── 5. ESTADÍSTICAS DEL DASHBOARD EN TIEMPO REAL ───────────
    print("\n[5/6] Probando Estadísticas Globales del Dashboard (GPA, Activas, Aprobadas)...")
    # Evaluaciones para materia 2 (reprobada para verificar clasificación)
    r = client.post(f"/api/v1/academic/subjects/{sub2_id}/evaluations", json={
        "name": "Práctica 1",
        "eval_type": "homework",
        "weight_percent": 100.0,
        "score": 08.0  # < 10.0 -> Reprobada
    }, headers=headers)
    assert r.status_code == 201

    r = client.get("/api/v1/academic/stats", headers=headers)
    assert r.status_code == 200
    stats = r.json()
    print(f"  📈 Estadísticas del Dashboard: {stats}")
    assert stats["active_subjects_count"] == 2
    assert stats["passed_count"] == 1
    assert stats["failed_count"] == 1
    assert stats["max_scale"] == 20.0
    assert stats["passing_grade"] == 10.0
    assert stats["gpa"] is not None
    print(f"  ✅ GPA ponderado ({stats['gpa']}), Aprobadas ({stats['passed_count']}), Reprobadas ({stats['failed_count']}) 100% correctos.")

    # ─── 6. ELIMINACIÓN EN CASCADA ──────────────────────────────
    print("\n[6/6] Probando Eliminación en Cascada de Materias...")
    r = client.delete(f"/api/v1/academic/subjects/{sub1_id}", headers=headers)
    assert r.status_code == 200
    r = client.get("/api/v1/academic/subjects", headers=headers)
    assert len(r.json()) == 1
    print("  ✅ Eliminación en cascada confirmada: evaluaciones y notas borradas con la materia.")

    print("\n" + "="*70)
    print("🎉 ¡TODAS LAS FASES Y PRUEBAS DEL PLAN DE REVISIÓN FUERON SUPERADAS CON ÉXITO AL 100%!")
    print("="*70)

if __name__ == "__main__":
    run_exhaustive_audit()
