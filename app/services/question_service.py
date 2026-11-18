
import json
import os
import random

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class QuestionService:
    """Select relevant questions and generate additional ones when needed."""

    QUESTION_BANK = [
        {
            "id": 1,
            "question": "What is a variable in Python?",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Beginner",
            "reference_answer": (
                "A variable is a name that refers to a value or object. "
                "Python determines the type dynamically."
            ),
        },
        {
            "id": 2,
            "question": "What is the difference between a list and a tuple?",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Beginner",
            "reference_answer": (
                "Lists are mutable, while tuples are immutable. "
                "Both can store multiple items."
            ),
        },
        {
            "id": 3,
            "question": "Explain decorators in Python.",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Intermediate",
            "reference_answer": (
                "A decorator wraps a function or class to extend or "
                "modify its behavior without directly changing its code."
            ),
        },
        {
            "id": 4,
            "question": "How does a Python generator work?",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Intermediate",
            "reference_answer": (
                "A generator yields values lazily, usually using yield, "
                "which can reduce memory usage for large sequences."
            ),
        },
        {
            "id": 5,
            "question": "Explain Python's Global Interpreter Lock.",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Advanced",
            "reference_answer": (
                "In conventional CPython builds, the GIL generally "
                "allows only one thread at a time to execute Python "
                "bytecode. Its effects depend on the workload and build."
            ),
        },
        {
            "id": 6,
            "question": "What is supervised machine learning?",
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml", "python"],
            "difficulty": "Beginner",
            "reference_answer": (
                "Supervised learning trains a model using labeled "
                "examples to predict outputs for new inputs."
            ),
        },
        {
            "id": 7,
            "question": (
                "What is the difference between classification and regression?"
            ),
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml"],
            "difficulty": "Beginner",
            "reference_answer": (
                "Classification predicts categories, while regression "
                "predicts numerical values."
            ),
        },
        {
            "id": 8,
            "question": "Explain overfitting and how to reduce it.",
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml"],
            "difficulty": "Intermediate",
            "reference_answer": (
                "Overfitting occurs when a model learns training-specific "
                "patterns that do not generalize. Regularization, "
                "cross-validation, more data, and simpler models can help."
            ),
        },
        {
            "id": 9,
            "question": (
                "Why might you choose a random forest over a single decision tree?"
            ),
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml"],
            "difficulty": "Advanced",
            "reference_answer": (
                "A random forest combines multiple randomized trees, "
                "often reducing variance and improving generalization "
                "compared with a single decision tree."
            ),
        },
        {
            "id": 10,
            "question": "What is a primary key in a database?",
            "role": "software developer",
            "skills": ["sql", "database"],
            "difficulty": "Beginner",
            "reference_answer": (
                "A primary key uniquely identifies each row in a table "
                "and cannot contain NULL values."
            ),
        },
        {
            "id": 11,
            "question": "Explain the difference between WHERE and HAVING in SQL.",
            "role": "software developer",
            "skills": ["sql", "database"],
            "difficulty": "Intermediate",
            "reference_answer": (
                "WHERE filters rows before grouping, while HAVING "
                "filters groups after GROUP BY."
            ),
        },
        {
            "id": 12,
            "question": "What is the difference between a process and a thread?",
            "role": "software developer",
            "skills": ["programming", "operating systems"],
            "difficulty": "Advanced",
            "reference_answer": (
                "Processes have separate address spaces by default, "
                "while threads within a process share memory and resources."
            ),
        },
    ]

    VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}
    MAX_QUESTIONS = 10

    def __init__(self, question_bank=None, rng=None, client=None, model=None):
        self.question_bank = (
            list(question_bank)
            if question_bank is not None
            else list(self.QUESTION_BANK)
        )
        self.rng = rng or random.Random()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = client

    @staticmethod
    def _normalize(value):
        return str(value).strip().lower()

    def _generate_questions(
        self, role, skills, difficulty, number_needed, existing_questions
    ):
        """Generate additional questions using the configured OpenAI model."""

        if number_needed <= 0:
            return []

        if self.client is None:
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key or api_key == "paste_your_actual_key_here":
                raise RuntimeError(
                    "More questions are needed, but AI generation is "
                    "unavailable. Add a valid OPENAI_API_KEY and ensure "
                    "your API account has available credits."
                )

            self.client = OpenAI(api_key=api_key)

        prompt = {
            "target_role": role,
            "skills": skills,
            "difficulty": difficulty,
            "number_of_questions": number_needed,
            "existing_questions": [
                item["question"] for item in existing_questions
            ],
            "requirements": [
                "Generate distinct technical interview questions.",
                "Match the requested role and difficulty.",
                "Use the supplied skills when relevant.",
                "Provide a technically correct reference answer for each.",
                "Avoid repeating or merely rewording existing questions.",
                "Return exactly the requested number of questions.",
            ],
        }

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=(
                    "Create high-quality technical interview questions. "
                    "Return valid JSON with a top-level 'questions' array. "
                    "Each item must contain 'question' and 'reference_answer'."
                ),
                input=json.dumps(prompt),
            )
            parsed = json.loads(response.output_text)
            generated = parsed["questions"]
        except Exception as exc:
            raise RuntimeError(
                "AI question generation failed. Check API access, "
                "available credits, network connection, and model settings."
            ) from exc

        if not isinstance(generated, list):
            raise RuntimeError("The AI returned an invalid question list.")

        seen = {
            self._normalize(item["question"])
            for item in existing_questions
        }
        results = []

        for item in generated:
            if not isinstance(item, dict):
                continue

            question = item.get("question")
            answer = item.get("reference_answer")

            if (
                not isinstance(question, str)
                or not question.strip()
                or not isinstance(answer, str)
                or not answer.strip()
            ):
                continue

            normalized = self._normalize(question)

            if normalized in seen:
                continue

            seen.add(normalized)
            results.append({
                "id": f"generated-{len(results) + 1}",
                "question": question.strip(),
                "role": self._normalize(role),
                "skills": list(skills),
                "difficulty": difficulty,
                "reference_answer": answer.strip(),
            })

            if len(results) >= number_needed:
                break

        if len(results) < number_needed:
            raise RuntimeError(
                f"AI generated {len(results)} of "
                f"{number_needed} required questions. Please try again."
            )

        return results

    def get_questions(
        self,
        role,
        skills=None,
        difficulty="Beginner",
        number_of_questions=5,
        exclude_ids=None,
    ):
        """Return the requested number of distinct interview questions."""

        if not isinstance(role, str) or not role.strip():
            raise ValueError("Role must not be empty.")

        if difficulty not in self.VALID_DIFFICULTIES:
            raise ValueError(
                "Difficulty must be Beginner, Intermediate, or Advanced."
            )

        if (
            not isinstance(number_of_questions, int)
            or isinstance(number_of_questions, bool)
            or number_of_questions < 1
        ):
            raise ValueError(
                "number_of_questions must be a positive integer."
            )

        # Reject oversized requests before any API call.
        if number_of_questions > self.MAX_QUESTIONS:
            raise ValueError(
                f"Only up to {self.MAX_QUESTIONS} questions can be requested; "
                f"{number_of_questions} requested."
            )

        if skills is None:
            skills = []

        exclude_ids = set(exclude_ids or [])
        requested_role = self._normalize(role)
        requested_skills = {
            self._normalize(skill)
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        }

        available = [
            item for item in self.question_bank
            if item.get("id") not in exclude_ids
        ]

        def matches_skill(item):
            item_skills = {
                self._normalize(skill)
                for skill in item.get("skills", [])
            }
            return bool(requested_skills.intersection(item_skills))

        # Rank existing questions by relevance and requested difficulty.
        def relevance(item):
            item_role = self._normalize(item.get("role", ""))
            item_difficulty = item.get("difficulty")

            score = 0

            if item_role == requested_role:
                score += 100
            elif item_role == "general":
                score += 60

            if matches_skill(item):
                score += 40

            if item_difficulty == difficulty:
                score += 30

            return score

        candidates = sorted(
            available,
            key=relevance,
            reverse=True,
        )

        # Shuffle questions with equal relevance to add variety.
        grouped = {}
        for item in candidates:
            grouped.setdefault(relevance(item), []).append(item)

        candidates = []
        for score in sorted(grouped, reverse=True):
            group = grouped[score]
            self.rng.shuffle(group)
            candidates.extend(group)

        # Prefer questions at the requested difficulty, but use other
        # existing questions if needed so the selected count can be met.
        # Prefer exact difficulty matches first.
        exact_difficulty = [
            item for item in candidates
            if item.get("difficulty") == difficulty
        ]

        other_difficulties = [
            item for item in candidates
            if item.get("difficulty") != difficulty
        ]

        selected = exact_difficulty[:number_of_questions]

        # Fill any remaining slots with other available questions only
        # when exact-difficulty questions are insufficient.
        if len(selected) < number_of_questions:
            selected_ids = {item["id"] for item in selected}

            for item in other_difficulties:
                if item["id"] not in selected_ids:
                    selected.append(item)
                    selected_ids.add(item["id"])

                if len(selected) >= number_of_questions:
                    break

        if len(selected) < number_of_questions:
            additional = self._generate_questions(
                role=role,
                skills=skills,
                difficulty=difficulty,
                number_needed=number_of_questions - len(selected),
                existing_questions=selected,
            )
            selected.extend(additional)

        if len(selected) < number_of_questions:
            raise ValueError(
                f"Only {len(selected)} questions are available; "
                f"{number_of_questions} requested."
            )

        return [
            {
                "id": item["id"],
                "question": item["question"],
                "role": item["role"],
                "skills": list(item.get("skills", [])),
                "difficulty": item["difficulty"],
                "reference_answer": item["reference_answer"],
            }
            for item in selected[:number_of_questions]
        ]
