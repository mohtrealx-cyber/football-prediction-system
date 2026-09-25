import unittest

from performance.portfolio_report import build_portfolio_report


SUPPORTED_TICKETS = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)

SUPPORTED_MARKETS = (
    "home_win",
    "draw",
    "away_win",
    "over_2_5",
    "under_2_5",
    "btts_yes",
    "btts_no",
)


class PortfolioReportTests(unittest.TestCase):

    def setUp(self):
        empty_markets = {
            market: []
            for market in SUPPORTED_MARKETS
        }

        self.results = {
            ticket: {
                market: list(values)
                for market, values in empty_markets.items()
            }
            for ticket in SUPPORTED_TICKETS
        }

        self.results["SAFE"]["home_win"] = [
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
        ]

        self.results["BALANCED"]["draw"] = [
            {
                "stake": 20.0,
                "won": True,
                "return_amount": 40.0,
                "profit_loss": 20.0,
            },
        ]

    def test_returns_dictionary(self):
        result = build_portfolio_report(self.results)

        self.assertIsInstance(result, dict)

    def test_overall_section_is_present(self):
        result = build_portfolio_report(self.results)

        self.assertIn("overall", result)

    def test_tickets_section_is_present(self):
        result = build_portfolio_report(self.results)

        self.assertIn("tickets", result)

    def test_ticket_markets_section_is_present(self):
        result = build_portfolio_report(self.results)

        self.assertIn("ticket_markets", result)

    def test_overall_is_dictionary(self):
        result = build_portfolio_report(self.results)

        self.assertIsInstance(
            result["overall"],
            dict,
        )

    def test_all_four_tickets_are_present(self):
        result = build_portfolio_report(self.results)

        self.assertEqual(
            set(result["tickets"].keys()),
            set(SUPPORTED_TICKETS),
        )

    def test_all_four_ticket_market_sections_are_present(self):
        result = build_portfolio_report(self.results)

        self.assertEqual(
            set(result["ticket_markets"].keys()),
            set(SUPPORTED_TICKETS),
        )

    def test_all_seven_markets_are_present_for_each_ticket(self):
        result = build_portfolio_report(self.results)

        for ticket_name in SUPPORTED_TICKETS:
            self.assertEqual(
                set(
                    result["ticket_markets"][ticket_name].keys()
                ),
                set(SUPPORTED_MARKETS),
            )

    def test_safe_home_win_metrics_are_preserved(self):
        result = build_portfolio_report(self.results)

        metrics = result["ticket_markets"]["SAFE"]["home_win"]

        self.assertEqual(
            metrics["total_tickets"],
            2,
        )

        self.assertEqual(
            metrics["wins"],
            1,
        )

        self.assertEqual(
            metrics["losses"],
            1,
        )

        self.assertEqual(
            metrics["total_profit_loss"],
            0.0,
        )

    def test_balanced_draw_metrics_are_preserved(self):
        result = build_portfolio_report(self.results)

        metrics = result["ticket_markets"]["BALANCED"]["draw"]

        self.assertEqual(
            metrics["total_tickets"],
            1,
        )

        self.assertEqual(
            metrics["wins"],
            1,
        )

        self.assertEqual(
            metrics["losses"],
            0,
        )

        self.assertEqual(
            metrics["total_profit_loss"],
            20.0,
        )

    def test_streaks_are_preserved(self):
        result = build_portfolio_report(self.results)

        safe_home_win = result["ticket_markets"]["SAFE"]["home_win"]

        self.assertIn(
            "streaks",
            safe_home_win,
        )

        self.assertIsInstance(
            safe_home_win["streaks"],
            dict,
        )

    def test_empty_markets_are_supported(self):
        result = build_portfolio_report(self.results)

        metrics = result["ticket_markets"]["VALUE"]["btts_yes"]

        self.assertEqual(
            metrics["total_tickets"],
            0,
        )

        self.assertEqual(
            metrics["wins"],
            0,
        )

        self.assertEqual(
            metrics["losses"],
            0,
        )

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_portfolio_report([])


if __name__ == "__main__":
    unittest.main()
