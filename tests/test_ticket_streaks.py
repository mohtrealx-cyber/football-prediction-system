import unittest

from performance.streaks import calculate_streaks


class TicketStreakTests(unittest.TestCase):

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

    def test_safe_streaks_can_be_calculated(self):
        result = calculate_streaks(self.results["SAFE"])

        self.assertEqual(
            result["total_results"],
            3,
        )

    def test_safe_longest_winning_streak(self):
        result = calculate_streaks(self.results["SAFE"])

        self.assertEqual(
            result["longest_winning_streak"],
            2,
        )

    def test_safe_current_streak(self):
        result = calculate_streaks(self.results["SAFE"])

        self.assertEqual(
            result["current_streak"],
            1,
        )

    def test_safe_current_streak_type(self):
        result = calculate_streaks(self.results["SAFE"])

        self.assertEqual(
            result["current_streak_type"],
            "LOSS",
        )

    def test_balanced_streaks_are_independent(self):
        safe_result = calculate_streaks(self.results["SAFE"])
        balanced_result = calculate_streaks(self.results["BALANCED"])

        self.assertEqual(
            safe_result["longest_winning_streak"],
            2,
        )

        self.assertEqual(
            balanced_result["longest_winning_streak"],
            1,
        )

    def test_aggressive_all_losses(self):
        result = calculate_streaks(self.results["AGGRESSIVE"])

        self.assertEqual(
            result["longest_losing_streak"],
            2,
        )

        self.assertEqual(
            result["current_streak"],
            2,
        )

        self.assertEqual(
            result["current_streak_type"],
            "LOSS",
        )

    def test_value_all_wins(self):
        result = calculate_streaks(self.results["VALUE"])

        self.assertEqual(
            result["longest_winning_streak"],
            1,
        )

        self.assertEqual(
            result["current_streak"],
            1,
        )

        self.assertEqual(
            result["current_streak_type"],
            "WIN",
        )

    def test_empty_ticket_has_zero_streaks(self):
        result = calculate_streaks([])

        self.assertEqual(
            result["total_results"],
            0,
        )

        self.assertEqual(
            result["current_streak"],
            0,
        )

        self.assertIsNone(
            result["current_streak_type"],
        )

        self.assertEqual(
            result["longest_winning_streak"],
            0,
        )

        self.assertEqual(
            result["longest_losing_streak"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
