
import unittest

from app.services.report_service import ReportService


class TestReportService(unittest.TestCase):

    def setUp(self):
        self.service = ReportService()

        self.results = [
            {
                "question": "What is Python?",
                "difficulty": "Beginner",
                "evaluation": {
                    "correctness": 9,
                    "relevance": 10,
                    "completeness": 8,
                    "clarity": 9,
                    "score": 9,
                    "max_score": 10,
                    "strengths": ["Correct explanation"],
                    "improvements": ["Add an example"],
                    "feedback": "Good answer.",
                },
            },
            {
                "question": "Explain decorators.",
                "difficulty": "Intermediate",
                "evaluation": {
                    "correctness": 6,
                    "relevance": 8,
                    "completeness": 5,
                    "clarity": 7,
                    "score": 6.5,
                    "max_score": 10,
                    "strengths": ["Relevant answer"],
                    "improvements": ["Add more details"],
                    "feedback": "Explain the concept further.",
                },
            },
        ]

    def test_calculates_overall_percentage(self):
        report = self.service.generate_report(self.results)

        self.assertEqual(report["total_score"], 15.5)
        self.assertEqual(report["maximum_score"], 20)
        self.assertEqual(report["percentage"], 77.5)

    def test_calculates_dimension_averages(self):
        report = self.service.generate_report(self.results)

        self.assertEqual(
            report["dimension_averages"]["correctness"], 7.5
        )
        self.assertEqual(
            report["dimension_averages"]["completeness"], 6.5
        )

    def test_identifies_strongest_and_weakest_areas(self):
        report = self.service.generate_report(self.results)

        self.assertEqual(report["strongest_area"], "relevance")
        self.assertEqual(report["weakest_area"], "completeness")

    def test_includes_question_wise_results(self):
        report = self.service.generate_report(self.results)

        self.assertEqual(report["questions_answered"], 2)
        self.assertEqual(len(report["question_reports"]), 2)
        self.assertEqual(
            report["question_reports"][0]["percentage"], 90.0
        )

    def test_collects_strengths_and_improvements(self):
        report = self.service.generate_report(self.results)

        self.assertIn(
            "Correct explanation", report["strengths"]
        )
        self.assertIn(
            "Add more details", report["improvements"]
        )

    def test_generates_recommendations(self):
        report = self.service.generate_report(self.results)

        self.assertTrue(report["recommendations"])
        self.assertTrue(
            any(
                "key concepts" in recommendation
                for recommendation in report["recommendations"]
            )
        )

    def test_supports_direct_evaluation_dictionaries(self):
        direct_results = [
            {
                "score": 8,
                "max_score": 10,
                "correctness": 8,
                "relevance": 8,
                "completeness": 8,
                "clarity": 8,
                "strengths": [],
                "improvements": [],
                "feedback": "Good.",
            }
        ]

        report = self.service.generate_report(direct_results)

        self.assertEqual(report["percentage"], 80.0)

    def test_rejects_empty_results(self):
        with self.assertRaises(ValueError):
            self.service.generate_report([])

    def test_rejects_invalid_scores(self):
        invalid_results = [
            {
                "score": 15,
                "max_score": 10,
            }
        ]

        with self.assertRaises(ValueError):
            self.service.generate_report(invalid_results)

    def test_uses_candidate_details(self):
        report = self.service.generate_report(
            self.results,
            candidate_name="Student A",
            role="Python Developer",
        )

        self.assertEqual(report["candidate_name"], "Student A")
        self.assertEqual(report["role"], "Python Developer")


if __name__ == "__main__":
    unittest.main()
