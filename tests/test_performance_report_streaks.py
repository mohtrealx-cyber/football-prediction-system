import unittest

from performance.report import build_performance_report


class PerformanceReportStreaksTests(unittest.TestCase):

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
            ],
            "draw": [],
            "away_win": [],
            "over_2_5": [],
            "under_2_5": [],
            "btts_yes": [],
            "btts_no": [],
        }

    def test_streaks_section_is_present(self):
        result = build_performance_report(self.results)

        self.assertIn("streaks", result)

    def test_streaks_section_is_dictionary(self):
        result = build_performance_report(self.results)

        self.assertIsInstance(result["streaks"], dict)

    def test_total_results_are_correct(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["streaks"]["total_results"],
            3,
        )

    def test_longest_winning_streak_is_correct(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["streaks"]["longest_winning_streak"],
            2,
        )

    def test_longest_losing_streak_is_correct(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["streaks"]["longest_losing_streak"],
            1,
        )

    def test_current_streak_is_correct(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["streaks"]["current_streak"],
            1,
        )

    def test_current_streak_type_is_correct(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["streaks"]["current_streak_type"],
            "LOSS",
        )

    def test_existing_overall_section_is_preserved(self):
        result = build_performance_report(self.results)

        self.assertIn("overall", result)
        self.assertIsInstance(result["overall"], dict)

    def test_existing_markets_section_is_preserved(self):
        result = build_performance_report(self.results)

        self.assertIn("markets", result)
        self.assertIsInstance(result["markets"], dict)

    def test_market_results_are_not_removed(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["markets"]["home_win"]["total_tickets"],
            3,
        )

        self.assertEqual(
            result["markets"]["home_win"]["wins"],
            2,
        )

        self.assertEqual(
            result["markets"]["home_win"]["losses"],
            1,
        )

    def test_empty_markets_do_not_break_streaks(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["streaks"]["total_results"],
            3,
        )

    def test_all_losses_produce_loss_streak(self):
        results = dict(self.results)

        results["home_win"] = [
            {
                "stake": 10.0,
                "won": False,
                "return_amount": 0.0,
                "profit_loss": -10.0,
            },
            {
                "stake": 10.0,
                "won": False,
                "return_amount": 0.0,
                "profit_loss": -10.0,
            },
            {
                "stake": 10.0,
                "won": False,
                "return_amount": 0.0,
                "profit_loss": -10.0,
            },
        ]

        result = build_performance_report(results)

        self.assertEqual(
            result["streaks"]["longest_losing_streak"],
            3,
        )

        self.assertEqual(
            result["streaks"]["current_streak_type"],
            "LOSS",
        )

    def test_all_wins_produce_win_streak(self):
        results = dict(self.results)

        results["home_win"] = [
            {
                "stake": 10.0,
                "won": True,
                "return_amount": 20.0,
                "profit_loss": 10.0,
            },
            {
                "stake": 10.0,
                "won": True,
                "return_amount": 20.0,
                "profit_loss": 10.0,
            },
            {
                "stake": 10.0,
                "won": True,
                "return_amount": 20.0,
                "profit_loss": 10.0,
            },
        ]

        result = build_performance_report(results)

        self.assertEqual(
            result["streaks"]["longest_winning_streak"],
            3,
        )

        self.assertEqual(
            result["streaks"]["current_streak_type"],
            "WIN",
        )

    def test_report_streaks_are_based_on_all_market_results(self):
        results = dict(self.results)

        results["draw"] = [
            {
                "stake": 10.0,
                "won": True,
                "return_amount": 20.0,
                "profit_loss": 10.0,
            }
        ]

        result = build_performance_report(results)

        self.assertEqual(
            result["streaks"]["total_results"],
            4,
        )

    def test_report_still_returns_overall_performance(self):
        result = build_performance_report(self.results)

        self.assertEqual(
            result["overall"]["total_tickets"],
            3,
        )


if __name__ == "__main__":
    unittest.main()
