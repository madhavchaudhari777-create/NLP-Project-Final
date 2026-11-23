
import unittest
from unittest.mock import Mock

from app.services.interview_service import InterviewService


class TestInterviewService(unittest.TestCase):

    def setUp(self):
        self.nlp = Mock()
        self.nlp.analyze_answer.return_value = {
            "word_count": 10,
            "skills": ["Python"],
            "keywords": ["function", "decorator"],
        }

        self.llm = Mock()
        self.local = Mock()
        self.dialogue = Mock()

        self.dialogue.current_difficulty = "Intermediate"
        self.dialogue.get_state.return_value = {
            "interview_complete": False,
            "questions_answered": 1,
        }
        self.dialogue.record_evaluation.return_value = {
            "difficulty_change": "none",
            "next_difficulty": "Intermediate",
        }

        self.service = InterviewService(
            nlp_processor=self.nlp,
            llm_evaluator=self.llm,
            local_evaluator=self.local,
            dialogue_manager=self.dialogue,
        )

        self.question = "Explain decorators in Python."
        self.answer = (
            "A decorator is a function that extends "
            "the behavior of another function."
        )

        self.llm_result = {
            "score": 8,
            "max_score": 10,
            "correctness": 8,
            "relevance": 8,
            "completeness": 7,
            "clarity": 9,
            "strengths": ["Clear explanation"],
            "improvements": [],
            "feedback": "Good answer",
        }

        self.local_result = {
            "score": 7,
            "max_score": 10,
            "correctness": 7,
            "relevance": 7,
            "completeness": 6,
            "clarity": 8,
            "strengths": ["Relevant concepts"],
            "improvements": ["Add an example"],
            "feedback": "Local evaluation",
        }

    def test_valid_answer_uses_llm(self):
        self.llm.evaluate_answer.return_value = self.llm_result

        result = self.service.process_answer(
            question=self.question,
            answer=self.answer,
            role="Python Developer",
        )

        self.assertEqual(result["evaluation"]["score"], 8)
        self.assertEqual(
            result["evaluation"]["evaluation_method"], "llm"
        )
        self.assertEqual(result["difficulty"], "Intermediate")

        self.llm.evaluate_answer.assert_called_once()
        self.local.evaluate_answer.assert_not_called()
        self.dialogue.record_evaluation.assert_called_once()

    def test_llm_failure_uses_local_fallback(self):
        self.llm.evaluate_answer.side_effect = RuntimeError(
            "API credits exhausted"
        )
        self.local.evaluate_answer.return_value = self.local_result

        result = self.service.process_answer(
            question=self.question,
            answer=self.answer,
        )

        self.assertEqual(result["evaluation"]["score"], 7)
        self.assertEqual(
            result["evaluation"]["evaluation_method"],
            "local_fallback",
        )

        self.llm.evaluate_answer.assert_called_once()
        self.local.evaluate_answer.assert_called_once()
        self.dialogue.record_evaluation.assert_called_once()

    def test_nlp_analysis_is_passed_to_evaluator(self):
        self.llm.evaluate_answer.return_value = self.llm_result

        self.service.process_answer(
            question=self.question,
            answer=self.answer,
        )

        kwargs = self.llm.evaluate_answer.call_args.kwargs
        self.assertEqual(
            kwargs["nlp_analysis"],
            self.nlp.analyze_answer.return_value,
        )

    def test_reference_answer_is_passed_to_evaluator(self):
        self.llm.evaluate_answer.return_value = self.llm_result
        reference = (
            "A decorator modifies or extends a function's behavior."
        )

        self.service.process_answer(
            question=self.question,
            answer=self.answer,
            reference_answer=reference,
        )

        kwargs = self.llm.evaluate_answer.call_args.kwargs
        self.assertEqual(kwargs["reference_answer"], reference)

    def test_empty_question_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Question"):
            self.service.process_answer(
                question=" ",
                answer=self.answer,
            )

        self.llm.evaluate_answer.assert_not_called()
        self.local.evaluate_answer.assert_not_called()

    def test_empty_answer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Answer"):
            self.service.process_answer(
                question=self.question,
                answer=" ",
            )

        self.llm.evaluate_answer.assert_not_called()
        self.local.evaluate_answer.assert_not_called()

    def test_non_string_answer_is_rejected(self):
<<<<<<< HEAD
        with self.assertRaises(ValueError):
=======
        with self.assertRaises(TypeError):
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
            self.service.process_answer(
                question=self.question,
                answer=123,
            )

    def test_completed_interview_rejects_answer(self):
        self.dialogue.get_state.return_value = {
            "interview_complete": True,
            "questions_answered": 5,
        }

        with self.assertRaisesRegex(ValueError, "already complete"):
            self.service.process_answer(
                question=self.question,
                answer=self.answer,
            )

        self.llm.evaluate_answer.assert_not_called()
        self.local.evaluate_answer.assert_not_called()

<<<<<<< HEAD
    def test_local_failure_uses_error_fallback(self):
        """When both LLM and local evaluator fail, return error fallback evaluation."""
=======
    def test_local_failure_does_not_update_dialogue(self):
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        self.llm.evaluate_answer.side_effect = RuntimeError(
            "API unavailable"
        )
        self.local.evaluate_answer.side_effect = RuntimeError(
            "Local evaluator failed"
        )

<<<<<<< HEAD
        result = self.service.process_answer(
            question=self.question,
            answer=self.answer,
        )

        # Should return a fallback evaluation without raising
        self.assertEqual(result["evaluation"]["evaluation_method"], "error_fallback")
        self.assertEqual(result["evaluation"]["score"], 0.0)
        self.assertIn("could not be completed", result["evaluation"]["feedback"].lower())
        
        # Dialogue should not be updated since evaluation failed
=======
        with self.assertRaisesRegex(
            RuntimeError, "Local evaluator failed"
        ):
            self.service.process_answer(
                question=self.question,
                answer=self.answer,
            )

>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        self.dialogue.record_evaluation.assert_not_called()

    def test_interview_state_is_returned(self):
        state = self.service.get_interview_state()

        self.assertEqual(state["interview_complete"], False)
        self.dialogue.get_state.assert_called_once()

    def test_question_id_is_tracked_after_successful_answer(self):
        self.llm.evaluate_answer.return_value = self.llm_result

        result = self.service.process_answer(
            question=self.question,
            answer=self.answer,
            question_id="q1",
        )

        self.assertEqual(result["question_id"], "q1")
        self.assertIn("q1", self.service.get_asked_question_ids())

    def test_duplicate_question_id_is_rejected(self):
        self.llm.evaluate_answer.return_value = self.llm_result

        self.service.process_answer(
            question=self.question,
            answer=self.answer,
            question_id="q1",
        )

        with self.assertRaisesRegex(
            ValueError, "already been answered"
        ):
            self.service.process_answer(
                question=self.question,
                answer=self.answer,
                question_id="q1",
            )

        self.assertEqual(self.llm.evaluate_answer.call_count, 1)

    def test_evaluation_history_is_recorded(self):
        self.llm.evaluate_answer.return_value = self.llm_result

        self.service.process_answer(
            question=self.question,
            answer=self.answer,
            question_id="q1",
        )

        history = self.service.get_evaluation_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["question_id"], "q1")
        self.assertEqual(history[0]["difficulty"], "Intermediate")


if __name__ == "__main__":
    unittest.main()
