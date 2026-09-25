import unittest

from portfolio_backtest.engine import evaluate_portfolio


class PortfolioBacktestTests(unittest.TestCase):

    def make_tickets(self):
        return [
            {
                "ticket_name": "SAFE",
                "won": True,
                "stake": 100.0,
                "return_amount": 200.0,
                "profit_loss": 100.0,
            },
            {
                "ticket_name": "BALANCED",
                "won": False,
                "stake": 100.0,
                "return_amount": 0.0,
                "profit_loss": -100.0,
            },
            {
                "ticket_name": "AGGRESSIVE",
                "won": True,
                "stake": 100.0,
                "return_amount": 250.0,
                "profit_loss": 150.0,
            },
            {
                "ticket_name": "VALUE",
                "won": False,
                "stake": 100.0,
                "return_amount": 0.0,
                "profit_loss": -100.0,
            },
        ]

    def test_returns_dictionary(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertIsInstance(result, dict)

    def test_four_tickets_are_evaluated(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertEqual(
            result["total_tickets"],
            4,
        )

    def test_winning_tickets_are_counted(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertEqual(
            result["wins"],
            2,
        )

    def test_losing_tickets_are_counted(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertEqual(
            result["losses"],
            2,
        )

    def test_total_stake_is_calculated(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertAlmostEqual(
            result["total_stake"],
            400.0,
        )

    def test_total_return_is_calculated(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertAlmostEqual(
            result["total_return"],
            450.0,
        )

    def test_total_profit_loss_is_calculated(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertAlmostEqual(
            result["total_profit_loss"],
            50.0,
        )

    def test_roi_is_calculated(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertAlmostEqual(
            result["roi"],
            0.125,
        )

    def test_ticket_breakdown_is_preserved(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertIn(
            "ticket_breakdown",
            result,
        )

        self.assertEqual(
            len(result["ticket_breakdown"]),
            4,
        )

    def test_safe_ticket_is_preserved(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertEqual(
            result["ticket_breakdown"]["SAFE"]["profit_loss"],
            100.0,
        )

    def test_balanced_ticket_is_preserved(self):
        result = evaluate_portfolio(self.make_tickets())

        self.assertEqual(
            result["ticket_breakdown"]["BALANCED"]["profit_loss"],
            -100.0,
        )

    def test_required_ticket_names_are_present(self):
        result = evaluate_portfolio(self.make_tickets())

        expected_names = {
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        }

        self.assertEqual(
            set(result["ticket_breakdown"].keys()),
            expected_names,
        )

    def test_duplicate_ticket_name_is_rejected(self):
        tickets = self.make_tickets()

        tickets[1]["ticket_name"] = "SAFE"

        with self.assertRaises(ValueError):
            evaluate_portfolio(tickets)

    def test_missing_ticket_name_is_rejected(self):
        tickets = self.make_tickets()

        del tickets[0]["ticket_name"]

        with self.assertRaises(ValueError):
            evaluate_portfolio(tickets)

    def test_invalid_ticket_list_is_rejected(self):
        with self.assertRaises(TypeError):
            evaluate_portfolio("not a list")

    def test_invalid_ticket_item_is_rejected(self):
        tickets = self.make_tickets()
        tickets[0] = "not a ticket"

        with self.assertRaises(TypeError):
            evaluate_portfolio(tickets)


if __name__ == "__main__":
    unittest.main()
