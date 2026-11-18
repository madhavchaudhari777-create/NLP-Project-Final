import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.db import init_db


class TestAuthAndDashboards(unittest.TestCase):

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE_PATH": self.temp_db_path,
        })
        init_db(self.temp_db_path)
        self.client = self.app.test_client()

        # Mock LLM evaluation to avoid external API calls in tests
        self.llm_patcher = patch(
            "app.services.interview_service.LLMEvaluator.evaluate_answer",
            return_value={
                "score": 8.5,
                "max_score": 10.0,
                "correctness": 9,
                "relevance": 8,
                "completeness": 8,
                "clarity": 9,
                "strengths": ["Strong conceptual clarity"],
                "improvements": ["Elaborate on edge cases"],
                "feedback": "Great technical response.",
            },
        )
        self.llm_patcher.start()
        self.addCleanup(self.llm_patcher.stop)

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def register_user(self, name="Alice", email="alice@test.com", password="password123", role="student"):
        return self.client.post("/register", json={
            "name": name,
            "email": email,
            "password": password,
            "role": role,
        })

    def login_user(self, email="alice@test.com", password="password123"):
        return self.client.post("/login", json={
            "email": email,
            "password": password,
        })

    # ---------------- Auth Tests ----------------

    def test_user_registration_success(self):
        resp = self.register_user()
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["name"], "Alice")
        self.assertEqual(data["user"]["role"], "student")

    def test_duplicate_email_registration_rejected(self):
        self.register_user(email="alice@test.com")
        resp = self.register_user(email="alice@test.com")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("already exists", resp.get_json()["error"])

    def test_short_password_rejected(self):
        resp = self.register_user(password="123")
        self.assertEqual(resp.status_code, 400)

    def test_login_success(self):
        self.register_user(email="alice@test.com", password="password123")
        resp = self.login_user(email="alice@test.com", password="password123")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["success"])

    def test_login_invalid_credentials(self):
        self.register_user(email="alice@test.com", password="password123")
        resp = self.login_user(email="alice@test.com", password="wrongpassword")
        self.assertEqual(resp.status_code, 401)

    def test_logout(self):
        self.register_user()
        me_resp = self.client.get("/api/me")
        self.assertTrue(me_resp.get_json()["authenticated"])

        self.client.post("/logout")
        me_after = self.client.get("/api/me")
        self.assertFalse(me_after.get_json()["authenticated"])

    # ---------------- Student Dashboard Tests ----------------

    def test_student_dashboard_requires_login(self):
        resp = self.client.get("/api/student/dashboard")
        self.assertEqual(resp.status_code, 401)

    def test_student_dashboard_returns_stats(self):
        self.register_user(name="Bob", email="bob@test.com", role="student")
        resp = self.client.get("/api/student/dashboard")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["stats"]["total_interviews"], 0)
        self.assertEqual(data["stats"]["average_percentage"], 0.0)

    # ---------------- End-to-End Interview & Report Tests ----------------

    def test_authenticated_interview_persists_to_dashboard_and_generates_report(self):
        # 1. Register student
        self.register_user(name="Student Dave", email="dave@test.com", role="student")

        # 2. Setup interview
        setup_resp = self.client.post("/setup", json={
            "name": "Student Dave",
            "role": "Python Developer",
            "skills": ["Python"],
            "difficulty": "Beginner",
            "number_of_questions": 1,
        })
        self.assertEqual(setup_resp.status_code, 200)
        setup_data = setup_resp.get_json()
        interview_id = setup_data["interview_id"]
        q_id = setup_data["question"]["id"]

        # 3. Submit answer
        eval_resp = self.client.post("/evaluate", json={
            "question_id": q_id,
            "answer": "A variable in Python is a named reference pointing to an object in memory.",
        })
        self.assertEqual(eval_resp.status_code, 200)
        self.assertTrue(eval_resp.get_json()["interview_complete"])

        # 4. Check student dashboard
        dash_resp = self.client.get("/api/student/dashboard")
        self.assertEqual(dash_resp.status_code, 200)
        dash_data = dash_resp.get_json()
        self.assertEqual(dash_data["stats"]["total_interviews"], 1)
        self.assertEqual(dash_data["stats"]["completed_interviews"], 1)
        self.assertEqual(len(dash_data["interviews"]), 1)
        self.assertEqual(dash_data["interviews"][0]["id"], interview_id)

        # 5. Check detailed report
        report_resp = self.client.get(f"/api/interview/{interview_id}/report")
        self.assertEqual(report_resp.status_code, 200)
        report_data = report_resp.get_json()
        self.assertTrue(report_data["success"])
        self.assertEqual(report_data["interview"]["role_applied"], "Python Developer")
        self.assertEqual(len(report_data["answers"]), 1)
        self.assertIn("recommendations", report_data["report"])

    def test_unauthorized_student_cannot_view_peer_report(self):
        # Alice completes an interview
        self.register_user(name="Alice", email="alice@test.com", role="student")
        setup_resp = self.client.post("/setup", json={
            "name": "Alice",
            "role": "Python Developer",
            "skills": ["Python"],
            "difficulty": "Beginner",
            "number_of_questions": 1,
        })
        interview_id = setup_resp.get_json()["interview_id"]
        self.client.post("/logout")

        # Bob logs in and tries to access Alice's interview report
        self.register_user(name="Bob", email="bob@test.com", role="student")
        hack_resp = self.client.get(f"/api/interview/{interview_id}/report")
        self.assertEqual(hack_resp.status_code, 403)

    # ---------------- Teacher Admin Tests ----------------

    def test_teacher_analytics_forbidden_for_students(self):
        self.register_user(name="Charlie", email="charlie@test.com", role="student")
        resp = self.client.get("/api/teacher/analytics")
        self.assertEqual(resp.status_code, 403)

    def test_teacher_analytics_accessible_for_teachers(self):
        self.register_user(name="Prof Smith", email="prof@test.com", role="teacher")
        resp = self.client.get("/api/teacher/analytics")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("class_average_percentage", data["analytics"])

    def test_teacher_can_view_student_list_and_audit_report(self):
        # Register a student and complete an interview
        self.register_user(name="Student Dan", email="dan@test.com", role="student")
        setup_resp = self.client.post("/setup", json={
            "name": "Student Dan",
            "role": "Python Developer",
            "skills": ["Python"],
            "difficulty": "Beginner",
            "number_of_questions": 1,
        })
        setup_data = setup_resp.get_json()
        interview_id = setup_data["interview_id"]
        self.client.post("/evaluate", json={
            "question_id": setup_data["question"]["id"],
            "answer": "Variables store references to Python objects.",
        })
        self.client.post("/logout")

        # Register teacher and audit
        self.register_user(name="Teacher Mary", email="mary@test.com", role="teacher")

        # Check student roster
        roster_resp = self.client.get("/api/teacher/students")
        self.assertEqual(roster_resp.status_code, 200)
        students = roster_resp.get_json()["students"]
        dan_entry = next((s for s in students if s["email"] == "dan@test.com"), None)
        self.assertIsNotNone(dan_entry)
        self.assertEqual(dan_entry["completed_interviews"], 1)

        # Audit Dan's interview report as teacher
        audit_resp = self.client.get(f"/api/interview/{interview_id}/report")
        self.assertEqual(audit_resp.status_code, 200)
        audit_data = audit_resp.get_json()
        self.assertEqual(len(audit_data["answers"]), 1)
        self.assertEqual(audit_data["interview"]["candidate_name"], "Student Dan")


if __name__ == "__main__":
    unittest.main()
