import unittest

from candidates.market_adapter import adapt_markets_to_candidates


class TestMarketAdapter(unittest.TestCase):

    def setUp(self):
        self.scored_markets = [
            {
                "market": "home_win",
                "model_probability": 0.70,
                "odds": 1.80,
                "market_probability": 1 / 1.80,
                "expected_value": 0.26,
                "value_edge": 14.44,
                "qualified": True,
                "score": 78.5,
            },
            {
                "market": "over_2_5",
                "model_probability": 0.60,
                "odds": 1.90,
                "market_probability": 1 / 1.90,
                "expected_value": 0.14,
                "value_edge": 7.37,
                "qualified": True,
                "score": 65.5,
            },
        ]

    def test_converts_markets_to_candidates(self):
        results = adapt_markets_to_candidates(
            "match_001",
            self.scored_markets,
        )

        self.assertEqual(len(results), 2)

    def test_match_id_is_added(self):
        results = adapt_markets_to_candidates(
            "match_001",
            self.scored_markets,
        )

        for result in results:
            self.assertEqual(result["match_id"], "match_001")

    def test_market_information_is_preserved(self):
        results = adapt_markets_to_candidates(
            "match_001",
            self.scored_markets,
        )

        self.assertEqual(
            results[0]["market"],
            "home_win",
        )

        self.assertEqual(
            results[0]["score"],
            78.5,
        )

    def test_original_market_data_is_not_modified(self):
        original = [dict(item) for item in self.scored_markets]

        adapt_markets_to_candidates(
            "match_001",
            self.scored_markets,
        )

        self.assertEqual(
            self.scored_markets,
            original,
        )

    def test_empty_market_list_is_allowed(self):
        results = adapt_markets_to_candidates(
            "match_001",
            [],
        )

        self.assertEqual(results, [])

    def test_empty_match_id_is_rejected(self):
        with self.assertRaises(ValueError):
            adapt_markets_to_candidates(
                "",
                self.scored_markets,
            )

    def test_match_id_must_be_string(self):
        with self.assertRaises(ValueError):
            adapt_markets_to_candidates(
                123,
                self.scored_markets,
            )

    def test_markets_must_be_list(self):
        with self.assertRaises(TypeError):
            adapt_markets_to_candidates(
                "match_001",
                {},
            )

    def test_invalid_market_result_is_rejected(self):
        with self.assertRaises(TypeError):
            adapt_markets_to_candidates(
                "match_001",
                ["invalid"],
            )

    def test_missing_required_field_is_rejected(self):
        incomplete = [self.scored_markets[0].copy()]
        del incomplete[0]["score"]

        with self.assertRaises(ValueError):
            adapt_markets_to_candidates(
                "match_001",
                incomplete,
            )


if __name__ == "__main__":
    unittest.main()
