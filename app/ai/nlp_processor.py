
import re
from collections import Counter


class NLPProcessor:
    """Process interview answers and extract useful text features."""

    def __init__(self):
        self.stop_words = {
            "a", "an", "the", "is", "am", "are", "was", "were",
            "be", "been", "being", "to", "of", "in", "on", "at",
            "for", "and", "or", "but", "with", "by", "as", "it",
            "this", "that", "these", "those", "i", "we", "you",
            "he", "she", "they", "my", "our", "your", "their",
            "do", "does", "did", "have", "has", "had", "can",
            "could", "would", "should", "will", "from", "into"
        }

        self.technical_skills = {
            "python", "java", "c++", "sql", "machine learning",
            "deep learning", "artificial intelligence", "nlp",
            "natural language processing", "flask", "django",
            "tensorflow", "pytorch", "scikit-learn", "numpy",
            "pandas", "data science", "neural networks",
            "database", "html", "css", "javascript", "rest api",
            "api", "classification", "regression", "clustering",
            "random forest", "decision tree", "llm", "rag"
        }

    def clean_text(self, text):
        """Normalize text while preserving common technical symbols."""

        if not isinstance(text, str):
            raise TypeError("Answer must be a string.")

        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-z0-9+#.\s/-]", "", text)

        return text

    def tokenize(self, text):
        """Split normalized text into tokens."""

        cleaned_text = self.clean_text(text)
        return re.findall(r"[a-z0-9]+(?:[+#.-][a-z0-9+#.-]*)*", cleaned_text)

    def extract_keywords(self, text):
        """Extract informative words, excluding common stop words."""

        tokens = self.tokenize(text)

        keywords = [
            token for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]

        return keywords

    def extract_skills(self, text):
        """Find known technical skills mentioned in the answer."""

        cleaned_text = self.clean_text(text)
        found_skills = []

        # Match longer phrases before shorter ones.
        for skill in sorted(
            self.technical_skills,
            key=len,
            reverse=True
        ):
            pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"

            if re.search(pattern, cleaned_text):
                found_skills.append(skill)

        return sorted(found_skills)

    def analyze_answer(self, text):
        """Return structured NLP features for an interview answer."""

        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        keywords = self.extract_keywords(cleaned_text)
        skills = self.extract_skills(cleaned_text)

        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "tokens": tokens,
            "keywords": keywords,
            "skills": skills,
            "word_count": len(tokens),
            "keyword_frequency": dict(Counter(keywords)),
            "is_empty": len(cleaned_text) == 0
        }
