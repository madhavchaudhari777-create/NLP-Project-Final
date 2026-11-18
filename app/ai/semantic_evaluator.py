"""
Semantic Evaluator Module
Part of Enhancement 1: Dense Vector Semantic Representations & Embeddings

Computes semantic similarity between candidate responses and technical reference answers
using dense embeddings (Sentence-Transformers all-MiniLM-L6-v2) or statistical
n-gram vector cosine similarity.
"""

import math
import re
from typing import Dict, Any, List, Optional

# Attempt optional PyTorch & Transformers imports safely
try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False
    torch = None

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
    and reference technical answers.
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        use_transformers: bool = True,
        model_name: Optional[str] = None,
        allow_download: bool = False
    ):
        self.model_name = model_name or self.MODEL_NAME
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        self.allow_download = allow_download
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if (torch and torch.cuda.is_available()) else "cpu"
        self._is_transformer_loaded = False
        self._load_attempted = False

    def _lazy_load_transformer(self) -> bool:
        """Safely attempt to load tokenizer and model without blocking on network retries if offline."""
        if self._load_attempted:
            return self._is_transformer_loaded

        self._load_attempted = True
        if not self.use_transformers:
            return False

        # 1. First attempt to load from local cache with local_files_only=True
        # This is instantaneous and avoids multi-second network retry loops when offline.
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                local_files_only=True
            )
            self.model = AutoModel.from_pretrained(
                self.model_name,
                local_files_only=True
            )
            self.model.to(self.device)
            self.model.eval()
            self._is_transformer_loaded = True
            return True
        except Exception:
            pass

        # 2. Only attempt online download if explicitly permitted
        if self.allow_download:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    local_files_only=False
                )
                self.model = AutoModel.from_pretrained(
                    self.model_name,
                    local_files_only=False
                )
                self.model.to(self.device)
                self.model.eval()
                self._is_transformer_loaded = True
                return True
            except Exception:
                self._is_transformer_loaded = False
                return False

        self._is_transformer_loaded = False
        return False

    @staticmethod
    def _mean_pooling(model_output, attention_mask):
        """Mean Pooling - Take attention mask into account for correct averaging."""
        token_embeddings = model_output[0]  # First element contains hidden state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def _transformer_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity using 384-dimensional dense transformer embeddings."""
        if not self._lazy_load_transformer():
            raise RuntimeError("Transformer model not loaded.")

        encoded = self.tokenizer(
            [text1, text2],
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )
        encoded = {k: v.to(self.device) for k, v in encoded.items()}

        with torch.no_grad():
            outputs = self.model(**encoded)

        sentence_embeddings = self._mean_pooling(outputs, encoded["attention_mask"])
        # Normalize vectors to unit length
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        sim = F.cosine_similarity(sentence_embeddings[0:1], sentence_embeddings[1:2]).item()
        return max(0.0, min(1.0, float(sim)))

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
                "engine": "none",
                "tier": "Empty answer",
                "is_aligned": False
            }

        if not reference_answer or not reference_answer.strip():
            return {
                "similarity": 0.0,
                "engine": "none",
                "tier": "No reference provided",
                "is_aligned": False
            }

        engine = "statistical_vector_tfidf"
        similarity = 0.0

        if self.use_transformers and self._lazy_load_transformer():
            try:
                similarity = self._transformer_similarity(student_answer, reference_answer)
                engine = "sentence_transformers_minilm"
            except Exception:
                similarity = self._statistical_vector_similarity(student_answer, reference_answer)
                engine = "statistical_vector_fallback"
        else:
            similarity = self._statistical_vector_similarity(student_answer, reference_answer)

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
