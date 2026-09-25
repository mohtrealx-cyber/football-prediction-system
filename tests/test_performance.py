import unittest

from performance.engine import calculate_performance


class PerformanceTests(unittest.TestCase):

    def make_results(self):
        return [
            {
                "selection_count": 3,
                "combined_odds": 2.00,
                "stake": 100.0,
                "won": True,
                "return_amount": 200.0,
                "profit_loss": 100.0,
            },
            {
                "selection_count": 3,
                "combined_odds": 1.50,
                "stake": 100.0,
                "won": False,
                "return_amount": 0.0,
                "profit_loss": -100.0,
            },
            {
                "selection_count": 4,
                "combined_odds": 2.50,
                "stake": 100.0,
                "won": True,
                "return_amount": 250.0,
                "profit_loss": 150.0,
            },
        ]

    def test_returns_dictionary(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertIsInstance(output, dict)

    def test_total_tickets_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertEqual(output["total_tickets"], 3)

    def test_wins_are_counted(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertEqual(output["wins"], 2)

    def test_losses_are_counted(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertEqual(output["losses"], 1)

    def test_win_rate_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertAlmostEqual(
            output["win_rate"],
            2 / 3,
        )

    def test_total_stake_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertAlmostEqual(
            output["total_stake"],
            300.0,
        )

    def test_total_return_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertAlmostEqual(
            output["total_return"],
            450.0,
        )

    def test_total_profit_loss_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertAlmostEqual(
            output["total_profit_loss"],
            150.0,
        )

    def test_roi_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertAlmostEqual(
            output["roi"],
            0.5,
        )

    def test_max_drawdown_is_calculated(self):
        results = self.make_results()

        output = calculate_performance(results)

        self.assertAlmostEqual(
            output["max_drawdown"],
            100.0,
        )

    def test_empty_results_return_zero_metrics(self):
        output = calculate_performance([])

        self.assertEqual(output["total_tickets"], 0)
        self.assertEqual(output["wins"], 0)
        self.assertEqual(output["losses"], 0)
        self.assertEqual(output["win_rate"], 0.0)
        self.assertEqual(output["total_stake"], 0.0)
        self.assertEqual(output["total_return"], 0.0)
        self.assertEqual(output["total_profit_loss"], 0.0)
        self.assertEqual(output["roi"], 0.0)
        self.assertEqual(output["max_drawdown"], 0.0)

    def test_non_list_results_are_rejected(self):
        with self.assertRaises(TypeError):
            calculate_performance("not a list")

    def test_missing_required_field_is_rejected(self):
        results = [
            {
                "stake": 100.0,
                "won": True,
                "return_amount": 200.0,
            }
        ]

        with self.assertRaises(ValueError):
            calculate_performance(results)

    def test_invalid_result_item_is_rejected(self):
        results = [
            "not a result"
        ]

        with self.assertRaises(TypeError):
            calculate_performance(results)


if __name__ == "__main__":
    unittest.main()
