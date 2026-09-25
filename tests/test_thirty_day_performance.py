import unittest

from performance.thirty_day import calculate_30_day_performance


class ThirtyDayPerformanceTests(unittest.TestCase):

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
        result = calculate_30_day_performance(self.daily_results)
        self.assertIsInstance(result, dict)

    def test_target_days_is_30(self):
        result = calculate_30_day_performance(self.daily_results)
        self.assertEqual(result["target_days"], 30)

    def test_elapsed_days_is_correct(self):
        result = calculate_30_day_performance(self.daily_results)
        self.assertEqual(result["elapsed_days"], 3)

    def test_days_remaining_is_correct(self):
        result = calculate_30_day_performance(self.daily_results)
        self.assertEqual(result["days_remaining"], 27)

    def test_experiment_is_not_complete_before_day_30(self):
        result = calculate_30_day_performance(self.daily_results)
        self.assertFalse(result["complete"])

    def test_aggregated_ticket_metrics_are_correct(self):
        result = calculate_30_day_performance(self.daily_results)

        self.assertEqual(result["total_tickets"], 12)
        self.assertEqual(result["wins"], 9)
        self.assertEqual(result["losses"], 3)

    def test_aggregated_financial_metrics_are_correct(self):
        result = calculate_30_day_performance(self.daily_results)

        self.assertEqual(result["total_stake"], 300.0)
        self.assertEqual(result["total_return"], 340.0)
        self.assertEqual(result["total_profit_loss"], 40.0)
        self.assertAlmostEqual(result["roi"], 40.0 / 300.0)

    def test_full_30_day_period_is_complete(self):
        daily_results = []

        for day in range(1, 31):
            daily_results.append(
                {
                    "date": f"2026-09-{day:02d}",
                    "total_tickets": 4,
                    "wins": 2,
                    "losses": 2,
                    "total_stake": 100.0,
                    "total_return": 100.0,
                    "total_profit_loss": 0.0,
                }
            )

        result = calculate_30_day_performance(daily_results)

        self.assertEqual(result["target_days"], 30)
        self.assertEqual(result["elapsed_days"], 30)
        self.assertEqual(result["days_remaining"], 0)
        self.assertTrue(result["complete"])

    def test_more_than_30_days_are_rejected(self):
        daily_results = self.daily_results * 11

        with self.assertRaises(ValueError):
            calculate_30_day_performance(daily_results)

    def test_empty_period_is_supported(self):
        result = calculate_30_day_performance([])

        self.assertEqual(result["target_days"], 30)
        self.assertEqual(result["elapsed_days"], 0)
        self.assertEqual(result["days_remaining"], 30)
        self.assertFalse(result["complete"])
        self.assertEqual(result["total_tickets"], 0)
        self.assertEqual(result["total_stake"], 0.0)
        self.assertEqual(result["total_return"], 0.0)
        self.assertEqual(result["total_profit_loss"], 0.0)
        self.assertEqual(result["roi"], 0.0)

    def test_non_list_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_30_day_performance({})

    def test_daily_results_are_not_modified(self):
        original = [dict(result) for result in self.daily_results]

        calculate_30_day_performance(self.daily_results)

        self.assertEqual(self.daily_results, original)


if __name__ == "__main__":
    unittest.main()
