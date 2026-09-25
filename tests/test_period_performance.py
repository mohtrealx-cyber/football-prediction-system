import unittest

from performance.period import calculate_period_performance


class PeriodPerformanceTests(unittest.TestCase):

    def setUp(self):
        self.daily_results = [
            {
                "date": "2026-09-01",
                "total_tickets": 4,
                "wins": 3,
                "losses": 1,
                "total_stake": 100.0,
                "total_return": 120.0,
                "total_profit_loss": 20.0,
            },
            {
                "date": "2026-09-02",
                "total_tickets": 4,
                "wins": 2,
                "losses": 2,
                "total_stake": 100.0,
                "total_return": 80.0,
                "total_profit_loss": -20.0,
            },
            {
                "date": "2026-09-03",
                "total_tickets": 4,
                "wins": 4,
                "losses": 0,
                "total_stake": 100.0,
                "total_return": 140.0,
                "total_profit_loss": 40.0,
            },
        ]

    def test_returns_dictionary(self):
        result = calculate_period_performance(self.daily_results)
        self.assertIsInstance(result, dict)

    def test_total_days_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["total_days"], 3)

    def test_total_tickets_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["total_tickets"], 12)

    def test_total_wins_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["wins"], 9)

    def test_total_losses_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["losses"], 3)

    def test_total_stake_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["total_stake"], 300.0)

    def test_total_return_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["total_return"], 340.0)

    def test_total_profit_loss_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["total_profit_loss"], 40.0)

    def test_roi_is_correct(self):
        result = calculate_period_performance(self.daily_results)
        self.assertAlmostEqual(result["roi"], 40.0 / 300.0)

    def test_profitable_days_are_counted(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["profitable_days"], 2)

    def test_losing_days_are_counted(self):
        result = calculate_period_performance(self.daily_results)
        self.assertEqual(result["losing_days"], 1)

    def test_empty_period_returns_zero_metrics(self):
        result = calculate_period_performance([])

        self.assertEqual(result["total_days"], 0)
        self.assertEqual(result["total_tickets"], 0)
        self.assertEqual(result["wins"], 0)
        self.assertEqual(result["losses"], 0)
        self.assertEqual(result["total_stake"], 0.0)
        self.assertEqual(result["total_return"], 0.0)
        self.assertEqual(result["total_profit_loss"], 0.0)
        self.assertEqual(result["roi"], 0.0)

    def test_non_list_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_period_performance({})

    def test_invalid_daily_result_is_rejected(self):
        invalid_results = [
            {
                "date": "2026-09-01",
                "total_tickets": 4,
                "wins": 3,
            }
        ]

        with self.assertRaises(ValueError):
            calculate_period_performance(invalid_results)


if __name__ == "__main__":
    unittest.main()
