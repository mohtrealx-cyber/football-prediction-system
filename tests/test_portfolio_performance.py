import unittest

from performance.portfolio import calculate_portfolio_performance


class PortfolioPerformanceTests(unittest.TestCase):

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
                    "return_amount": 25.0,
                    "profit_loss": 15.0,
                },
            ],
        }

    def test_returns_dictionary(self):
        result = calculate_portfolio_performance(self.results)
        self.assertIsInstance(result, dict)

    def test_overall_section_is_present(self):
        result = calculate_portfolio_performance(self.results)
        self.assertIn("overall", result)

    def test_tickets_section_is_present(self):
        result = calculate_portfolio_performance(self.results)
        self.assertIn("tickets", result)

    def test_all_four_tickets_are_present(self):
        result = calculate_portfolio_performance(self.results)

        self.assertEqual(
            set(result["tickets"].keys()),
            {"SAFE", "BALANCED", "AGGRESSIVE", "VALUE"},
        )

    def test_overall_total_tickets_is_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertEqual(result["overall"]["total_tickets"], 5)

    def test_overall_wins_are_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertEqual(result["overall"]["wins"], 3)

    def test_overall_losses_are_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertEqual(result["overall"]["losses"], 2)

    def test_overall_total_stake_is_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertEqual(result["overall"]["total_stake"], 140.0)

    def test_overall_total_return_is_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertEqual(result["overall"]["total_return"], 165.0)

    def test_overall_profit_loss_is_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertEqual(result["overall"]["total_profit_loss"], 25.0)

    def test_overall_roi_is_correct(self):
        result = calculate_portfolio_performance(self.results)
        self.assertAlmostEqual(
            result["overall"]["roi"],
            25.0 / 140.0,
        )

    def test_safe_metrics_are_preserved(self):
        result = calculate_portfolio_performance(self.results)

        self.assertEqual(
            result["tickets"]["SAFE"]["total_profit_loss"],
            0.0,
        )

    def test_balanced_metrics_are_preserved(self):
        result = calculate_portfolio_performance(self.results)

        self.assertEqual(
            result["tickets"]["BALANCED"]["total_profit_loss"],
            30.0,
        )

    def test_aggressive_metrics_are_preserved(self):
        result = calculate_portfolio_performance(self.results)

        self.assertEqual(
            result["tickets"]["AGGRESSIVE"]["total_profit_loss"],
            -20.0,
        )

    def test_value_metrics_are_preserved(self):
        result = calculate_portfolio_performance(self.results)

        self.assertEqual(
            result["tickets"]["VALUE"]["total_profit_loss"],
            15.0,
        )

    def test_empty_ticket_is_supported(self):
        results = dict(self.results)
        results["AGGRESSIVE"] = []

        result = calculate_portfolio_performance(results)

        self.assertEqual(
            result["tickets"]["AGGRESSIVE"]["total_tickets"],
            0,
        )

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_portfolio_performance([])

    def test_unknown_ticket_is_rejected(self):
        results = dict(self.results)
        results["UNKNOWN"] = []

        with self.assertRaises(ValueError):
            calculate_portfolio_performance(results)

    def test_missing_ticket_is_rejected(self):
        results = dict(self.results)
        del results["VALUE"]

        with self.assertRaises(ValueError):
            calculate_portfolio_performance(results)


if __name__ == "__main__":
    unittest.main()
