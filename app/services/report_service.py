
class ReportService:
    """Generate a final interview performance report."""

    DIMENSIONS = [
        "correctness",
        "relevance",
        "completeness",
        "clarity",
    ]

    def generate_report(
        self,
        interview_results,
        candidate_name="Candidate",
        role="General",
    ):
        """Create a report from completed interview results."""

        if not isinstance(interview_results, list):
            raise TypeError("interview_results must be a list.")

        if not interview_results:
            raise ValueError(
                "At least one interview result is required."
            )

        if not isinstance(candidate_name, str) or not candidate_name.strip():
            raise ValueError("Candidate name must not be empty.")

        if not isinstance(role, str) or not role.strip():
            raise ValueError("Role must not be empty.")

        total_score = 0.0
        total_possible = 0.0
        dimension_totals = {key: 0.0 for key in self.DIMENSIONS}
        strengths = []
        improvements = []
        question_reports = []

        for index, item in enumerate(interview_results, start=1):
            if not isinstance(item, dict):
                raise TypeError(
                    f"Result {index} must be a dictionary."
                )

            evaluation = item.get("evaluation", item)

            if not isinstance(evaluation, dict):
                raise TypeError(
                    f"Evaluation {index} must be a dictionary."
                )

            score = evaluation.get("score")
            max_score = evaluation.get("max_score", 10)

            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not isinstance(max_score, (int, float))
                or isinstance(max_score, bool)
                or max_score <= 0
                or not 0 <= score <= max_score
            ):
                raise ValueError(
                    f"Invalid score or maximum score in result {index}."
                )

            total_score += score
            total_possible += max_score

            for dimension in self.DIMENSIONS:
                value = evaluation.get(dimension, 0)

                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or not 0 <= value <= 10
                ):
                    raise ValueError(
                        f"Invalid {dimension} score in result {index}."
                    )

                dimension_totals[dimension] += value

            item_strengths = evaluation.get("strengths", [])
            item_improvements = evaluation.get("improvements", [])

            if not isinstance(item_strengths, list):
                raise TypeError("Strengths must be a list.")

            if not isinstance(item_improvements, list):
                raise TypeError("Improvements must be a list.")

            strengths.extend(
                text for text in item_strengths
                if isinstance(text, str) and text.strip()
            )
            improvements.extend(
                text for text in item_improvements
                if isinstance(text, str) and text.strip()
            )

            question_reports.append({
                "question_number": index,
                "question": item.get("question", ""),
                "difficulty": item.get("difficulty", "Unknown"),
                "score": round(score, 2),
                "max_score": round(max_score, 2),
                "percentage": round(score / max_score * 100, 2),
                "feedback": evaluation.get("feedback", ""),
            })

        question_count = len(interview_results)

        dimension_averages = {
            key: round(value / question_count, 2)
            for key, value in dimension_totals.items()
        }

        percentage = round(
            total_score / total_possible * 100, 2
        )

        # Rank performance dimensions from strongest to weakest.
        ranked_dimensions = sorted(
            dimension_averages.items(),
            key=lambda pair: pair[1],
            reverse=True,
        )

        recommendations = []

        recommendation_map = {
            "correctness": (
                "Review core concepts and practise explaining "
                "why your answers are technically correct."
            ),
            "relevance": (
                "Focus on answering the exact question before "
                "adding supporting details."
            ),
            "completeness": (
                "Include key concepts, examples, and relevant "
                "steps when explaining your answers."
            ),
            "clarity": (
                "Structure answers clearly and use concise "
                "technical explanations."
            ),
        }

        for dimension, average in ranked_dimensions:
            if average < 7:
                recommendations.append(
                    recommendation_map[dimension]
                )

        if not recommendations:
            recommendations.append(
                "Maintain your performance by practising "
                "more advanced interview questions."
            )

        # Remove duplicate feedback while preserving its order.
        strengths = list(dict.fromkeys(strengths))
        improvements = list(dict.fromkeys(improvements))

        return {
            "candidate_name": candidate_name.strip(),
            "role": role.strip(),
            "questions_answered": question_count,
            "total_score": round(total_score, 2),
            "maximum_score": round(total_possible, 2),
            "percentage": percentage,
            "dimension_averages": dimension_averages,
            "strongest_area": ranked_dimensions[0][0],
            "weakest_area": ranked_dimensions[-1][0],
            "strengths": strengths,
            "improvements": improvements,
            "recommendations": recommendations,
            "question_reports": question_reports,
        }
