
import unittest

from app.ai.dialogue_manager import DialogueManager


class TestDialogueManager(unittest.TestCase):

    def test_initial_state(self):
        manager = DialogueManager("Intermediate", 5)
        state = manager.get_state()

        self.assertEqual(state["current_difficulty"], "Intermediate")
        self.assertEqual(state["questions_remaining"], 5)
        self.assertFalse(state["interview_complete"])

    def test_high_score_increases_difficulty(self):
        manager = DialogueManager("Beginner", 3)

        manager.record_evaluation({"score": 9, "max_score": 10})

        state = manager.get_state()
        self.assertEqual(state["current_difficulty"], "Intermediate")

    def test_low_score_decreases_difficulty(self):
        manager = DialogueManager("Advanced", 3)

        manager.record_evaluation({"score": 3, "max_score": 10})

        self.assertEqual(
            manager.get_state()["current_difficulty"],
            "Intermediate"
        )

    def test_difficulty_does_not_exceed_advanced(self):
        manager = DialogueManager("Advanced", 3)

        manager.record_evaluation({"score": 10, "max_score": 10})

        self.assertEqual(
            manager.get_state()["current_difficulty"],
            "Advanced"
        )

    def test_score_normalization(self):
        manager = DialogueManager("Intermediate", 3)

        result = manager.record_evaluation({
            "score": 16,
            "max_score": 20
        })

        self.assertEqual(result["normalized_score"], 8.0)

    def test_interview_completion(self):
        manager = DialogueManager("Beginner", 2)

        manager.record_evaluation({"score": 6, "max_score": 10})
        result = manager.record_evaluation({
            "score": 6,
            "max_score": 10
        })

        self.assertTrue(result["interview_complete"])
        self.assertEqual(manager.get_state()["questions_remaining"], 0)

    def test_cannot_evaluate_after_completion(self):
        manager = DialogueManager("Beginner", 1)

        manager.record_evaluation({"score": 6, "max_score": 10})

        with self.assertRaises(ValueError):
            manager.record_evaluation({
                "score": 7,
                "max_score": 10
            })

    def test_invalid_score_is_rejected(self):
        manager = DialogueManager("Beginner", 3)

        with self.assertRaises(ValueError):
            manager.record_evaluation({
                "score": 12,
                "max_score": 10
            })


if __name__ == "__main__":
    unittest.main()
