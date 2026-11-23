
import unittest
import random

from app.services.question_service import QuestionService


class TestQuestionService(unittest.TestCase):

    def setUp(self):
        self.service = QuestionService(rng=random.Random(42))

    def test_selects_requested_difficulty(self):
        questions = self.service.get_questions(
            role="Python Developer",
            skills=["Python"],
            difficulty="Beginner",
            number_of_questions=2,
        )

        self.assertEqual(len(questions), 2)
        self.assertTrue(
            all(q["difficulty"] == "Beginner" for q in questions)
        )

    def test_questions_are_not_repeated(self):
        questions = self.service.get_questions(
            role="Python Developer",
            difficulty="Beginner",
            number_of_questions=2,
        )

        ids = [q["id"] for q in questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_reference_answers_are_included(self):
        questions = self.service.get_questions(
            role="Python Developer",
            difficulty="Beginner",
            number_of_questions=1,
        )

        self.assertTrue(questions[0]["reference_answer"])

    def test_excluded_questions_are_skipped(self):
        questions = self.service.get_questions(
            role="Python Developer",
            difficulty="Beginner",
            number_of_questions=1,
            exclude_ids=[1],
        )

        self.assertNotEqual(questions[0]["id"], 1)

    def test_unknown_role_can_use_skill_matches(self):
        questions = self.service.get_questions(
            role="Data Analyst",
            skills=["SQL"],
            difficulty="Beginner",
            number_of_questions=1,
        )

# Should match a Data Analyst question with SQL skill (id 39: INNER JOIN vs LEFT JOIN)
        self.assertEqual(int(questions[0]["id"]), 39)
        self.assertEqual(questions[0]["role"], "data analyst")
        self.assertIn("sql", [s.lower() for s in questions[0]["skills"]])

    def test_invalid_role_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.get_questions(
                role=" ",
                number_of_questions=1,
            )

    def test_invalid_difficulty_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.get_questions(
                role="Python Developer",
                difficulty="Expert",
                number_of_questions=1,
            )

    def test_invalid_question_count_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.get_questions(
                role="Python Developer",
                number_of_questions=0,
            )

    def test_insufficient_questions_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Only"):
            self.service.get_questions(
                role="Python Developer",
                difficulty="Beginner",
                number_of_questions=100,
            )

    def test_adaptive_difficulty_selects_matching_question(self):
        questions = self.service.get_questions(
            role="Python Developer",
            skills=["Python"],
            difficulty="Advanced",
            number_of_questions=1,
        )

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["difficulty"], "Advanced")

    def test_adaptive_selection_respects_excluded_ids(self):
        questions = self.service.get_questions(
            role="Python Developer",
            skills=["Python"],
            difficulty="Intermediate",
            number_of_questions=1,
            exclude_ids=[3],
        )

        self.assertEqual(len(questions), 1)
        self.assertNotEqual(questions[0]["id"], 3)


if __name__ == "__main__":
    unittest.main()
