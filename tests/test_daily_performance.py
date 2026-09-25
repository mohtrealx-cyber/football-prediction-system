import unittest

from performance.daily import calculate_daily_performance


class DailyPerformanceTests(unittest.TestCase):

    def setUp(self):
        self.results = {
            "SAFE": [
                {
                    "stake": 40.0,
                    "won": True,
                    "return_amount": 80.0,
                    "profit_loss": 40.0,
                },
                {
                    "stake": 40.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -40.0,
                },
            ],
            "BALANCED": [
                {
                    "stake": 30.0,
                    "won": True,
                    "return_amount": 60.0,
                    "profit_loss": 30.0,
                },
            ],
            "AGGRESSIVE": [
                {
                    "stake": 20.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -20.0,
                },
            ],
            "VALUE": [
                {
                    "stake": 10.0,
                    "won": True,
                    "return_amount": 20.0,
                    "profit_loss": 10.0,
                },
            ],
        }

    def test_returns_dictionary(self):
        result = calculate_daily_performance(self.results)

        self.assertIsInstance(result, dict)

    def test_total_tickets_is_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertEqual(
            result["total_tickets"],
            5,
        )

    def test_wins_are_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertEqual(
            result["wins"],
            3,
        )

    def test_losses_are_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertEqual(
            result["losses"],
            2,
        )

    def test_total_stake_is_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertEqual(
            result["total_stake"],
            140.0,
        )

    def test_total_return_is_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertEqual(
            result["total_return"],
            160.0,
        )

    def test_total_profit_loss_is_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertEqual(
            result["total_profit_loss"],
            20.0,
        )

    def test_roi_is_correct(self):
        result = calculate_daily_performance(self.results)

        self.assertAlmostEqual(
            result["roi"],
            20.0 / 140.0,
        )

    def test_ticket_breakdown_is_preserved(self):
        result = calculate_daily_performance(self.results)

        self.assertIn(
            "tickets",
            result,
        )

        self.assertEqual(
            set(result["tickets"].keys()),
            {
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            },
        )

    def test_streaks_are_present(self):
        result = calculate_daily_performance(self.results)

        self.assertIn(
            "streaks",
            result,
        )

        self.assertIsInstance(
            result["streaks"],
            dict,
        )

    def test_empty_day_returns_zero_metrics(self):
        empty_results = {
            "SAFE": [],
            "BALANCED": [],
            "AGGRESSIVE": [],
            "VALUE": [],
        }

        result = calculate_daily_performance(empty_results)

        self.assertEqual(
            result["total_tickets"],
            0,
        )

        self.assertEqual(
            result["wins"],
            0,
        )

        self.assertEqual(
            result["losses"],
            0,
        )

        self.assertEqual(
            result["total_stake"],
            0,
        )

        self.assertEqual(
            result["total_return"],
            0,
        )

        self.assertEqual(
            result["total_profit_loss"],
            0,
        )

    def test_missing_ticket_is_rejected(self):
        invalid_results = dict(self.results)
        invalid_results.pop("SAFE")

        with self.assertRaises(ValueError):
            calculate_daily_performance(invalid_results)

    def test_unknown_ticket_is_rejected(self):
        invalid_results = dict(self.results)
        invalid_results["UNKNOWN"] = []

        with self.assertRaises(ValueError):
            calculate_daily_performance(invalid_results)

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_daily_performance([])


if __name__ == "__main__":
    unittest.main()
