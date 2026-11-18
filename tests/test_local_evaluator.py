
import unittest

from app.ai.local_evaluator import LocalEvaluator


class TestLocalEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = LocalEvaluator()

    def test_empty_answer_gets_zero(self):
        result = self.evaluator.evaluate_answer(
            question="What is Python?",
            answer="",
        )

        self.assertEqual(result["score"], 0)
        self.assertEqual(result["correctness"], 0)
        self.assertEqual(result["evaluation_method"], "local_fallback")

    def test_empty_question_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_answer(
                question=" ",
                answer="Python is a programming language.",
            )

    def test_invalid_max_score_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_answer(
                question="What is Python?",
                answer="Python is a programming language.",
                max_score=0,
            )

    def test_max_score_must_be_numeric(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_answer(
                question="What is Python?",
                answer="Python is a programming language.",
                max_score="10",
            )

    def test_boolean_max_score_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_answer(
                question="What is Python?",
                answer="Python is a programming language.",
                max_score=True,
            )

    def test_correct_gil_answer_recognizes_core_concepts(self):
        result = self.evaluator.evaluate_answer(
            question="What is the Global Interpreter Lock (GIL)?",
            answer=(
                "The GIL is a lock in CPython that allows only "
                "one thread to execute Python bytecode at a time."
            ),
        )

        self.assertGreaterEqual(result["correctness"], 7)
        self.assertGreaterEqual(result["score"], 7)
        self.assertEqual(result["evaluation_method"], "local_fallback")

    def test_overfitting_answer(self):
        result = self.evaluator.evaluate_answer(
            question="What is overfitting in machine learning?",
            answer=(
                "Overfitting happens when a model learns the training "
                "data too closely, including noise, and performs poorly "
                "on unseen data."
            ),
        )

        self.assertGreaterEqual(result["correctness"], 7)
        self.assertGreater(result["score"], 0)

    def test_classification_and_regression(self):
        result = self.evaluator.evaluate_answer(
            question="Differentiate classification and regression.",
            answer=(
                "Classification predicts categories or class labels, "
                "while regression predicts continuous numerical values."
            ),
        )

        self.assertEqual(result["correctness"], 10)
        self.assertGreater(result["score"], 0)

    def test_primary_key_answer(self):
        result = self.evaluator.evaluate_answer(
            question="What is a primary key in a database?",
            answer=(
                "A primary key is a column that uniquely identifies "
                "each row or record in a table."
            ),
        )

        self.assertGreaterEqual(result["correctness"], 7)
        self.assertGreater(result["score"], 0)

    def test_reference_answer_matching(self):
        reference = (
            "A stack follows last in first out order. "
            "Push inserts an element and pop removes the top element."
        )

        result = self.evaluator.evaluate_answer(
            question="Explain the stack data structure.",
            answer=(
                "A stack uses LIFO ordering. Push adds an item "
                "and pop removes the top item."
            ),
            reference_answer=reference,
        )

        self.assertGreaterEqual(result["correctness"], 6)
        self.assertGreater(result["score"], 0)

    def test_score_stays_within_max_score(self):
        result = self.evaluator.evaluate_answer(
            question="What is a Python variable?",
            answer=(
                "A variable is a name that refers to a value or object "
                "and can store data."
            ),
            max_score=5,
        )

        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 5)
        self.assertEqual(result["max_score"], 5)

    def test_result_contains_required_fields(self):
        result = self.evaluator.evaluate_answer(
            question="What is a Python variable?",
            answer=(
                "A variable is a name that refers to a value "
                "and stores data."
            ),
        )

        required_fields = {
            "score",
            "max_score",
            "correctness",
            "relevance",
            "completeness",
            "clarity",
            "strengths",
            "improvements",
            "feedback",
            "evaluation_method",
        }

        self.assertTrue(required_fields.issubset(result.keys()))

    def test_unknown_question_without_reference(self):
        result = self.evaluator.evaluate_answer(
            question="Explain a concept not covered by topic rules.",
            answer="This is a sufficiently long answer with several words.",
        )

        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 10)
        self.assertEqual(result["evaluation_method"], "local_fallback")

    def test_short_answer_gets_completeness_penalty(self):
        short_result = self.evaluator.evaluate_answer(
            question="What is a Python variable?",
            answer="A variable stores data.",
        )

        detailed_result = self.evaluator.evaluate_answer(
            question="What is a Python variable?",
            answer=(
                "A variable is a name that refers to a value or object. "
                "It can store data and be used later in a program."
            ),
        )

        self.assertLess(
            short_result["completeness"],
            detailed_result["completeness"],
        )


if __name__ == "__main__":
    unittest.main()
