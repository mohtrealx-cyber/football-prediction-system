import unittest

from performance.streaks import calculate_streaks


class StreakTests(unittest.TestCase):

    def test_returns_dictionary(self):
        results = [
            {"won": True},
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertIsInstance(result, dict)

    def test_empty_results_return_zero_streaks(self):
        result = calculate_streaks([])

        self.assertEqual(result["total_results"], 0)
        self.assertEqual(result["current_streak"], 0)
        self.assertIsNone(result["current_streak_type"])
        self.assertEqual(result["longest_winning_streak"], 0)
        self.assertEqual(result["longest_losing_streak"], 0)

    def test_all_wins_create_winning_streak(self):
        results = [
            {"won": True},
            {"won": True},
            {"won": True},
            {"won": True},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["total_results"], 4)
        self.assertEqual(result["current_streak"], 4)
        self.assertEqual(result["current_streak_type"], "WIN")
        self.assertEqual(result["longest_winning_streak"], 4)
        self.assertEqual(result["longest_losing_streak"], 0)

    def test_all_losses_create_losing_streak(self):
        results = [
            {"won": False},
            {"won": False},
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["total_results"], 3)
        self.assertEqual(result["current_streak"], 3)
        self.assertEqual(result["current_streak_type"], "LOSS")
        self.assertEqual(result["longest_winning_streak"], 0)
        self.assertEqual(result["longest_losing_streak"], 3)

    def test_win_streak_is_reset_by_loss(self):
        results = [
            {"won": True},
            {"won": True},
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["current_streak"], 1)
        self.assertEqual(result["current_streak_type"], "LOSS")
        self.assertEqual(result["longest_winning_streak"], 2)
        self.assertEqual(result["longest_losing_streak"], 1)

    def test_loss_streak_is_reset_by_win(self):
        results = [
            {"won": False},
            {"won": False},
            {"won": True},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["current_streak"], 1)
        self.assertEqual(result["current_streak_type"], "WIN")
        self.assertEqual(result["longest_winning_streak"], 1)
        self.assertEqual(result["longest_losing_streak"], 2)

    def test_longest_winning_streak_is_preserved(self):
        results = [
            {"won": True},
            {"won": True},
            {"won": False},
            {"won": True},
            {"won": True},
            {"won": True},
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["longest_winning_streak"], 3)

    def test_longest_losing_streak_is_preserved(self):
        results = [
            {"won": False},
            {"won": True},
            {"won": False},
            {"won": False},
            {"won": False},
            {"won": True},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["longest_losing_streak"], 3)

    def test_current_streak_is_last_sequence(self):
        results = [
            {"won": True},
            {"won": True},
            {"won": False},
            {"won": False},
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["current_streak"], 3)
        self.assertEqual(result["current_streak_type"], "LOSS")

    def test_single_win_is_one_win_streak(self):
        results = [
            {"won": True},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["current_streak"], 1)
        self.assertEqual(result["current_streak_type"], "WIN")
        self.assertEqual(result["longest_winning_streak"], 1)
        self.assertEqual(result["longest_losing_streak"], 0)

    def test_single_loss_is_one_loss_streak(self):
        results = [
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["current_streak"], 1)
        self.assertEqual(result["current_streak_type"], "LOSS")
        self.assertEqual(result["longest_winning_streak"], 0)
        self.assertEqual(result["longest_losing_streak"], 1)

    def test_alternating_results_have_no_long_streak(self):
        results = [
            {"won": True},
            {"won": False},
            {"won": True},
            {"won": False},
            {"won": True},
            {"won": False},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["longest_winning_streak"], 1)
        self.assertEqual(result["longest_losing_streak"], 1)
        self.assertEqual(result["current_streak"], 1)
        self.assertEqual(result["current_streak_type"], "LOSS")

    def test_total_results_is_correct(self):
        results = [
            {"won": True},
            {"won": False},
            {"won": True},
            {"won": True},
        ]

        result = calculate_streaks(results)

        self.assertEqual(result["total_results"], 4)

    def test_input_list_is_not_modified(self):
        results = [
            {"won": True},
            {"won": False},
            {"won": True},
        ]

        original = [dict(item) for item in results]

        calculate_streaks(results)

        self.assertEqual(results, original)

    def test_non_list_input_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_streaks({})

    def test_invalid_result_item_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_streaks([
                {"won": True},
                "invalid",
            ])

    def test_missing_won_field_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_streaks([
                {"won": True},
                {},
            ])

    def test_won_must_be_boolean(self):
        with self.assertRaises(TypeError):
            calculate_streaks([
                {"won": 1},
            ])


if __name__ == "__main__":
    unittest.main()
