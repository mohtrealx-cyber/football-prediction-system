import unittest

from analysis.engine import analyze_selection


class AnalysisEngineTests(unittest.TestCase):

    def test_high_value_selection_qualifies(self):
        result = analyze_selection(
            market="Over 2.5",
            model_probability=0.60,
            odds=2.00,
            minimum_edge=5.0,
        )

        self.assertTrue(result.qualified)
        self.assertAlmostEqual(result.market_probability, 0.50)
        self.assertAlmostEqual(result.expected_value, 0.20)
        self.assertAlmostEqual(result.value_edge, 10.0)

    def test_low_value_selection_is_rejected(self):
        result = analyze_selection(
            market="Home Win",
            model_probability=0.52,
            odds=1.90,
            minimum_edge=5.0,
        )

        self.assertFalse(result.qualified)

    def test_custom_minimum_edge(self):
        result = analyze_selection(
            market="BTTS",
            model_probability=0.60,
            odds=2.00,
            minimum_edge=12.0,
        )

        self.assertFalse(result.qualified)

    def test_empty_market_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_selection(
                market="",
                model_probability=0.60,
                odds=2.00,
            )

    def test_invalid_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_selection(
                market="Home Win",
                model_probability=1.5,
                odds=2.00,
            )

    def test_invalid_odds_are_rejected(self):
        with self.assertRaises(ValueError):
            analyze_selection(
                market="Home Win",
                model_probability=0.60,
                odds=1.00,
            )

    def test_negative_minimum_edge_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_selection(
                market="Home Win",
                model_probability=0.60,
                odds=2.00,
                minimum_edge=-1.0,
            )

    def test_result_can_be_converted_to_dict(self):
        result = analyze_selection(
            market="Over 2.5",
            model_probability=0.60,
            odds=2.00,
        )

        data = result.to_dict()

        self.assertEqual(data["market"], "Over 2.5")
        self.assertIn("qualified", data)
        self.assertIn("expected_value", data)
        self.assertIn("value_edge", data)


if __name__ == "__main__":
    unittest.main()
