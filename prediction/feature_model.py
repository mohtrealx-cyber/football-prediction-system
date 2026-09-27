REQUIRED_FEATURES = {
    "home_attack_strength",
    "home_defense_strength",
    "away_attack_strength",
    "away_defense_strength",
    "home_recent_points",
    "away_recent_points",
    "home_form_goals_for",
    "away_form_goals_for",
    "home_home_avg_goals",
    "away_away_avg_goals",
    "league_avg_home_goals",
    "league_avg_away_goals",
}


# Conservative neutral scoring baselines.
#
# These are fallback values only when the historical dataset
# produces a zero league scoring average.
NEUTRAL_HOME_GOALS = 1.20
NEUTRAL_AWAY_GOALS = 1.00


def predict_from_features(features: dict) -> dict:
    """
    Convert engineered historical features into expected goals.

    V3.9 baseline model:

        league scoring baseline
        × attacking strength
        × opponent defensive factor

    If the historical feature calculation produces a zero
    league scoring baseline, use a neutral positive baseline
    so the downstream Poisson engine can operate.

    The fallback is intentionally applied only to a zero
    league baseline. Negative feature values remain invalid.
    """

    if not isinstance(features, dict):
        raise TypeError("features must be a dictionary")

    missing = REQUIRED_FEATURES - features.keys()

    if missing:
        raise ValueError(
            f"Missing required features: {sorted(missing)}"
        )

    for name in REQUIRED_FEATURES:
        value = features[name]

        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Feature '{name}' must be numeric"
            )

        if value < 0:
            raise ValueError(
                f"Feature '{name}' must be non-negative"
            )

    league_home = features["league_avg_home_goals"]
    league_away = features["league_avg_away_goals"]

    if league_home < 0 or league_away < 0:
        raise ValueError(
            "League averages must be non-negative"
        )

    # ---------------------------------------------------------
    # LEAGUE BASELINE
    # ---------------------------------------------------------
    #
    # A zero league average can occur when the historical
    # dataset is too small or contains no usable scoring data.
    #
    # The prediction engine requires positive expected goals,
    # so use a neutral baseline rather than passing zero
    # downstream.
    #
    if league_home == 0:
        league_home = NEUTRAL_HOME_GOALS

    if league_away == 0:
        league_away = NEUTRAL_AWAY_GOALS

    # ---------------------------------------------------------
    # TEAM STRENGTH FACTORS
    # ---------------------------------------------------------

    home_attack = features["home_attack_strength"]
    away_attack = features["away_attack_strength"]

    home_defense = features["home_defense_strength"]
    away_defense = features["away_defense_strength"]

    # Neutral factor when insufficient historical information
    # produces a zero team-strength value.
    home_attack_factor = (
        home_attack if home_attack > 0 else 1.0
    )

    away_attack_factor = (
        away_attack if away_attack > 0 else 1.0
    )

    home_defense_factor = (
        home_defense if home_defense > 0 else 1.0
    )

    away_defense_factor = (
        away_defense if away_defense > 0 else 1.0
    )

    # ---------------------------------------------------------
    # EXPECTED GOALS
    # ---------------------------------------------------------

    expected_home_goals = (
        league_home
        * home_attack_factor
        * away_defense_factor
    )

    expected_away_goals = (
        league_away
        * away_attack_factor
        * home_defense_factor
    )

    # ---------------------------------------------------------
    # FINAL SAFETY CHECK
    # ---------------------------------------------------------

    if expected_home_goals <= 0:
        expected_home_goals = NEUTRAL_HOME_GOALS

    if expected_away_goals <= 0:
        expected_away_goals = NEUTRAL_AWAY_GOALS

    return {
        "expected_home_goals": float(
            expected_home_goals
        ),
        "expected_away_goals": float(
            expected_away_goals
        ),
    }
