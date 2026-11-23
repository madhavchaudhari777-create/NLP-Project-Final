"""
Unit tests for Enhancement 1: Semantic Evaluator Module.
"""

import unittest
from app.ai.semantic_evaluator import SemanticEvaluator


class TestSemanticEvaluator(unittest.TestCase):

    def setUp(self):
        # Instantiate semantic evaluator in deterministic vector mode for fast testing
        self.evaluator = SemanticEvaluator(use_transformers=False)

    def test_empty_student_answer_returns_zero(self):
        result = self.evaluator.compute_similarity("", "A stack is LIFO.")
        self.assertEqual(result["similarity"], 0.0)
        self.assertFalse(result["is_aligned"])
        self.assertEqual(result["engine"], "none")

    def test_empty_reference_answer_returns_zero(self):
        result = self.evaluator.compute_similarity("A stack is LIFO.", "")
        self.assertEqual(result["similarity"], 0.0)
        self.assertFalse(result["is_aligned"])

    def test_identical_technical_answers_score_high(self):
        text = "A stack is a linear data structure that follows the Last In First Out (LIFO) principle."
        result = self.evaluator.compute_similarity(text, text)
        self.assertGreaterEqual(result["similarity"], 0.95)
        self.assertTrue(result["is_aligned"])
        self.assertEqual(result["tier"], "High Alignment")

    def test_semantically_related_answers(self):
        ref = "Overfitting occurs when a machine learning model learns the training noise instead of generalized patterns."
        ans = "Overfitting is when a model memorizes the training data and fails to generalize to unseen test data."
        result = self.evaluator.compute_similarity(ans, ref)
        self.assertGreater(result["similarity"], 0.15)
        self.assertIn(result["engine"], ["statistical_vector_tfidf", "sentence_transformers_minilm"])

    def test_completely_dissimilar_answers_score_low(self):
        ref = "A primary key uniquely identifies each record in a relational database table."
        ans = "Photosynthesis is the process by which green plants use sunlight to synthesize nutrients."
        result = self.evaluator.compute_similarity(ans, ref)
        self.assertLess(result["similarity"], 0.20)
        self.assertFalse(result["is_aligned"])

    def test_score_scaling(self):
        ref = "Python lists are mutable ordered sequences."
        ans = "Python lists are mutable ordered sequences."
        score = self.evaluator.evaluate_semantic_score(ans, ref, max_score=10.0)
        self.assertGreaterEqual(score, 9.0)
        self.assertLessEqual(score, 10.0)

    def test_score_scaling_custom_max(self):
        ref = "SQL WHERE filters rows before grouping."
        ans = "SQL WHERE filters records prior to GROUP BY aggregation."
        score = self.evaluator.evaluate_semantic_score(ans, ref, max_score=5.0)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 5.0)


if __name__ == "__main__":
    unittest.main()
