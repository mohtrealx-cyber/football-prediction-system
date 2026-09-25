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
