import unittest

from performance.ticket import calculate_ticket_performance


class TicketPerformanceTests(unittest.TestCase):

    def setUp(self):
        self.results = {
            "SAFE": [
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
                    "stake": 10.0,
                    "won": True,
                    "return_amount": 20.0,
                    "profit_loss": 10.0,
                },
            ],
            "BALANCED": [
                {
                    "stake": 20.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -20.0,
                },
                {
                    "stake": 20.0,
                    "won": True,
                    "return_amount": 40.0,
                    "profit_loss": 20.0,
                },
            ],
            "AGGRESSIVE": [],
            "VALUE": [
                {
                    "stake": 5.0,
                    "won": True,
                    "return_amount": 10.0,
                    "profit_loss": 5.0,
                },
            ],
        }

    def test_returns_dictionary(self):
        result = calculate_ticket_performance(self.results)

        self.assertIsInstance(result, dict)

    def test_all_four_tickets_are_present(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            set(result.keys()),
            {
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            },
        )

    def test_each_ticket_returns_dictionary(self):
        result = calculate_ticket_performance(self.results)

        for ticket_name in (
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ):
            self.assertIsInstance(
                result[ticket_name],
                dict,
            )

    def test_all_ticket_metrics_have_same_structure(self):
        result = calculate_ticket_performance(self.results)

        expected_keys = {
            "total_tickets",
            "wins",
            "losses",
            "win_rate",
            "total_stake",
            "total_return",
            "total_profit_loss",
            "roi",
            "max_drawdown",
            "streaks",
        }

        for ticket_name in (
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ):
            self.assertEqual(
                set(result[ticket_name].keys()),
                expected_keys,
            )

            self.assertIsInstance(
                result[ticket_name]["streaks"],
                dict,
            )

    def test_safe_total_tickets(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["total_tickets"],
            3,
        )

    def test_safe_wins_are_counted(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["wins"],
            2,
        )

    def test_safe_losses_are_counted(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["losses"],
            1,
        )

    def test_safe_total_stake(self):
        result = calculate_ticket_performance(self.results)

        self.assertAlmostEqual(
            result["SAFE"]["total_stake"],
            30.0,
        )

    def test_safe_total_return(self):
        result = calculate_ticket_performance(self.results)

        self.assertAlmostEqual(
            result["SAFE"]["total_return"],
            40.0,
        )

    def test_safe_profit_loss(self):
        result = calculate_ticket_performance(self.results)

        self.assertAlmostEqual(
            result["SAFE"]["total_profit_loss"],
            10.0,
        )

    def test_safe_roi(self):
        result = calculate_ticket_performance(self.results)

        self.assertAlmostEqual(
            result["SAFE"]["roi"],
            10.0 / 30.0,
        )

    def test_balanced_is_calculated_separately(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["BALANCED"]["total_tickets"],
            2,
        )

        self.assertEqual(
            result["BALANCED"]["wins"],
            1,
        )

        self.assertEqual(
            result["BALANCED"]["losses"],
            1,
        )

        self.assertAlmostEqual(
            result["BALANCED"]["total_stake"],
            40.0,
        )

        self.assertAlmostEqual(
            result["BALANCED"]["total_profit_loss"],
            0.0,
        )

    def test_empty_aggressive_ticket_returns_zero_metrics(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["AGGRESSIVE"]["total_tickets"],
            0,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["wins"],
            0,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["losses"],
            0,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["total_stake"],
            0.0,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["total_return"],
            0.0,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["total_profit_loss"],
            0.0,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["roi"],
            0.0,
        )

    def test_invalid_ticket_name_is_rejected(self):
        invalid_results = dict(self.results)

        invalid_results["INVALID"] = []

        with self.assertRaises(ValueError):
            calculate_ticket_performance(invalid_results)

    def test_missing_ticket_name_is_rejected(self):
        invalid_results = dict(self.results)

        del invalid_results["VALUE"]

        with self.assertRaises(ValueError):
            calculate_ticket_performance(invalid_results)

    def test_invalid_ticket_result_is_rejected(self):
        invalid_results = {
            "SAFE": [
                {
                    "stake": 10.0,
                    "won": True,
                }
            ],
            "BALANCED": [],
            "AGGRESSIVE": [],
            "VALUE": [],
        }

        with self.assertRaises(ValueError):
            calculate_ticket_performance(invalid_results)

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_ticket_performance([])

    def test_ticket_results_are_independent(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["total_tickets"],
            3,
        )

        self.assertEqual(
            result["BALANCED"]["total_tickets"],
            2,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["total_tickets"],
            0,
        )

        self.assertEqual(
            result["VALUE"]["total_tickets"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
