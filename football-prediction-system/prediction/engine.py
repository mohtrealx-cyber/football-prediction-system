import math


def _validate_expected_goals(value, name):
    """Validate an expected-goals value."""

    # Boolean values are not valid expected-goals values.
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")

    # Expected goals must be numeric.
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")

    # Reject NaN and infinity.
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    # Expected goals must be greater than zero.
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")


def _validate_max_goals(max_goals):
    """Validate the maximum goals used by the Poisson calculation."""

    if isinstance(max_goals, bool):
        raise ValueError("max_goals must be an integer")

    if not isinstance(max_goals, int):
        raise ValueError("max_goals must be an integer")

    if max_goals <= 0:
        raise ValueError("max_goals must be greater than zero")


def _poisson_probability(expected_goals, goals):
    """Calculate the Poisson probability of a specific goals count."""

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

    # Validate expected goals.
    _validate_expected_goals(
        expected_home_goals,
        "expected_home_goals",
    )

    _validate_expected_goals(
        expected_away_goals,
        "expected_away_goals",
    )

    # Validate maximum goals.
    _validate_max_goals(max_goals)

    # Create Poisson distributions for home and away goals.
    home_distribution = [
        _poisson_probability(
            expected_home_goals,
            goals,
        )
        for goals in range(max_goals + 1)
    ]

    away_distribution = [
        _poisson_probability(
            expected_away_goals,
            goals,
        )
        for goals in range(max_goals + 1)
    ]

    # Match result probabilities.
    home_win = 0.0
    draw = 0.0
    away_win = 0.0

    # Goals market.
    over_2_5 = 0.0

    # Both Teams To Score.
    btts_yes = 0.0

    # Combine both Poisson distributions.
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):

            probability = (
                home_distribution[home_goals]
                * away_distribution[away_goals]
            )

            # Home / Draw / Away.
            if home_goals > away_goals:
                home_win += probability

            elif home_goals == away_goals:
                draw += probability

            else:
                away_win += probability

            # Over 2.5 goals.
            if home_goals + away_goals > 2:
                over_2_5 += probability

            # BTTS Yes.
            if home_goals >= 1 and away_goals >= 1:
                btts_yes += probability

    # Complementary markets.
    under_2_5 = 1.0 - over_2_5
    btts_no = 1.0 - btts_yes

    # Normalize Home/Draw/Away because the Poisson distribution
    # is truncated at max_goals.
    match_result_total = (
        home_win
        + draw
        + away_win
    )

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
