
import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.db import init_db
from app.routes import interview_sessions


class TestInterviewRoutes(unittest.TestCase):

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": self.temp_db_path,
        })
        init_db(self.temp_db_path)
        self.client = self.app.test_client()

        interview_sessions.clear()

        self.setup_data = {
            "name": "Test Candidate",
            "role": "Python Developer",
            "skills": ["Python"],
            "difficulty": "Beginner",
            "number_of_questions": 2,
        }

        # Use a predictable question pool for route tests.
        self.questions = [
            {
                "id": 1,
                "question": "What is a variable in Python?",
                "role": "Python Developer",
                "skills": ["Python"],
                "difficulty": "Beginner",
                "reference_answer": (
                    "A variable is a name that refers to a value."
                ),
            },
            {
                "id": 2,
                "question": "What is the difference between a list and tuple?",
                "role": "Python Developer",
                "skills": ["Python"],
                "difficulty": "Beginner",
                "reference_answer": (
                    "Lists are mutable, while tuples are immutable."
                ),
            },
        ]

        self.question_patcher = patch(
            "app.routes.question_service.get_questions",
            return_value=self.questions,
        )
        self.question_patcher.start()
        self.addCleanup(self.question_patcher.stop)

        # Prevent route tests from requiring OpenAI API credits.
        self.llm_patcher = patch(
            "app.services.interview_service.LLMEvaluator.evaluate_answer",
            return_value={
                "score": 8,
                "max_score": 10,
                "correctness": 8,
                "relevance": 8,
                "completeness": 7,
                "clarity": 9,
                "strengths": ["Clear explanation"],
                "improvements": ["Add more detail"],
                "feedback": "Good answer",
            },
        )
        self.llm_patcher.start()
        self.addCleanup(self.llm_patcher.stop)

    def tearDown(self):
        interview_sessions.clear()
        if hasattr(self, "temp_db_path") and os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def start_interview(self):
        """Start an interview and return its setup response."""
        response = self.client.post(
            "/setup",
            json=self.setup_data,
        )
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def get_active_interview(self):
        """Get the interview associated with the test browser session."""
        with self.client.session_transaction() as browser_session:
            interview_id = browser_session.get("interview_id")

        self.assertIsNotNone(interview_id)
        self.assertIn(interview_id, interview_sessions)

        return interview_sessions[interview_id]

    def submit_current_answer(self, answer="A variable stores a value."):
        """Submit an answer for the current question."""
        interview = self.get_active_interview()
        question_id = interview["current_question_id"]

        question = next(
            item
            for item in interview["questions"]
            if item["id"] == question_id
        )

        return self.client.post(
            "/evaluate",
            json={
                "question_id": question["id"],
                "question": question["question"],
                "answer": answer,
            },
        )

    # ---------------- Home and setup tests ----------------

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_setup_page_loads(self):
        response = self.client.get("/setup")

        self.assertEqual(response.status_code, 200)

    def test_missing_name_is_rejected(self):
        data = dict(self.setup_data)
        data["name"] = ""

        response = self.client.post("/setup", json=data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_missing_role_is_rejected(self):
        data = dict(self.setup_data)
        data["role"] = ""

        response = self.client.post("/setup", json=data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_missing_skills_is_rejected(self):
        data = dict(self.setup_data)
        data["skills"] = []

        response = self.client.post("/setup", json=data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_invalid_question_count_is_rejected(self):
        data = dict(self.setup_data)
        data["number_of_questions"] = "abc"

        response = self.client.post("/setup", json=data)

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "whole number",
            response.get_json()["error"],
        )

    def test_setup_rejects_more_than_ten_questions(self):
        data = dict(self.setup_data)
        data["number_of_questions"] = 11

        response = self.client.post("/setup", json=data)

        self.assertEqual(response.status_code, 400)

    def test_valid_setup_returns_questions(self):
        response = self.client.post(
            "/setup",
            json=self.setup_data,
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertIn("candidate", data)
        self.assertIn("question", data)
        self.assertIn("id", data["question"])
        self.assertIn("question", data["question"])
        self.assertIn("difficulty", data["question"])
        self.assertNotIn("questions", data)
        self.assertEqual(data["progress"]["answered"], 0)
        self.assertEqual(
            data["progress"]["total"],
            self.setup_data["number_of_questions"],
        )

    # ---------------- Next-question tests ----------------

    def test_next_question_returns_current_question(self):
        self.start_interview()

        response = self.client.get("/next-question")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertIn("question", data)
        self.assertIn("id", data["question"])
        self.assertEqual(data["progress"]["answered"], 0)
        self.assertEqual(data["progress"]["total"], 2)

    def test_next_question_requires_active_interview(self):
        response = self.client.get("/next-question")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    # ---------------- Answer evaluation tests ----------------

    def test_evaluation_requires_active_interview(self):
        response = self.client.post(
            "/evaluate",
            json={
                "question": "What is a variable?",
                "answer": "A variable stores a value.",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "No active interview",
            response.get_json()["error"],
        )

    def test_empty_answer_is_rejected(self):
        self.start_interview()

        response = self.submit_current_answer("   ")

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "answer",
            response.get_json()["error"].lower(),
        )

    def test_missing_question_is_rejected(self):
        self.start_interview()

        response = self.client.post(
            "/evaluate",
            json={
                "answer": "A variable stores a value.",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_invalid_json_body_is_rejected(self):
        response = self.client.post(
            "/evaluate",
            data="not json",
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_valid_answer_returns_evaluation(self):
        self.start_interview()

        response = self.submit_current_answer()

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertIn("evaluation", data)
        self.assertIn("nlp_summary", data)
        self.assertIn("adaptation", data)
        self.assertIn("interview_state", data)
        self.assertEqual(data["evaluation"]["score"], 8)
        self.assertEqual(data["progress"]["answered"], 1)
        self.assertEqual(data["progress"]["total"], 2)
        self.assertFalse(data["interview_complete"])
        self.assertIsNotNone(data["next_question"])

    def test_evaluation_rejects_wrong_question_id(self):
        self.start_interview()

        response = self.client.post(
            "/evaluate",
            json={
                "question_id": "not-a-valid-question",
                "answer": "This is my answer.",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "does not belong",
            response.get_json()["error"],
        )

    def test_duplicate_answer_is_rejected(self):
        self.start_interview()

        first_response = self.submit_current_answer()
        self.assertEqual(first_response.status_code, 200)

        interview = self.get_active_interview()
        first_question = self.questions[0]

        response = self.client.post(
            "/evaluate",
            json={
                "question_id": str(first_question["id"]),
                "question": first_question["question"],
                "answer": "A variable stores a value.",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_final_answer_completes_interview(self):
        self.start_interview()

        first_response = self.submit_current_answer()
        self.assertEqual(first_response.status_code, 200)

        second_response = self.submit_current_answer(
            "A list is mutable, while a tuple is immutable."
        )

        self.assertEqual(second_response.status_code, 200)

        data = second_response.get_json()

        self.assertTrue(data["success"])
        self.assertTrue(data["interview_complete"])
        self.assertIsNone(data["next_question"])
        self.assertEqual(data["progress"]["answered"], 2)
        self.assertEqual(data["progress"]["total"], 2)

    def test_completed_interview_rejects_next_question(self):
        self.start_interview()

        self.submit_current_answer()
        self.submit_current_answer(
            "A list is mutable, while a tuple is immutable."
        )

        response = self.client.get("/next-question")

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "complete",
            response.get_json()["error"].lower(),
        )


if __name__ == "__main__":
    unittest.main()
