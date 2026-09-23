
import math
from typing import Dict


def poisson_probability(goals: int, expected_goals: float) -> float:
    """
    Probability of a team scoring exactly `goals`,
    when its expected goals is `expected_goals`.
    """
    if expected_goals < 0:
        raise ValueError("expected_goals cannot be negative")

    return (
        math.exp(-expected_goals)
        * (expected_goals ** goals)
        / math.factorial(goals)
    )


def predict_match(
    home_expected_goals: float,
    away_expected_goals: float,
    max_goals: int = 10,
) -> Dict[str, float]:

    if home_expected_goals <= 0:
        raise ValueError("home_expected_goals must be greater than 0")

    if away_expected_goals <= 0:
        raise ValueError("away_expected_goals must be greater than 0")

    if max_goals < 1:
        raise ValueError("max_goals must be at least 1")

    home_probs = [
        poisson_probability(i, home_expected_goals)
        for i in range(max_goals + 1)
    ]

    away_probs = [
        poisson_probability(i, away_expected_goals)
        for i in range(max_goals + 1)
    ]

    home_win = 0.0
    draw = 0.0
    away_win = 0.0
    over_2_5 = 0.0
    btts_yes = 0.0

    for home_goals, home_prob in enumerate(home_probs):
        for away_goals, away_prob in enumerate(away_probs):

            score_probability = home_prob * away_prob

            if home_goals > away_goals:
                home_win += score_probability

            elif home_goals == away_goals:
                draw += score_probability

            else:
                away_win += score_probability

            if home_goals + away_goals >= 3:
                over_2_5 += score_probability

            if home_goals >= 1 and away_goals >= 1:
                btts_yes += score_probability

    under_2_5 = 1.0 - over_2_5
    btts_no = 1.0 - btts_yes

    return {
        "home_win": round(home_win, 6),
        "draw": round(draw, 6),
        "away_win": round(away_win, 6),
        "over_2_5": round(over_2_5, 6),
        "under_2_5": round(under_2_5, 6),
        "btts_yes": round(btts_yes, 6),
        "btts_no": round(btts_no, 6),
    }
