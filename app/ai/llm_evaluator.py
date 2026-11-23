import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# Load API credentials from the project root's .env file.
load_dotenv()


class AnswerEvaluation(BaseModel):
    """Structured evaluation returned by the LLM."""

    correctness: int = Field(ge=0, le=10)
    relevance: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    score: float = Field(ge=0, le=10)
    strengths: List[str]
    improvements: List[str]
    feedback: str


class LLMEvaluator:
    """Evaluate interview answers using a hosted OpenAI model."""

    def __init__(self, client=None, model=None):
        self.model = model or os.getenv(
            "OPENAI_MODEL", "gpt-4o-mini"
        )

        # Allow a mock client to be injected during testing.
        self.client = client

        if self.client is None:
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key or api_key == "your_api_key_here":
                # No OpenAI key configured: fall back to the local evaluator.
                # evaluate_answer() will raise a catchable error so the
                # interview service can use local fallback evaluation.
                self.client = None
            else:
                self.client = OpenAI(api_key=api_key)

    def evaluate_answer(
        self,
        question,
        answer,
        role="General",
        difficulty="Medium",
        max_score=10,
        reference_answer=None,
        nlp_analysis=None,
    ):
        """Evaluate one answer and return a structured dictionary."""

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must not be empty.")

        if not isinstance(answer, str):
            raise TypeError("Answer must be a string.")

        if not isinstance(max_score, (int, float)) or isinstance(
            max_score, bool
        ) or max_score <= 0:
            raise ValueError("max_score must be a positive number.")

        # An unanswered question should not require an API call.
        if not answer.strip():
            return {
                "correctness": 0,
                "relevance": 0,
                "completeness": 0,
                "clarity": 0,
                "score": 0.0,
                "max_score": max_score,
                "strengths": [],
                "improvements": [
                    "Provide an answer to the interview question."
                ],
                "feedback": "No answer was provided.",
            }

        if self.client is None:
            raise RuntimeError(
                "OpenAI API key not configured; using local fallback evaluator."
            )

        context = {
            "role": role,
            "difficulty": difficulty,
            "question": question,
            "student_answer": answer,
            "reference_answer": reference_answer,
            "nlp_analysis": nlp_analysis,
            "maximum_score": max_score,
        }

        instructions = """
You are a fair technical interview evaluator.

Evaluate the student's answer based on:
1. Correctness: Are the statements technically accurate?
2. Relevance: Does the answer address the question?
3. Completeness: Does it cover the important concepts?
4. Clarity: Is the explanation understandable?

Return integer scores from 0 to 10 for each dimension.
Return an overall score from 0 to 10.

SCORING RULES - READ CAREFULLY:
- The reference answer is ONLY ONE EXAMPLE of a correct answer. It is NOT the required answer.
- Different but technically valid explanations, analogies, or approaches MUST receive full credit.
- Give PARTIAL CREDIT (5-7) for partially correct answers with some right concepts.
- Give HIGH CREDIT (8-10) for answers that are essentially correct even if phrased differently.
- Only give LOW scores (0-3) for factually incorrect statements or completely irrelevant answers.
- Do NOT penalize for: different wording, different examples, missing minor details, concise answers.
- Do NOT require specific keywords or phrases from the reference answer.
- Judge the TECHNICAL MERIT of the answer, not similarity to the reference.
- If the student demonstrates understanding of the core concept, score 7+ on correctness.
- Completeness: Score based on depth for the difficulty level (Beginner=basic, Advanced=thorough).
- Clarity: Score based on readability and structure, not length.

EXAMPLES OF FAIR SCORING:
- Student explains concept correctly in their own words -> Correctness: 9-10
- Student has right idea but minor technical inaccuracy -> Correctness: 6-7  
- Student mentions key terms but shows confusion -> Correctness: 4-5
- Student gives completely wrong explanation -> Correctness: 0-2

Be generous with partial credit. Be consistent. Return concise feedback.
"""

        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=(
                    "Evaluate this interview answer:\n"
                    + str(context)
                ),
                text_format=AnswerEvaluation,
            )

            evaluation = response.output_parsed

            if evaluation is None:
                raise RuntimeError(
                    "The model did not return a valid evaluation."
                )

            result = evaluation.model_dump()

            # Convert the model's 0-to-10 score to the requested scale.
            result["score"] = round(
                evaluation.score / 10 * max_score, 2
            )
            result["max_score"] = max_score

            return result

        except Exception as error:
            print("ORIGINAL OPENAI ERROR:", repr(error))
            raise RuntimeError(
                f"Answer evaluation failed: {error}"
            ) from error