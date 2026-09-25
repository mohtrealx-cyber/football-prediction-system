def calculate_streaks(results: list) -> dict:
    """
    Calculate winning and losing streak statistics.

    The results list must contain dictionaries with a boolean
    'won' field.

    Returns:
        total_results
        current_streak
        current_streak_type
        longest_winning_streak
        longest_losing_streak
    """

    if not isinstance(results, list):
        raise TypeError("results must be a list")

    total_results = len(results)

    if total_results == 0:
        return {
            "total_results": 0,
            "current_streak": 0,
            "current_streak_type": None,
            "longest_winning_streak": 0,
            "longest_losing_streak": 0,
        }

    longest_winning_streak = 0
    longest_losing_streak = 0

    current_streak = 0
    current_streak_type = None

    for result in results:
        if not isinstance(result, dict):
            raise TypeError("each result must be a dictionary")

        if "won" not in result:
            raise ValueError("each result must contain 'won'")

        won = result["won"]

        if not isinstance(won, bool):
            raise TypeError("'won' must be a boolean")

        if won:
            if current_streak_type == "WIN":
                current_streak += 1
            else:
                current_streak = 1
                current_streak_type = "WIN"

            if current_streak > longest_winning_streak:
                longest_winning_streak = current_streak

        else:
            if current_streak_type == "LOSS":
                current_streak += 1
            else:
                current_streak = 1
                current_streak_type = "LOSS"

            if current_streak > longest_losing_streak:
                longest_losing_streak = current_streak

    return {
        "total_results": total_results,
        "current_streak": current_streak,
        "current_streak_type": current_streak_type,
        "longest_winning_streak": longest_winning_streak,
        "longest_losing_streak": longest_losing_streak,
    }
