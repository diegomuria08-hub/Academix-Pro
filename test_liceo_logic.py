import sys
import os
import unittest
from types import SimpleNamespace

root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.academic_service import calculate_subject_metrics

def make_eval(id, name, weight, lapso, score):
    grade = SimpleNamespace(
        id=f"g-{id}",
        evaluation_id=id,
        score=score,
        notes="Nota registrada"
    ) if score is not None else None

    return SimpleNamespace(
        id=id,
        subject_id="sub-123",
        name=name,
        description="Evaluación académica",
        eval_type="exam",
        weight_percent=weight,
        date=None,
        status="calificada" if score is not None else "pendiente",
        max_grade=20.0,
        lapso_number=lapso,
        grade=grade
    )

class TestLiceoBusinessLogic(unittest.TestCase):
    def test_liceo_lapsos_and_annual_definitiva(self):
        """
        Prueba quirúrgica de la regla de negocio #1:
        - 3 lapsos escolares.
        - En cada lapso las evaluaciones suman hasta 100%.
        - La definitiva anual es el promedio aritmético de las notas de los lapsos completados.
        """
        # Lapso 1: 100% evaluado
        # Examen 1: 50% con 16/20 -> 8 pts
        # Examen 2: 50% con 18/20 -> 9 pts
        # Total Lapso 1 = 17.0 pts
        ev1 = make_eval("e1", "Parcial 1 Lapso 1", 50.0, 1, 16.0)
        ev2 = make_eval("e2", "Parcial 2 Lapso 1", 50.0, 1, 18.0)

        # Lapso 2: 100% evaluado
        # Taller: 40% con 20/20 -> 8 pts
        # Examen: 60% con 15/20 -> 9 pts
        # Total Lapso 2 = 17.0 pts
        ev3 = make_eval("e3", "Taller Lapso 2", 40.0, 2, 20.0)
        ev4 = make_eval("e4", "Examen Lapso 2", 60.0, 2, 15.0)

        # Lapso 3: 100% evaluado
        # Proyecto Final: 100% con 14/20 -> 14 pts
        # Total Lapso 3 = 14.0 pts
        ev5 = make_eval("e5", "Proyecto Lapso 3", 100.0, 3, 14.0)

        mock_subject = SimpleNamespace(
            id="sub-123",
            name="Biología General",
            code="BIO-01",
            color_hex="#00E5FF",
            credits=4,
            period_id="p-1",
            passing_grade_override=None,
            max_grade_override=None,
            target_grade=15.0,
            is_archived=False,
            evaluations=[ev1, ev2, ev3, ev4, ev5]
        )

        subject_response, _, _, _, _ = calculate_subject_metrics(
            subject=mock_subject,
            default_passing=10.0,
            default_max=20.0,
            evaluation_mode="liceo",
            student_type="high_school",
            total_lapsos=3,
            current_lapso=3
        )

        # Validaciones de la regla de negocio
        self.assertIsNotNone(subject_response.lapsos_summary)
        self.assertEqual(len(subject_response.lapsos_summary), 3)

        # Lapso 1
        l1 = subject_response.lapsos_summary[0]
        self.assertEqual(l1["lapso"], 1)
        self.assertEqual(l1["accumulated_points"], 17.0)
        self.assertEqual(l1["evaluated_percent"], 100.0)
        self.assertTrue(l1["is_completed"])

        # Lapso 2
        l2 = subject_response.lapsos_summary[1]
        self.assertEqual(l2["lapso"], 2)
        self.assertEqual(l2["accumulated_points"], 17.0)
        self.assertEqual(l2["evaluated_percent"], 100.0)
        self.assertTrue(l2["is_completed"])

        # Lapso 3
        l3 = subject_response.lapsos_summary[2]
        self.assertEqual(l3["lapso"], 3)
        self.assertEqual(l3["accumulated_points"], 14.0)
        self.assertEqual(l3["evaluated_percent"], 100.0)
        self.assertTrue(l3["is_completed"])

        # Definitiva Anual: Promedio exacto de (17 + 17 + 14) / 3 = 48 / 3 = 16.0 pts
        self.assertEqual(subject_response.annual_definitiva, 16.0)
        self.assertTrue(subject_response.is_passed)
        print("\n>>> [SUCCESS] Regla de Negocio de Liceo/Secundaria verificada al 100%!")
        print(f">>> Lapsos calculados: {len(subject_response.lapsos_summary)}")
        print(f">>> Lapso 1: {l1['accumulated_points']} pts | Lapso 2: {l2['accumulated_points']} pts | Lapso 3: {l3['accumulated_points']} pts")
        print(f">>> Promedio Definitivo Anual: {subject_response.annual_definitiva} / 20 pts")

if __name__ == "__main__":
    unittest.main()
