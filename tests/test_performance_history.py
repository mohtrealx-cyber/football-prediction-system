import unittest

from performance.history import build_performance_history


class PerformanceHistoryTests(unittest.TestCase):

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

    def test_returns_list(self):
        result = build_performance_history(self.daily_results)
        self.assertIsInstance(result, list)

    def test_one_history_entry_is_created_per_day(self):
        result = build_performance_history(self.daily_results)
        self.assertEqual(len(result), 3)

    def test_dates_are_preserved(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["date"], "2026-09-01")
        self.assertEqual(result[1]["date"], "2026-09-02")
        self.assertEqual(result[2]["date"], "2026-09-03")

    def test_day_numbers_are_added(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["day"], 1)
        self.assertEqual(result[1]["day"], 2)
        self.assertEqual(result[2]["day"], 3)

    def test_cumulative_tickets_are_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["cumulative_tickets"], 4)
        self.assertEqual(result[1]["cumulative_tickets"], 8)
        self.assertEqual(result[2]["cumulative_tickets"], 12)

    def test_cumulative_wins_are_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["cumulative_wins"], 3)
        self.assertEqual(result[1]["cumulative_wins"], 5)
        self.assertEqual(result[2]["cumulative_wins"], 9)

    def test_cumulative_losses_are_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["cumulative_losses"], 1)
        self.assertEqual(result[1]["cumulative_losses"], 3)
        self.assertEqual(result[2]["cumulative_losses"], 3)

    def test_cumulative_stake_is_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["cumulative_stake"], 100.0)
        self.assertEqual(result[1]["cumulative_stake"], 200.0)
        self.assertEqual(result[2]["cumulative_stake"], 300.0)

    def test_cumulative_return_is_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["cumulative_return"], 120.0)
        self.assertEqual(result[1]["cumulative_return"], 200.0)
        self.assertEqual(result[2]["cumulative_return"], 340.0)

    def test_cumulative_profit_loss_is_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertEqual(result[0]["cumulative_profit_loss"], 20.0)
        self.assertEqual(result[1]["cumulative_profit_loss"], 0.0)
        self.assertEqual(result[2]["cumulative_profit_loss"], 40.0)

    def test_cumulative_roi_is_correct(self):
        result = build_performance_history(self.daily_results)

        self.assertAlmostEqual(result[0]["cumulative_roi"], 0.20)
        self.assertAlmostEqual(result[1]["cumulative_roi"], 0.0)
        self.assertAlmostEqual(
            result[2]["cumulative_roi"],
            40.0 / 300.0,
        )

    def test_empty_history_returns_empty_list(self):
        result = build_performance_history([])
        self.assertEqual(result, [])

    def test_non_list_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_performance_history({})

    def test_invalid_daily_result_is_rejected(self):
        invalid_results = [
            {
                "date": "2026-09-01",
                "total_tickets": 4,
            }
        ]

        with self.assertRaises(ValueError):
            build_performance_history(invalid_results)

    def test_duplicate_dates_are_rejected(self):
        duplicate_dates = [
            dict(self.daily_results[0]),
            dict(self.daily_results[0]),
        ]

        with self.assertRaises(ValueError):
            build_performance_history(duplicate_dates)

    def test_input_is_not_modified(self):
        original = [dict(result) for result in self.daily_results]

        build_performance_history(self.daily_results)

        self.assertEqual(self.daily_results, original)


if __name__ == "__main__":
    unittest.main()
