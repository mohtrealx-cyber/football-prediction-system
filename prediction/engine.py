import math


def _validate_expected_goals(value, name):
    """Validate an expected-goals input."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def _poisson_probability(expected_goals, goals):
    """Return Poisson probability for an exact goals value."""
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

    Markets returned:
        home_win
        draw
        away_win
        over_2_5
        under_2_5
        btts_yes
        btts_no

    Expected goals are represented by the two input values.
    """

    _validate_expected_goals(expected_home_goals, "expected_home_goals")
    _validate_expected_goals(expected_away_goals, "expected_away_goals")

    if not isinstance(max_goals, int):
        raise TypeError("max_goals must be an integer")

    if max_goals <= 0:
        raise ValueError("max_goals must be greater than zero")

    # Build Poisson distributions for both teams.
    home_distribution = [
        _poisson_probability(expected_home_goals, goals)
        for goals in range(max_goals + 1)
    ]

    away_distribution = [
        _poisson_probability(expected_away_goals, goals)
        for goals in range(max_goals + 1)
    ]

    # Match result probabilities.
    home_win = 0.0
    draw = 0.0
    away_win = 0.0

    # Over 2.5 goals probability.
    over_2_5 = 0.0

    # BTTS probability.
    btts_yes = 0.0

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

    # Complementary markets.
    under_2_5 = 1.0 - over_2_5
    btts_no = 1.0 - btts_yes

    # Because the Poisson distributions are truncated at max_goals,
    # a tiny amount of probability can fall outside the calculated range.
    # Normalize Home/Draw/Away so the three mutually-exclusive outcomes
    # sum to exactly 1.0.
    match_result_total = home_win + draw + away_win

    if match_result_total > 0:
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
