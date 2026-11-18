
import re
from app.ai.semantic_evaluator import SemanticEvaluator


class LocalEvaluator:
    """Rule-based and semantic fallback evaluator for interview answers."""

    def __init__(self, semantic_evaluator=None):
        self.semantic_evaluator = semantic_evaluator or SemanticEvaluator()

    TOPIC_RULES = {
        "gil": {
            "concepts": [
                ["global interpreter lock", "gil"],
                ["thread", "threads", "threading"],
                [
                    "one thread at a time",
                    "one thread",
                    "one at a time",
                    "single thread",
                    "execute python bytecode",
                ],
            ],
            "optional": [
                "cpython",
                "bytecode",
                "parallel",
                "multithreading",
                "concurrency",
            ],
        },
        "overfitting": {
            "concepts": [
                ["training data", "training set", "train dataset"],
                [
                    "unseen data",
                    "test data",
                    "generalization",
                    "generalisation",
                    "new data",
                ],
                [
                    "noise",
                    "memorize",
                    "memorise",
                    "too closely",
                    "poor generalization",
                    "poor generalisation",
                ],
            ],
            "optional": [
                "regularization",
                "regularisation",
                "dropout",
                "cross validation",
                "early stopping",
                "pruning",
            ],
        },
        "classification_regression": {
            "concepts": [
                [
                    "classification",
                    "class",
                    "classes",
                    "category",
                    "categories",
                    "label",
                    "labels",
                ],
                [
                    "regression",
                    "continuous",
                    "numerical",
                    "numeric",
                    "real valued",
                ],
            ],
            "optional": [
                "spam",
                "price",
                "temperature",
                "prediction",
                "house price",
            ],
        },
        "where_having": {
            "concepts": [
                ["where"],
                ["having"],
                ["rows", "row", "individual records"],
                [
                    "group",
                    "groups",
                    "group by",
                    "aggregate",
                    "aggregation",
                ],
            ],
            "optional": [
                "before",
                "after",
                "filter",
                "condition",
                "aggregate function",
            ],
        },
        "primary_key": {
            "concepts": [
                ["unique", "uniquely", "distinct"],
                ["identify", "identifies", "identifier"],
                ["row", "record", "tuple"],
            ],
            "optional": [
                "table",
                "null",
                "duplicate",
                "column",
            ],
        },
        "decorator": {
            "concepts": [
                ["function", "callable"],
                [
                    "another function",
                    "function as input",
                    "wrapper",
                    "wrap",
                    "takes a function",
                ],
                [
                    "behavior",
                    "behaviour",
                    "modify",
                    "extend",
                    "functionality",
                ],
            ],
            "optional": [
                "return",
                "returns",
                "callable",
                "@",
            ],
        },
        "variable_python": {
            "concepts": [
                ["name", "label", "identifier"],
                ["value", "object", "data"],
                ["store", "reference", "refer", "bind"],
            ],
            "optional": [
                "memory",
                "assignment",
                "assign",
                "object reference",
            ],
        },
    }

    STOP_WORDS = {
        "the", "and", "for", "with", "that", "this", "from",
        "are", "was", "were", "into", "can", "you", "your",
        "have", "has", "its", "their", "they", "will", "which",
        "when", "what", "how", "does", "using", "used", "use",
        "not", "but", "also", "such", "than", "then", "each",
        "a", "an", "in", "of", "to", "is", "it", "as", "on",
        "by", "be", "or", "at",
    }

    def _normalize(self, text):
        """Normalize text while retaining common technical symbols."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9@+#.\s-]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _contains_phrase(self, answer, alternatives):
        """Match whole words or phrases rather than partial words."""
        for phrase in alternatives:
            phrase = self._normalize(phrase)

            if not phrase:
                continue

            pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"

            if re.search(pattern, answer):
                return True

        return False

    def _find_topic(self, question):
        """Identify supported topics from the question."""
        q = self._normalize(question)

        if "gil" in q or "global interpreter lock" in q:
            return "gil"

        if "overfitting" in q or "overfit" in q:
            return "overfitting"

        if "classification" in q and "regression" in q:
            return "classification_regression"

        if "where" in q and "having" in q and "sql" in q:
            return "where_having"

        if "primary key" in q:
            return "primary_key"

        if "decorator" in q:
            return "decorator"

        if "variable" in q and "python" in q:
            return "variable_python"

        return None

    def _reference_coverage(self, answer, reference_answer):
        """
        Estimate lexical concept overlap with a reference answer.

        This does not establish semantic correctness.
        """
        def tokenize(text):
            return set(
                re.findall(r"[a-z0-9+#]+", text.lower())
            )

        # Normalize common technical equivalents.
        replacements = [
            (r"\blast in first out\b", "lifo"),
            (r"\bfirst in first out\b", "fifo"),
            (r"\bpushes\b", "push"),
            (r"\bpops\b", "pop"),
            (r"\binserts\b", "insert"),
            (r"\bremoves\b", "remove"),
            (r"\bitems\b", "item"),
            (r"\belements\b", "element"),
            (r"\bvalues\b", "value"),
            (r"\brows\b", "row"),
            (r"\brecords\b", "record"),
        ]

        def normalize_terms(text):
            text = self._normalize(text)

            for pattern, replacement in replacements:
                text = re.sub(pattern, replacement, text)

            return tokenize(text)

        answer_words = normalize_terms(answer)
        reference_words = normalize_terms(reference_answer)

        meaningful_reference = {
            word
            for word in reference_words
            if len(word) > 2 and word not in self.STOP_WORDS
        }

        if not meaningful_reference:
            return 0.4

        overlap = (
            len(meaningful_reference & answer_words)
            / len(meaningful_reference)
        )

        # Recognize abbreviations for common technical expressions.
        normalized_reference = self._normalize(reference_answer)
        normalized_answer = self._normalize(answer)

        if (
            "last in first out" in normalized_reference
            and "lifo" in normalized_answer
        ):
            overlap = min(1.0, overlap + 0.25)

        if (
            "first in first out" in normalized_reference
            and "fifo" in normalized_answer
        ):
            overlap = min(1.0, overlap + 0.25)

        return min(1.0, overlap)

    def evaluate_answer(
        self,
        question,
        answer,
        role="General",
        difficulty="Intermediate",
        max_score=10,
        reference_answer=None,
        nlp_analysis=None,
    ):
        """Evaluate an answer and return a consistent result dictionary."""

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must not be empty.")

        if (
            isinstance(max_score, bool)
            or not isinstance(max_score, (int, float))
        ):
            raise ValueError("Maximum score must be numeric.")

        if max_score <= 0:
            raise ValueError("Maximum score must be greater than zero.")

        if not isinstance(answer, str) or not answer.strip():
            return {
                "score": 0,
                "max_score": max_score,
                "correctness": 0,
                "relevance": 0,
                "completeness": 0,
                "clarity": 0,
                "strengths": [],
                "improvements": ["Please provide an answer."],
                "feedback": "No answer was provided.",
                "evaluation_method": "local_fallback",
            }

        normalized_answer = self._normalize(answer)
        word_count = len(normalized_answer.split())

        topic = self._find_topic(question)
        matched_concepts = []
        optional_matches = []
        total_concepts = 0
        coverage = 0.0

        semantic_info = None

        if topic:
            rules = self.TOPIC_RULES[topic]
            total_concepts = len(rules["concepts"])

            for alternatives in rules["concepts"]:
                if self._contains_phrase(
                    normalized_answer, alternatives
                ):
                    matched_concepts.append(alternatives[0])

            for concept in rules["optional"]:
                if self._contains_phrase(
                    normalized_answer, [concept]
                ):
                    optional_matches.append(concept)

            coverage = len(matched_concepts) / total_concepts
            correctness = round(coverage * 10)

            if matched_concepts and optional_matches:
                correctness = min(10, correctness + 1)

            # If reference answer is also present, calculate semantic alignment
            if isinstance(reference_answer, str) and reference_answer.strip():
                semantic_info = self.semantic_evaluator.compute_similarity(
                    answer, reference_answer
                )

        elif (
            isinstance(reference_answer, str)
            and reference_answer.strip()
        ):
            coverage = self._reference_coverage(
                normalized_answer,
                self._normalize(reference_answer),
            )
            # Enhancement 1: Calculate dense vector semantic similarity
            semantic_info = self.semantic_evaluator.compute_similarity(
                answer, reference_answer
            )
            sem_sim = semantic_info.get("similarity", 0.0)

            # Effective coverage rewards both technical concept aliases and semantic alignment
            effective_score = max(coverage, sem_sim)
            correctness = round(effective_score * 10)

        else:
            # Unknown questions cannot be reliably graded by keywords.
            correctness = 4 if word_count >= 8 else 2

        # Estimate relevance from topic evidence or reference overlap.
        if topic and total_concepts:
            relevance = min(
                10,
                round(5 + 5 * len(matched_concepts) / total_concepts),
            )
        elif (
            isinstance(reference_answer, str)
            and reference_answer.strip()
        ):
            sem_sim = semantic_info.get("similarity", 0.0) if semantic_info else coverage
            effective_overlap = max(coverage, sem_sim)
            relevance = round(3 + 7 * effective_overlap)
        else:
            relevance = 5 if word_count >= 5 else 2

        # Word count is only a rough completeness indicator.
        if word_count < 5:
            completeness = 3
        elif word_count < 12:
            completeness = 6
        elif word_count < 25:
            completeness = 8
        else:
            completeness = 9

        # Basic structural clarity estimate.
        clarity = 4 if word_count < 5 else 6

        if any(mark in answer for mark in [".", ";", "\n"]):
            clarity = min(10, clarity + 1)

        # Weighted score out of 10, then scaled to max_score.
        raw_score = (
            correctness * 0.60
            + relevance * 0.15
            + completeness * 0.15
            + clarity * 0.10
        )

        score = round(raw_score * max_score / 10, 1)
        score = max(0, min(max_score, score))

        strengths = []
        improvements = []

        if matched_concepts:
            strengths.append(
                "Relevant concepts identified: "
                + ", ".join(matched_concepts)
                + "."
            )

        if correctness >= 7:
            strengths.append(
                "Your answer covers several important concepts."
            )

        if word_count >= 8:
            strengths.append(
                "You provided an explanation with supporting detail."
            )

        if topic:
            missing_concepts = [
                alternatives[0]
                for alternatives in self.TOPIC_RULES[topic]["concepts"]
                if not self._contains_phrase(
                    normalized_answer, alternatives
                )
            ]

            if missing_concepts:
                improvements.append(
                    "Consider explaining these additional aspects: "
                    + ", ".join(missing_concepts)
                    + "."
                )

        elif (
            isinstance(reference_answer, str)
            and reference_answer.strip()
            and correctness < 8
        ):
            improvements.append(
                "Compare your answer with the reference and include "
                "any important missing concepts."
            )

        if word_count < 8:
            improvements.append(
                "Add a brief explanation or a relevant example if needed."
            )

        if not improvements:
            improvements.append(
                "Where relevant, include an example or explain "
                "the practical significance."
            )

        return {
            "score": score,
            "max_score": max_score,
            "correctness": correctness,
            "relevance": relevance,
            "completeness": completeness,
            "clarity": clarity,
            "strengths": strengths,
            "improvements": improvements,
            "feedback": (
                "This score was produced by a local rule-based and semantic evaluator. "
                "It is an estimate and may not recognize every valid "
                "alternative explanation."
            ),
            "evaluation_method": "local_fallback",
            "semantic_similarity": (
                semantic_info.get("similarity", 0.0) if semantic_info else None
            ),
            "semantic_engine": (
                semantic_info.get("engine", "none") if semantic_info else "none"
            ),
        }
