"""
Semantic Evaluator Module - Vercel Compatible Version
Computes semantic similarity using statistical TF-IDF + character n-gram cosine similarity.
No heavy ML dependencies (no PyTorch, Transformers, or Sentence-Transformers).
"""

import math
import re
from typing import Dict, Any, List, Optional

# Attempt scikit-learn for robust statistical fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


class SemanticEvaluator:
    """
    Evaluates semantic meaning and conceptual alignment between candidate answers
    and reference technical answers using statistical methods only.
    Lightweight version for serverless deployment (Vercel compatible).
    """

    def __init__(
        self,
        use_transformers: bool = False,  # Disabled for Vercel
        model_name: Optional[str] = None,
        allow_download: bool = False
    ):
        # Vercel-compatible: always use statistical fallback
        self.use_transformers = False
        self.model_name = model_name
        self.allow_download = False
        self.tokenizer = None
        self.model = None
        self._is_transformer_loaded = False
        self._load_attempted = True

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text for vector analysis."""
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9+#.\s/-]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _statistical_vector_similarity(self, text1: str, text2: str) -> float:
        """
        Robust statistical word + character n-gram cosine similarity.
        Handles morphological variation, stemming, and domain vocabulary alignment.
        """
        c1 = self._clean_text(text1)
        c2 = self._clean_text(text2)

        if not c1 or not c2:
            return 0.0

        if SKLEARN_AVAILABLE:
            try:
                # 1. Word unigram TF-IDF
                v_word = TfidfVectorizer(ngram_range=(1, 1), stop_words="english")
                w_sim = float(cosine_similarity(v_word.fit_transform([c1, c2]))[0][1])

                # 2. Sub-word character n-gram TF-IDF (3-4 char boundaries)
                v_char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4))
                c_sim = float(cosine_similarity(v_char.fit_transform([c1, c2]))[0][1])

                # Combined hybrid statistical similarity
                combined = 0.5 * w_sim + 0.5 * c_sim
                return max(0.0, min(1.0, float(combined)))
            except Exception:
                pass

        # Pure Python fallback: Set-based Jaccard + Character N-gram overlap
        words1 = set(c1.split())
        words2 = set(c2.split())
        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0.0

        # Substring / character trigrams for morphological variations
        tri1 = {c1[i:i+3] for i in range(max(0, len(c1)-2))}
        tri2 = {c2[i:i+3] for i in range(max(0, len(c2)-2))}
        tri_sim = len(tri1 & tri2) / max(1, len(tri1 | tri2))

        return round(0.6 * jaccard + 0.4 * tri_sim, 3)

    def compute_similarity(self, student_answer: str, reference_answer: str) -> Dict[str, Any]:
        """
        Compute semantic similarity between candidate answer and reference answer.
        Returns a dictionary with similarity score, engine used, and qualitative rating.
        """
        if not student_answer or not student_answer.strip():
            return {
                "similarity": 0.0,
                "engine": "statistical_tfidf",
                "tier": "Empty answer",
                "is_aligned": False
            }

        if not reference_answer or not reference_answer.strip():
            return {
                "similarity": 0.0,
                "engine": "statistical_tfidf",
                "tier": "No reference provided",
                "is_aligned": False
            }

        similarity = self._statistical_vector_similarity(student_answer, reference_answer)
        engine = "statistical_tfidf"

        # Calibrate alignment tier based on cosine similarity
        if similarity >= 0.80:
            tier = "High Alignment"
            is_aligned = True
        elif similarity >= 0.60:
            tier = "Moderate Alignment"
            is_aligned = True
        elif similarity >= 0.35:
            tier = "Partial Conceptual Overlap"
            is_aligned = False
        else:
            tier = "Low Semantic Alignment"
            is_aligned = False

        return {
            "similarity": round(similarity, 3),
            "engine": engine,
            "tier": tier,
            "is_aligned": is_aligned
        }

    def evaluate_semantic_score(
        self,
        student_answer: str,
        reference_answer: str,
        max_score: float = 10.0
    ) -> float:
        """Return a scaled score from 0 to max_score based on semantic similarity."""
        result = self.compute_similarity(student_answer, reference_answer)
        sim = result["similarity"]
        raw = sim * max_score
        return round(max(0.0, min(max_score, raw)), 1)