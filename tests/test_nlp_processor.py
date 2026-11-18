
import unittest

from app.ai.nlp_processor import NLPProcessor


class TestNLPProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = NLPProcessor()

    def test_clean_text(self):
        result = self.processor.clean_text(
            "  PYTHON   is GREAT!  "
        )
        self.assertEqual(result, "python is great")

    def test_tokenize(self):
        result = self.processor.tokenize(
            "Python and SQL"
        )
        self.assertEqual(result, ["python", "and", "sql"])

    def test_extract_keywords(self):
        result = self.processor.extract_keywords(
            "Python is useful for machine learning"
        )
        self.assertIn("python", result)
        self.assertIn("useful", result)
        self.assertNotIn("is", result)

    def test_extract_skills(self):
        result = self.processor.extract_skills(
            "I use Python, SQL, and machine learning."
        )
        self.assertIn("python", result)
        self.assertIn("sql", result)
        self.assertIn("machine learning", result)

    def test_analyze_answer(self):
        result = self.processor.analyze_answer(
            "Python helps build machine learning models."
        )
        self.assertEqual(result["word_count"], 6)
        self.assertIn("python", result["skills"])
        self.assertFalse(result["is_empty"])

    def test_empty_answer(self):
        result = self.processor.analyze_answer("   ")
        self.assertTrue(result["is_empty"])
        self.assertEqual(result["word_count"], 0)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            self.processor.analyze_answer(None)


if __name__ == "__main__":
    unittest.main()
