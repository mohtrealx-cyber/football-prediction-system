import unittest

from performance.ticket import calculate_ticket_performance


class TicketPerformanceTests(unittest.TestCase):

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
                {
                    "stake": 40.0,
                    "won": True,
                    "return_amount": 100.0,
                    "profit_loss": 60.0,
                },
            ],
            "BALANCED": [
                {
                    "stake": 30.0,
                    "won": True,
                    "return_amount": 75.0,
                    "profit_loss": 45.0,
                },
                {
                    "stake": 30.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -30.0,
                },
            ],
            "AGGRESSIVE": [],
            "VALUE": [
                {
                    "stake": 10.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -10.0,
                },
            ],
        }

    def test_returns_dictionary(self):
        result = calculate_ticket_performance(self.results)

        self.assertIsInstance(result, dict)

    def test_all_four_tickets_are_present(self):
        result = calculate_ticket_performance(self.results)

        expected_tickets = {
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        }

        self.assertEqual(
            set(result.keys()),
            expected_tickets,
        )

    def test_each_ticket_returns_dictionary(self):
        result = calculate_ticket_performance(self.results)

        for ticket_result in result.values():
            self.assertIsInstance(
                ticket_result,
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

        self.assertEqual(
            result["SAFE"]["total_stake"],
            120.0,
        )

    def test_safe_total_return(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["total_return"],
            180.0,
        )

    def test_safe_profit_loss(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["total_profit_loss"],
            60.0,
        )

    def test_safe_roi(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["roi"],
            0.5,
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

        self.assertEqual(
            result["BALANCED"]["total_stake"],
            60.0,
        )

        self.assertEqual(
            result["BALANCED"]["total_return"],
            75.0,
        )

        self.assertEqual(
            result["BALANCED"]["total_profit_loss"],
            15.0,
        )

    def test_empty_aggressive_ticket_returns_zero_metrics(self):
        result = calculate_ticket_performance(self.results)

        aggressive = result["AGGRESSIVE"]

        self.assertEqual(
            aggressive["total_tickets"],
            0,
        )

        self.assertEqual(
            aggressive["wins"],
            0,
        )

        self.assertEqual(
            aggressive["losses"],
            0,
        )

        self.assertEqual(
            aggressive["total_stake"],
            0.0,
        )

        self.assertEqual(
            aggressive["total_return"],
            0.0,
        )

        self.assertEqual(
            aggressive["total_profit_loss"],
            0.0,
        )

        self.assertEqual(
            aggressive["roi"],
            0.0,
        )

        self.assertEqual(
            aggressive["max_drawdown"],
            0.0,
        )

    def test_all_ticket_metrics_have_same_structure(self):
        result = calculate_ticket_performance(self.results)

        expected_fields = {
            "total_tickets",
            "wins",
            "losses",
            "win_rate",
            "total_stake",
            "total_return",
            "total_profit_loss",
            "roi",
            "max_drawdown",
        }

        for ticket_result in result.values():
            self.assertEqual(
                set(ticket_result.keys()),
                expected_fields,
            )

    def test_ticket_results_are_independent(self):
        result = calculate_ticket_performance(self.results)

        self.assertNotEqual(
            result["SAFE"]["total_tickets"],
            result["BALANCED"]["total_tickets"],
        )

        self.assertNotEqual(
            result["SAFE"]["total_stake"],
            result["VALUE"]["total_stake"],
        )

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_ticket_performance([])

    def test_invalid_ticket_name_is_rejected(self):
        invalid_results = {
            "INVALID": []
        }

        with self.assertRaises(ValueError):
            calculate_ticket_performance(invalid_results)

    def test_invalid_ticket_result_is_rejected(self):
        invalid_results = {
            "SAFE": [
                {
                    "stake": 40.0,
                    "won": True,
                }
            ],
            "BALANCED": [],
            "AGGRESSIVE": [],
            "VALUE": [],
        }

        with self.assertRaises(ValueError):
            calculate_ticket_performance(invalid_results)


if __name__ == "__main__":
    unittest.main()
