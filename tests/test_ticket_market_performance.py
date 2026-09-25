import unittest

from performance.ticket_market import calculate_ticket_market_performance


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


class TicketMarketPerformanceTests(unittest.TestCase):

    def setUp(self):
        empty_market_results = {
            market: []
            for market in SUPPORTED_MARKETS
        }

        self.results = {
            ticket: {
                market: list(results)
                for market, results in empty_market_results.items()
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
        ]

        self.results["AGGRESSIVE"]["over_2_5"] = [
            {
                "stake": 5.0,
                "won": False,
                "return_amount": 0.0,
                "profit_loss": -5.0,
            },
            {
                "stake": 5.0,
                "won": False,
                "return_amount": 0.0,
                "profit_loss": -5.0,
            },
        ]

        self.results["VALUE"]["btts_yes"] = [
            {
                "stake": 5.0,
                "won": True,
                "return_amount": 10.0,
                "profit_loss": 5.0,
            },
            {
                "stake": 5.0,
                "won": True,
                "return_amount": 10.0,
                "profit_loss": 5.0,
            },
            {
                "stake": 5.0,
                "won": True,
                "return_amount": 10.0,
                "profit_loss": 5.0,
            },
        ]

    def test_returns_dictionary(self):
        result = calculate_ticket_market_performance(self.results)

        self.assertIsInstance(result, dict)

    def test_all_four_tickets_are_present(self):
        result = calculate_ticket_market_performance(self.results)

        self.assertEqual(
            set(result.keys()),
            set(SUPPORTED_TICKETS),
        )

    def test_all_seven_markets_are_present_for_each_ticket(self):
        result = calculate_ticket_market_performance(self.results)

        for ticket_name in SUPPORTED_TICKETS:
            self.assertEqual(
                set(result[ticket_name].keys()),
                set(SUPPORTED_MARKETS),
            )

    def test_each_ticket_market_returns_dictionary(self):
        result = calculate_ticket_market_performance(self.results)

        for ticket_name in SUPPORTED_TICKETS:
            for market_name in SUPPORTED_MARKETS:
                self.assertIsInstance(
                    result[ticket_name][market_name],
                    dict,
                )

    def test_each_ticket_market_contains_streaks(self):
        result = calculate_ticket_market_performance(self.results)

        for ticket_name in SUPPORTED_TICKETS:
            for market_name in SUPPORTED_MARKETS:
                self.assertIn(
                    "streaks",
                    result[ticket_name][market_name],
                )

                self.assertIsInstance(
                    result[ticket_name][market_name]["streaks"],
                    dict,
                )

    def test_safe_home_win_metrics_are_correct(self):
        result = calculate_ticket_market_performance(self.results)

        safe_home_win = result["SAFE"]["home_win"]

        self.assertEqual(
            safe_home_win["total_tickets"],
            3,
        )

        self.assertEqual(
            safe_home_win["wins"],
            2,
        )

        self.assertEqual(
            safe_home_win["losses"],
            1,
        )

        self.assertEqual(
            safe_home_win["total_stake"],
            30.0,
        )

        self.assertEqual(
            safe_home_win["total_return"],
            40.0,
        )

        self.assertEqual(
            safe_home_win["total_profit_loss"],
            10.0,
        )

    def test_safe_home_win_streaks_are_correct(self):
        result = calculate_ticket_market_performance(self.results)

        streaks = result["SAFE"]["home_win"]["streaks"]

        self.assertEqual(
            streaks["longest_winning_streak"],
            2,
        )

        self.assertEqual(
            streaks["longest_losing_streak"],
            1,
        )

        self.assertEqual(
            streaks["current_streak"],
            1,
        )

        self.assertEqual(
            streaks["current_streak_type"],
            "LOSS",
        )

    def test_balanced_draw_is_calculated_independently(self):
        result = calculate_ticket_market_performance(self.results)

        balanced_draw = result["BALANCED"]["draw"]

        self.assertEqual(
            balanced_draw["total_tickets"],
            2,
        )

        self.assertEqual(
            balanced_draw["wins"],
            1,
        )

        self.assertEqual(
            balanced_draw["losses"],
            1,
        )

        self.assertEqual(
            balanced_draw["total_profit_loss"],
            0.0,
        )

    def test_aggressive_over_2_5_all_losses(self):
        result = calculate_ticket_market_performance(self.results)

        metrics = result["AGGRESSIVE"]["over_2_5"]

        self.assertEqual(
            metrics["wins"],
            0,
        )

        self.assertEqual(
            metrics["losses"],
            2,
        )

        self.assertEqual(
            metrics["total_profit_loss"],
            -10.0,
        )

        self.assertEqual(
            metrics["streaks"]["longest_losing_streak"],
            2,
        )

    def test_value_btts_yes_all_wins(self):
        result = calculate_ticket_market_performance(self.results)

        metrics = result["VALUE"]["btts_yes"]

        self.assertEqual(
            metrics["wins"],
            3,
        )

        self.assertEqual(
            metrics["losses"],
            0,
        )

        self.assertEqual(
            metrics["total_profit_loss"],
            15.0,
        )

        self.assertEqual(
            metrics["streaks"]["longest_winning_streak"],
            3,
        )

    def test_empty_ticket_market_returns_zero_metrics(self):
        result = calculate_ticket_market_performance(self.results)

        metrics = result["SAFE"]["draw"]

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

        self.assertEqual(
            metrics["total_profit_loss"],
            0,
        )

        self.assertEqual(
            metrics["streaks"]["total_results"],
            0,
        )

    def test_invalid_ticket_name_is_rejected(self):
        invalid_results = {
            **self.results,
            "UNKNOWN": {
                market: []
                for market in SUPPORTED_MARKETS
            },
        }

        with self.assertRaises(ValueError):
            calculate_ticket_market_performance(invalid_results)

    def test_missing_ticket_name_is_rejected(self):
        invalid_results = dict(self.results)
        invalid_results.pop("SAFE")

        with self.assertRaises(ValueError):
            calculate_ticket_market_performance(invalid_results)

    def test_invalid_market_name_is_rejected(self):
        invalid_results = {
            ticket: dict(markets)
            for ticket, markets in self.results.items()
        }

        invalid_results["SAFE"]["unknown_market"] = []

        with self.assertRaises(ValueError):
            calculate_ticket_market_performance(invalid_results)

    def test_missing_market_name_is_rejected(self):
        invalid_results = {
            ticket: dict(markets)
            for ticket, markets in self.results.items()
        }

        invalid_results["SAFE"].pop("draw")

        with self.assertRaises(ValueError):
            calculate_ticket_market_performance(invalid_results)

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_ticket_market_performance([])


if __name__ == "__main__":
    unittest.main()
