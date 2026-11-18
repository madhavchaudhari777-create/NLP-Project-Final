
from app.ai.nlp_processor import NLPProcessor
from app.ai.llm_evaluator import LLMEvaluator
from app.ai.local_evaluator import LocalEvaluator
from app.ai.dialogue_manager import DialogueManager


class InterviewService:
    """Coordinate answer evaluation and adaptive interview progress."""

    def __init__(
        self,
        nlp_processor=None,
        llm_evaluator=None,
        local_evaluator=None,
        dialogue_manager=None,
    ):
        self.nlp_processor = nlp_processor or NLPProcessor()
        self.llm_evaluator = llm_evaluator or LLMEvaluator()
        self.local_evaluator = local_evaluator or LocalEvaluator()
        self.dialogue_manager = dialogue_manager or DialogueManager()

        # Track answered questions and evaluation history.
        self.asked_question_ids = set()
        self.evaluation_history = []

    def process_answer(
        self,
        question,
        answer,
        role="General",
        reference_answer=None,
        max_score=10,
        question_id=None,
    ):
        """Evaluate an answer and update adaptive interview state."""

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must not be empty.")

        if not isinstance(answer, str):
            raise TypeError("Answer must be a string.")

        if not answer.strip():
            raise ValueError("Answer must not be empty.")

        state = self.dialogue_manager.get_state()

        if state.get("interview_complete", False):
            raise ValueError("The interview is already complete.")

        if (
            question_id is not None
            and question_id in self.asked_question_ids
        ):
            raise ValueError("This question has already been answered.")

        difficulty = self.dialogue_manager.current_difficulty

        # Stage 1: Analyze the answer.
        nlp_analysis = self.nlp_processor.analyze_answer(answer)

        # Stage 2: Evaluate using the LLM, with local fallback.
        evaluation_method = "llm"

        try:
            evaluation = self.llm_evaluator.evaluate_answer(
                question=question,
                answer=answer,
                role=role,
                difficulty=difficulty,
                max_score=max_score,
                reference_answer=reference_answer,
                nlp_analysis=nlp_analysis,
            )

            # Support Pydantic models and dictionaries.
            if hasattr(evaluation, "model_dump"):
                evaluation = evaluation.model_dump()

            if not isinstance(evaluation, dict):
                raise TypeError(
                    "LLM evaluator returned an invalid result."
                )

        except Exception as error:
            print(
                "LLM evaluation unavailable; using local fallback:",
                repr(error),
            )

            evaluation_method = "local_fallback"

            evaluation = self.local_evaluator.evaluate_answer(
                question=question,
                answer=answer,
                role=role,
                difficulty=difficulty,
                max_score=max_score,
                reference_answer=reference_answer,
                nlp_analysis=nlp_analysis,
            )

        if not isinstance(evaluation, dict):
            raise TypeError("Evaluator returned an invalid result.")

        # Avoid modifying an evaluator's shared result dictionary.
        evaluation = dict(evaluation)
        evaluation["evaluation_method"] = evaluation_method

        # Stage 3: Update adaptive dialogue after successful evaluation.
        adaptation = self.dialogue_manager.record_evaluation(
            evaluation
        )

        # Track the question only after evaluation succeeds.
        if question_id is not None:
            self.asked_question_ids.add(question_id)

        self.evaluation_history.append({
            "question_id": question_id,
            "question": question,
            "difficulty": difficulty,
            "evaluation": dict(evaluation),
        })

        return {
            "question": question,
            "question_id": question_id,
            "answer": answer,
            "difficulty": difficulty,
            "nlp_analysis": nlp_analysis,
            "evaluation": evaluation,
            "adaptation": adaptation,
            "interview_state": self.dialogue_manager.get_state(),
            "asked_question_ids": list(self.asked_question_ids),
        }

    def get_interview_state(self):
        """Return the current interview progress."""
        return self.dialogue_manager.get_state()

    def get_asked_question_ids(self):
        """Return a copy of answered question IDs."""
        return set(self.asked_question_ids)

    def get_evaluation_history(self):
        """Return a copy of the evaluation history."""
        return list(self.evaluation_history)
