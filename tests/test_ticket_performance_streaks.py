import unittest

from performance.ticket import calculate_ticket_performance


class TicketPerformanceStreaksTests(unittest.TestCase):

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
                {
                    "stake": 30.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -30.0,
                },
            ],
            "AGGRESSIVE": [
                {
                    "stake": 20.0,
                    "won": False,
                    "return_amount": 0.0,
                    "profit_loss": -20.0,
                },
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
                    "return_amount": 20.0,
                    "profit_loss": 10.0,
                },
            ],
        }

    def test_each_ticket_contains_streaks(self):
        result = calculate_ticket_performance(self.results)

        for ticket_name in (
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ):
            self.assertIn(
                "streaks",
                result[ticket_name],
            )

    def test_streaks_are_dictionaries(self):
        result = calculate_ticket_performance(self.results)

        for ticket_name in (
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ):
            self.assertIsInstance(
                result[ticket_name]["streaks"],
                dict,
            )

    def test_safe_streaks_are_correct(self):
        result = calculate_ticket_performance(self.results)

        streaks = result["SAFE"]["streaks"]

        self.assertEqual(
            streaks["total_results"],
            3,
        )

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

    def test_balanced_streaks_are_correct(self):
        result = calculate_ticket_performance(self.results)

        streaks = result["BALANCED"]["streaks"]

        self.assertEqual(
            streaks["total_results"],
            2,
        )

        self.assertEqual(
            streaks["longest_winning_streak"],
            1,
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

    def test_aggressive_streaks_are_correct(self):
        result = calculate_ticket_performance(self.results)

        streaks = result["AGGRESSIVE"]["streaks"]

        self.assertEqual(
            streaks["total_results"],
            2,
        )

        self.assertEqual(
            streaks["longest_losing_streak"],
            2,
        )

        self.assertEqual(
            streaks["current_streak"],
            2,
        )

        self.assertEqual(
            streaks["current_streak_type"],
            "LOSS",
        )

    def test_value_streaks_are_correct(self):
        result = calculate_ticket_performance(self.results)

        streaks = result["VALUE"]["streaks"]

        self.assertEqual(
            streaks["total_results"],
            1,
        )

        self.assertEqual(
            streaks["longest_winning_streak"],
            1,
        )

        self.assertEqual(
            streaks["current_streak"],
            1,
        )

        self.assertEqual(
            streaks["current_streak_type"],
            "WIN",
        )

    def test_existing_performance_metrics_are_preserved(self):
        result = calculate_ticket_performance(self.results)

        self.assertEqual(
            result["SAFE"]["total_tickets"],
            3,
        )

        self.assertEqual(
            result["SAFE"]["wins"],
            2,
        )

        self.assertEqual(
            result["SAFE"]["losses"],
            1,
        )

        self.assertEqual(
            result["AGGRESSIVE"]["total_tickets"],
            2,
        )

    def test_empty_ticket_has_zero_streaks(self):
        results = dict(self.results)
        results["VALUE"] = []

        result = calculate_ticket_performance(results)

        streaks = result["VALUE"]["streaks"]

        self.assertEqual(
            streaks["total_results"],
            0,
        )

        self.assertEqual(
            streaks["current_streak"],
            0,
        )

        self.assertIsNone(
            streaks["current_streak_type"],
        )

        self.assertEqual(
            streaks["longest_winning_streak"],
            0,
        )

        self.assertEqual(
            streaks["longest_losing_streak"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
