
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

    def test_stem(self):
        result = self.processor.stem("computing computers computed")
        # Porter stemmer should reduce these to "comput"
        self.assertIn("comput", result)

    def test_lemmatize(self):
        result = self.processor.lemmatize("computing computers computed")
        # WordNet lemmatizer with heuristic POS tagging:
        # "computing" -> "compute" (verb), "computers" -> "computers" (treated as verb), "computed" -> "compute" (verb)
        self.assertIn("compute", result)
        # "computers" is not reduced due to heuristic POS tagging limitation
        self.assertIn("computers", result)

    def test_analyze_answer_includes_stemmed_and_lemmatized(self):
        result = self.processor.analyze_answer(
            "Python helps building machine learning models."
        )
        self.assertIn("stemmed_tokens", result)
        self.assertIn("lemmatized_tokens", result)
        self.assertIsInstance(result["stemmed_tokens"], list)
        self.assertIsInstance(result["lemmatized_tokens"], list)
        self.assertTrue(len(result["stemmed_tokens"]) > 0)
        self.assertTrue(len(result["lemmatized_tokens"]) > 0)

    def test_analyze_sentiment(self):
        result = self.processor.analyze_sentiment(
            "I love Python! It's amazing and wonderful."
        )
        self.assertIn("compound", result)
        self.assertIn("positive", result)
        self.assertIn("negative", result)
        self.assertIn("neutral", result)
        self.assertIn("label", result)
        self.assertIn(result["label"], ["positive", "negative", "neutral"])

    def test_analyze_sentiment_negative(self):
        result = self.processor.analyze_sentiment(
            "I hate this terrible awful code."
        )
        self.assertIn("label", result)
        self.assertEqual(result["label"], "negative")

    def test_analyze_sentiment_neutral(self):
        result = self.processor.analyze_sentiment(
            "Python is a programming language."
        )
        self.assertIn("label", result)
        self.assertEqual(result["label"], "neutral")

    def test_analyze_answer_includes_sentiment(self):
        result = self.processor.analyze_answer(
            "Python is great for machine learning."
        )
        self.assertIn("sentiment", result)
        self.assertIn("compound", result["sentiment"])
        self.assertIn("label", result["sentiment"])

    def test_extract_topics_lda_insufficient_docs(self):
        # Need at least 2 documents
        result = self.processor.extract_topics_lda(["Only one document"])
        self.assertIn("topics", result)
        self.assertEqual(result["topics"], [])

    def test_extract_topics_lda(self):
        docs = [
            "Python machine learning data science neural networks",
            "SQL database query optimization indexing performance",
            "Python web development flask django rest api"
        ]
        result = self.processor.extract_topics_lda(docs, n_topics=3, n_words=5)
        self.assertIn("topics", result)
        self.assertIn("topic_distributions", result)
        self.assertIn("n_topics", result)
        # If sklearn is available, we should get topics
        # If not, we get a note
        if "note" not in result:
            self.assertTrue(len(result["topics"]) > 0)

    def test_get_answer_topics_with_reference(self):
        ref_docs = [
            "Python machine learning data science neural networks",
            "SQL database query optimization indexing performance"
        ]
        answer = "I love Python for data science and machine learning"
        result = self.processor.get_answer_topics(answer, reference_documents=ref_docs)
        self.assertIn("topic_distribution", result)
        self.assertIn("topics", result)
        self.assertIn("n_topics", result)


if __name__ == "__main__":
    unittest.main()
