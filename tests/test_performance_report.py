import unittest

from performance.report import build_performance_report


class PerformanceReportTests(unittest.TestCase):

    def setUp(self):
        self.results = {
            "home_win": [
                {
                    "stake": 10.0,
                    "won": True,
                    "return_amount": 20.0,
                    "profit_loss": 10.0,
                },
                {
                    "stake": 10.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -10.0,
                },
                {
                    "stake": 20.0,
                    "won": True,
                    "return_amount": 40.0,
                    "profit_loss": 20.0,
                },
            ],
            "draw": [
                {
                    "stake": 10.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -10.0,
                },
                {
                    "stake": 10.0,
                    "won": True,
                    "return_amount": 30.0,
                    "profit_loss": 20.0,
                },
            ],
            "away_win": [],
            "over_2_5": [
                {
                    "stake": 20.0,
                    "won": True,
                    "return_amount": 50.0,
                    "profit_loss": 30.0,
                },
            ],
            "under_2_5": [
                {
                    "stake": 20.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -20.0,
                },
            ],
            "btts_yes": [
                {
                    "stake": 15.0,
                    "won": True,
                    "return_amount": 30.0,
                    "profit_loss": 15.0,
                },
            ],
            "btts_no": [
                {
                    "stake": 15.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -15.0,
                },
            ],
        }

    def test_returns_dictionary(self):
        result = build_performance_report(self.results)

        self.assertIsInstance(result, dict)

    def test_overall_section_is_present(self):
        result = build_performance_report(self.results)

        self.assertIn("overall", result)

    def test_markets_section_is_present(self):
        result = build_performance_report(self.results)

        self.assertIn("markets", result)

    def test_overall_is_dictionary(self):
        result = build_performance_report(self.results)

        self.assertIsInstance(
            result["overall"],
            dict,
        )

    def test_markets_is_dictionary(self):
        result = build_performance_report(self.results)

        self.assertIsInstance(
            result["markets"],
            dict,
        )

    def test_all_seven_markets_are_preserved(self):
        result = build_performance_report(self.results)

        expected_markets = {
            "home_win",
            "draw",
            "away_win",
            "over_2_5",
            "under_2_5",
            "btts_yes",
            "btts_no",
        }

        self.assertEqual(
            set(result["markets"].keys()),
            expected_markets,
        )

    def test_overall_total_tickets_is_sum_of_market_results(self):
        result = build_performance_report(self.results)

        # 3 + 2 + 0 + 1 + 1 + 1 + 1
        self.assertEqual(
            result["overall"]["total_tickets"],
            9,
        )

    def test_overall_wins_are_counted(self):
        result = build_performance_report(self.results)

        # 2 + 1 + 0 + 1 + 0 + 1 + 0
        self.assertEqual(
            result["overall"]["wins"],
            5,
        )

    def test_overall_losses_are_counted(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["overall"]["losses"],
            4,
        )

    def test_overall_total_stake_is_sum_of_market_stakes(self):
        result = build_performance_report(self.results)

        # 40 + 20 + 0 + 20 + 20 + 15 + 15
        self.assertEqual(
            result["overall"]["total_stake"],
            130.0,
        )

    def test_overall_total_return_is_sum_of_market_returns(self):
        result = build_performance_report(self.results)

        # 60 + 30 + 0 + 50 + 0 + 30 + 0
        self.assertEqual(
            result["overall"]["total_return"],
            170.0,
        )

    def test_overall_profit_loss_is_sum_of_market_profit_loss(self):
        result = build_performance_report(self.results)

        # 20 + 10 + 0 + 30 - 20 + 15 - 15
        self.assertEqual(
            result["overall"]["total_profit_loss"],
            40.0,
        )

    def test_overall_roi_is_calculated(self):
        result = build_performance_report(self.results)

        self.assertAlmostEqual(
            result["overall"]["roi"],
            40.0 / 130.0,
        )

    def test_overall_win_rate_is_calculated(self):
        result = build_performance_report(self.results)

        self.assertAlmostEqual(
            result["overall"]["win_rate"],
            5.0 / 9.0,
        )

    def test_market_breakdown_matches_market_performance(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["markets"]["home_win"]["total_tickets"],
            3,
        )

        self.assertEqual(
            result["markets"]["draw"]["total_tickets"],
            2,
        )

        self.assertEqual(
            result["markets"]["over_2_5"]["total_tickets"],
            1,
        )

    def test_empty_markets_are_supported(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["markets"]["away_win"]["total_tickets"],
            0,
        )

        self.assertEqual(
            result["markets"]["away_win"]["total_profit_loss"],
            0.0,
        )

    def test_report_does_not_remove_market_results(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            len(result["markets"]),
            7,
        )

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_performance_report([])

    def test_invalid_market_result_is_rejected(self):
        invalid_results = {
            "home_win": [
                {
                    "stake": 10.0,
                    "won": True,
                }
            ],
            "draw": [],
            "away_win": [],
            "over_2_5": [],
            "under_2_5": [],
            "btts_yes": [],
            "btts_no": [],
        }

        with self.assertRaises(ValueError):
            build_performance_report(invalid_results)

    def test_invalid_market_name_is_rejected(self):
        invalid_results = {
            "invalid_market": []
        }

        with self.assertRaises(ValueError):
            build_performance_report(invalid_results)


if __name__ == "__main__":
    unittest.main()
