import unittest

from scoring.engine import calculate_score, rank_selections


class ScoringEngineTests(unittest.TestCase):

    def test_score_is_calculated(self):
        score = calculate_score(
            model_probability=0.80,
            value_edge=8.0,
        )

        self.assertAlmostEqual(score, 68.0)

    def test_zero_value_edge(self):
        score = calculate_score(
            model_probability=0.80,
            value_edge=0.0,
        )

        self.assertAlmostEqual(score, 56.0)

    def test_value_edge_is_capped(self):
        score = calculate_score(
            model_probability=0.80,
            value_edge=50.0,
        )

        expected = 56.0 + 30.0

        self.assertAlmostEqual(
            score,
            expected,
        )

    def test_invalid_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_score(
                model_probability=1.5,
                value_edge=5.0,
            )

    def test_negative_value_edge_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_score(
                model_probability=0.70,
                value_edge=-2.0,
            )

    def test_rankings_are_sorted_highest_first(self):
        selections = [
            {
                "match": "Match A",
                "model_probability": 0.80,
                "value_edge": 8.0,
            },
            {
                "match": "Match B",
                "model_probability": 0.70,
                "value_edge": 15.0,
            },
            {
                "match": "Match C",
                "model_probability": 0.60,
                "value_edge": 5.0,
            },
        ]

        ranked = rank_selections(selections)

        scores = [
            selection["score"]
            for selection in ranked
        ]

        self.assertEqual(
            scores,
            sorted(scores, reverse=True),
        )

    def test_score_is_added_to_selection(self):
        selections = [
            {
                "match": "Match A",
                "model_probability": 0.80,
                "value_edge": 8.0,
            }
        ]

        ranked = rank_selections(selections)

        self.assertIn(
            "score",
            ranked[0],
        )

    def test_missing_probability_is_rejected(self):
        selections = [
            {
                "match": "Match A",
                "value_edge": 8.0,
            }
        ]

        with self.assertRaises(ValueError):
            rank_selections(selections)

    def test_missing_value_edge_is_rejected(self):
        selections = [
            {
                "match": "Match A",
                "model_probability": 0.80,
            }
        ]

        with self.assertRaises(ValueError):
            rank_selections(selections)


if __name__ == "__main__":
    unittest.main()
