from prediction.engine import predict_match
from prediction.feature_model import predict_from_features


def predict_match_from_features(features: dict) -> dict:
    """
    Convert engineered features into full football market
    probabilities.

    The feature model first produces expected goals.
    The existing Poisson prediction engine then converts those
    expected goals into market probabilities.
    """

    if not isinstance(features, dict):
        raise TypeError("features must be a dictionary")

    expected_goals = predict_from_features(features)

    expected_home_goals = expected_goals["expected_home_goals"]
    expected_away_goals = expected_goals["expected_away_goals"]

    predictions = predict_match(
        expected_home_goals,
        expected_away_goals,
    )

    return {
        "expected_home_goals": expected_home_goals,
        "expected_away_goals": expected_away_goals,
        **predictions,
    }
