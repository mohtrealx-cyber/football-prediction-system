import math


def _poisson_probability(expected_goals, goals):
    """Calculate Poisson probability for an exact goals value."""
    return (
        math.exp(-expected_goals)
        * (expected_goals ** goals)
        / math.factorial(goals)
    )


def predict_match(
    expected_home_goals,
    expected_away_goals,
    max_goals=10,
):
    """
    Convert expected goals into football market probabilities.

    Returns:
        home_win
        draw
        away_win
        over_2_5
        under_2_5
        btts_yes
        btts_no
    """

    # Validate home expected goals.
    if isinstance(expected_home_goals, bool):
        raise ValueError(
            "expected_home_goals must be greater than zero"
        )

    if not isinstance(expected_home_goals, (int, float)):
        raise ValueError(
            "expected_home_goals must be a number"
        )

    if not math.isfinite(expected_home_goals):
        raise ValueError(
            "expected_home_goals must be finite"
        )

    if expected_home_goals <= 0:
        raise ValueError(
            "expected_home_goals must be greater than zero"
        )

    # Validate away expected goals.
    if isinstance(expected_away_goals, bool):
        raise ValueError(
            "expected_away_goals must be greater than zero"
        )

    if not isinstance(expected_away_goals, (int, float)):
        raise ValueError(
            "expected_away_goals must be a number"
        )

    if not math.isfinite(expected_away_goals):
        raise ValueError(
            "expected_away_goals must be finite"
        )

    if expected_away_goals <= 0:
        raise ValueError(
            "expected_away_goals must be greater than zero"
        )

    # Validate maximum goals.
    if isinstance(max_goals, bool):
        raise ValueError(
            "max_goals must be a positive integer"
        )

    if not isinstance(max_goals, int):
        raise ValueError(
            "max_goals must be a positive integer"
        )

    if max_goals <= 0:
        raise ValueError(
            "max_goals must be greater than zero"
        )

    # Build Poisson distributions.
    home_distribution = [
        _poisson_probability(expected_home_goals, goals)
        for goals in range(max_goals + 1)
    ]

    away_distribution = [
        _poisson_probability(expected_away_goals, goals)
        for goals in range(max_goals + 1)
    ]

    home_win = 0.0
    draw = 0.0
    away_win = 0.0
    over_2_5 = 0.0
    btts_yes = 0.0

    # Calculate market probabilities.
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):

            probability = (
                home_distribution[home_goals]
                * away_distribution[away_goals]
            )

            if home_goals > away_goals:
                home_win += probability

            elif home_goals == away_goals:
                draw += probability

            else:
                away_win += probability

            if home_goals + away_goals > 2:
                over_2_5 += probability

            if home_goals >= 1 and away_goals >= 1:
                btts_yes += probability

    under_2_5 = 1.0 - over_2_5
    btts_no = 1.0 - btts_yes

    # Normalize Home / Draw / Away because the goal
    # distribution is truncated at max_goals.
    match_result_total = home_win + draw + away_win

    if match_result_total <= 0:
        raise ValueError(
            "Unable to calculate match result probabilities"
        )

    home_win /= match_result_total
    draw /= match_result_total
    away_win /= match_result_total

    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "over_2_5": over_2_5,
        "under_2_5": under_2_5,
        "btts_yes": btts_yes,
        "btts_no": btts_no,
    }
