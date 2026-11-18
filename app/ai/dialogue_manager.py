
class DialogueManager:
    """Manage interview progress and adapt question difficulty."""

    DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]

    def __init__(self, initial_difficulty="Intermediate",
                 total_questions=5):
        if initial_difficulty not in self.DIFFICULTY_LEVELS:
            raise ValueError("Invalid initial difficulty.")

        if (
            not isinstance(total_questions, int)
            or isinstance(total_questions, bool)
            or total_questions < 1
        ):
            raise ValueError("total_questions must be a positive integer.")

        self.current_difficulty = initial_difficulty
        self.total_questions = total_questions
        self.answers_evaluated = 0
        self.score_history = []
        self.performance_history = []

    def record_evaluation(self, evaluation):
        """Record one evaluation and update adaptive difficulty."""

        if self.answers_evaluated >= self.total_questions:
            raise ValueError("The interview is already complete.")

        score = evaluation.get("score")
        max_score = evaluation.get("max_score", 10)

        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not isinstance(max_score, (int, float))
            or isinstance(max_score, bool)
            or max_score <= 0
            or not 0 <= score <= max_score
        ):
            raise ValueError("Invalid evaluation score.")

        normalized_score = (score / max_score) * 10

        self.score_history.append(normalized_score)
        self.answers_evaluated += 1

        # Use the latest two answers when possible to reduce
        # overreaction to one unusually good or poor answer.
        recent_scores = self.score_history[-2:]
        average_score = sum(recent_scores) / len(recent_scores)

        previous_difficulty = self.current_difficulty
        current_index = self.DIFFICULTY_LEVELS.index(
            self.current_difficulty
        )

        if average_score >= 8:
            current_index = min(
                current_index + 1,
                len(self.DIFFICULTY_LEVELS) - 1
            )
        elif average_score < 5:
            current_index = max(current_index - 1, 0)

        self.current_difficulty = self.DIFFICULTY_LEVELS[current_index]

        result = {
            "question_number": self.answers_evaluated,
            "normalized_score": round(normalized_score, 2),
            "recent_average": round(average_score, 2),
            "previous_difficulty": previous_difficulty,
            "next_difficulty": self.current_difficulty,
            "interview_complete": (
                self.answers_evaluated >= self.total_questions
            ),
        }

        self.performance_history.append(result)
        return result

    def get_state(self):
        """Return the current interview state."""

        average = (
            sum(self.score_history) / len(self.score_history)
            if self.score_history else 0.0
        )

        return {
            "current_difficulty": self.current_difficulty,
            "total_questions": self.total_questions,
            "answers_evaluated": self.answers_evaluated,
            "questions_remaining": (
                self.total_questions - self.answers_evaluated
            ),
            "average_score": round(average, 2),
            "interview_complete": (
                self.answers_evaluated >= self.total_questions
            ),
            "performance_history": self.performance_history.copy(),
        }
