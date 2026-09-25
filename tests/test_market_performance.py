import unittest

from performance.market import calculate_market_performance


class MarketPerformanceTests(unittest.TestCase):

    def setUp(self):
        self.results = {
            "home_win": [
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
                    "stake": 20.0,
                    "won": True,
                    "return_amount": 40.0,
                    "profit_loss": 20.0,
                },
            ],
            "draw": [
                {
                    "stake": 10.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -10.0,
                },
                {
                    "stake": 10.0,
                    "won": True,
                    "return_amount": 30.0,
                    "profit_loss": 20.0,
                },
            ],
            "away_win": [],
            "over_2_5": [
                {
                    "stake": 20.0,
                    "won": True,
                    "return_amount": 50.0,
                    "profit_loss": 30.0,
                },
            ],
            "under_2_5": [
                {
                    "stake": 20.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -20.0,
                },
            ],
            "btts_yes": [
                {
                    "stake": 15.0,
                    "won": True,
                    "return_amount": 30.0,
                    "profit_loss": 15.0,
                },
            ],
            "btts_no": [
                {
                    "stake": 15.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -15.0,
                },
            ],
        }

    def test_returns_dictionary(self):
        result = calculate_market_performance(self.results)

        self.assertIsInstance(result, dict)

    def test_all_seven_markets_are_present(self):
        result = calculate_market_performance(self.results)

        expected_markets = {
            "home_win",
            "draw",
            "away_win",
            "over_2_5",
            "under_2_5",
            "btts_yes",
            "btts_no",
        }

        self.assertEqual(
            set(result.keys()),
            expected_markets,
        )

    def test_each_market_returns_dictionary(self):
        result = calculate_market_performance(self.results)

        for market_result in result.values():
            self.assertIsInstance(
                market_result,
                dict,
            )

    def test_home_win_total_tickets(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["total_tickets"],
            3,
        )

    def test_home_win_wins_are_counted(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["wins"],
            2,
        )

    def test_home_win_losses_are_counted(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["losses"],
            1,
        )

    def test_home_win_total_stake(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["total_stake"],
            40.0,
        )

    def test_home_win_total_return(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["total_return"],
            60.0,
        )

    def test_home_win_profit_loss(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["total_profit_loss"],
            20.0,
        )

    def test_home_win_roi(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["home_win"]["roi"],
            0.5,
        )

    def test_draw_metrics_are_calculated_separately(self):
        result = calculate_market_performance(self.results)

        self.assertEqual(
            result["draw"]["total_tickets"],
            2,
        )

        self.assertEqual(
            result["draw"]["wins"],
            1,
        )

        self.assertEqual(
            result["draw"]["losses"],
            1,
        )

        self.assertEqual(
            result["draw"]["total_stake"],
            20.0,
        )

        self.assertEqual(
            result["draw"]["total_return"],
            30.0,
        )

        self.assertEqual(
            result["draw"]["total_profit_loss"],
            10.0,
        )

    def test_empty_market_returns_zero_metrics(self):
        result = calculate_market_performance(self.results)

        empty_result = result["away_win"]

        self.assertEqual(
            empty_result["total_tickets"],
            0,
        )

        self.assertEqual(
            empty_result["wins"],
            0,
        )

        self.assertEqual(
            empty_result["losses"],
            0,
        )

        self.assertEqual(
            empty_result["total_stake"],
            0.0,
        )

        self.assertEqual(
            empty_result["total_return"],
            0.0,
        )

        self.assertEqual(
            empty_result["total_profit_loss"],
            0.0,
        )

        self.assertEqual(
            empty_result["roi"],
            0.0,
        )

        self.assertEqual(
            empty_result["max_drawdown"],
            0.0,
        )

    def test_max_drawdown_is_preserved_from_market_results(self):
        result = calculate_market_performance(self.results)

        self.assertGreaterEqual(
            result["home_win"]["max_drawdown"],
            0.0,
        )

    def test_all_market_metrics_have_same_structure(self):
        result = calculate_market_performance(self.results)

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

        for market_result in result.values():
            self.assertEqual(
                set(market_result.keys()),
                expected_fields,
            )

    def test_market_results_are_independent(self):
        result = calculate_market_performance(self.results)

        self.assertNotEqual(
            result["home_win"]["total_tickets"],
            result["draw"]["total_tickets"],
        )

        self.assertNotEqual(
            result["home_win"]["total_stake"],
            result["draw"]["total_stake"],
        )

    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_market_performance([])

    def test_invalid_market_result_is_rejected(self):
        invalid_results = {
            "home_win": [
                {
                    "stake": 10.0,
                    "won": True,
                }
            ]
        }

        with self.assertRaises(ValueError):
            calculate_market_performance(invalid_results)

    def test_invalid_market_name_is_rejected(self):
        invalid_results = {
            "invalid_market": []
        }

        with self.assertRaises(ValueError):
            calculate_market_performance(invalid_results)


if __name__ == "__main__":
    unittest.main()
