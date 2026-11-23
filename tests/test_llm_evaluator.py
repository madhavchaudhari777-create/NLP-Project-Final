
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from app.ai.llm_evaluator import LLMEvaluator, AnswerEvaluation


class TestLLMEvaluator(unittest.TestCase):

    def setUp(self):
        # Mock the API so tests do not make real requests.
        self.mock_client = Mock()
        self.evaluator = LLMEvaluator(
            client=self.mock_client,
            model="test-model"
        )

    def test_empty_answer_returns_zero(self):
        result = self.evaluator.evaluate_answer(
            question="What is Python?",
            answer=""
        )

        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["correctness"], 0)
        self.assertEqual(result["max_score"], 10)
        self.mock_client.responses.parse.assert_not_called()

    def test_empty_question_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_answer(
                question=" ",
                answer="Python is a programming language."
            )

    def test_invalid_answer_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.evaluator.evaluate_answer(
                question="What is Python?",
                answer=None
            )

    def test_invalid_max_score_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_answer(
                question="What is Python?",
                answer="Python is a programming language.",
                max_score=0
            )

    def test_valid_answer_is_evaluated(self):
        # Simulate a structured response from the LLM.
        evaluation = AnswerEvaluation(
            correctness=9,
            relevance=10,
            completeness=8,
            clarity=9,
            score=8.5,
            strengths=["Correct definition"],
            improvements=["Add an example"],
            feedback="A strong answer."
        )

        self.mock_client.responses.parse.return_value = (
            SimpleNamespace(output_parsed=evaluation)
        )

        result = self.evaluator.evaluate_answer(
            question="What is Python?",
            answer="Python is a programming language.",
            max_score=20
        )

        self.assertEqual(result["correctness"], 9)
        self.assertEqual(result["score"], 17.0)
        self.assertEqual(result["max_score"], 20)
        self.assertIn("Correct definition", result["strengths"])
        self.assertEqual(result["feedback"], "A strong answer.")

        self.mock_client.responses.parse.assert_called_once()

    def test_api_failure_is_handled(self):
        self.mock_client.responses.parse.side_effect = Exception(
            "Simulated API failure"
        )

        with self.assertRaisesRegex(
            RuntimeError, "Answer evaluation failed"
        ):
            self.evaluator.evaluate_answer(
                question="What is Python?",
                answer="Python is a programming language."
            )


if __name__ == "__main__":
    unittest.main()
