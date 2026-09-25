import math
from datetime import timedelta

from data.models import Match
from data.features import build_match_features
from prediction.feature_prediction import predict_match_from_features
from backtesting.engine import backtest_selection
from markets.engine import get_supported_markets
from data.historical_models import HistoricalMatch


MIN_EXPECTED_GOALS = 0.0001


def _validate_stake(stake: float) -> float:
    """Validate and normalize the rolling backtest stake."""
    if not isinstance(stake, (int, float)) or isinstance(stake, bool):
        raise TypeError("stake must be numeric")

    stake = float(stake)

    if not math.isfinite(stake):
        raise ValueError("stake must be finite")

    if stake <= 0:
        raise ValueError("stake must be greater than 0")

    return stake


def _historical_to_match(historical_match: HistoricalMatch) -> Match:
    """Convert a HistoricalMatch into the Match type used by feature engineering."""
    if not isinstance(historical_match, HistoricalMatch):
        raise TypeError("historical_match must be a HistoricalMatch")

    return Match(
        match_id=historical_match.match_id,
        home_team=historical_match.home_team,
        away_team=historical_match.away_team,
        league=historical_match.league,
        kickoff=historical_match.kickoff,
        status="scheduled",
        odds=dict(historical_match.odds),
    )


def _stabilize_goal_baselines(features: dict) -> dict:
    """
    Prevent zero league goal baselines from producing zero expected goals.

    The prediction engine requires positive expected goals, so very early
    historical samples are given a tiny positive floor.
    """
    if not isinstance(features, dict):
        raise TypeError("features must be a dictionary")

    stabilized = dict(features)

    for key in (
        "league_avg_home_goals",
        "league_avg_away_goals",
    ):
        if key not in stabilized:
            raise KeyError(f"Missing required feature: {key}")

        value = stabilized[key]

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{key} must be numeric")

        value = float(value)

        if not math.isfinite(value):
            raise ValueError(f"{key} must be finite")

        if value <= 0:
            stabilized[key] = MIN_EXPECTED_GOALS
        else:
            stabilized[key] = value

    return stabilized


def rolling_backtest(
    matches: list[HistoricalMatch],
    market: str,
    stake: float = 1.0,
) -> list[dict]:
    """
    Run a chronological rolling historical backtest.

    For every target match, only matches played BEFORE that target kickoff
    are allowed to contribute to the features.

    The target match itself is never included in its own historical data.

    Returns one result dictionary per backtested selection.
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every item must be a HistoricalMatch")

    if not isinstance(market, str):
        raise TypeError("market must be a string")

    supported_markets = get_supported_markets()

    if market not in supported_markets:
        raise ValueError(f"Unsupported market: {market}")

    stake = _validate_stake(stake)

    # Work on a copy so the caller's original list is never modified.
    ordered_matches = sorted(matches, key=lambda match: match.kickoff)

    results: list[dict] = []

    for target_match in ordered_matches:
        # Strictly earlier matches only.
        previous_matches = [
            historical_match
            for historical_match in ordered_matches
            if historical_match.kickoff < target_match.kickoff
        ]

        # A model cannot be evaluated without historical information.
        if not previous_matches:
            continue

        # Feature engineering currently expects data.models.Match.
        feature_target = _historical_to_match(target_match)

        features = build_match_features(
            target_match=feature_target,
            historical_matches=previous_matches,
        )

        # Protect the early part of the dataset from zero goal baselines.
        features = _stabilize_goal_baselines(features)

        predictions = predict_match_from_features(features)

        if market not in predictions:
            raise KeyError(
                f"Prediction output does not contain market: {market}"
            )

        model_probability = predictions[market]

        if not isinstance(model_probability, (int, float)):
            raise TypeError("model probability must be numeric")

        model_probability = float(model_probability)

        if not math.isfinite(model_probability):
            raise ValueError("model probability must be finite")

        if not 0 <= model_probability <= 1:
            raise ValueError("model probability must be between 0 and 1")

        # A historical match may not contain odds for every supported market.
        odds = target_match.odds.get(market)

        if odds is None:
            continue

        if not isinstance(odds, (int, float)) or isinstance(odds, bool):
            raise TypeError("odds must be numeric")

        odds = float(odds)

        if not math.isfinite(odds):
            raise ValueError("odds must be finite")

        if odds <= 1:
            raise ValueError("odds must be greater than 1")

        # Settlement must use the original HistoricalMatch because it contains
        # the actual final score.
        settlement = backtest_selection(
            match=target_match,
            market=market,
            odds=odds,
            stake=stake,
        )

        # The cutoff is deliberately STRICTLY earlier than the target kickoff.
        history_cutoff = target_match.kickoff - timedelta(
            microseconds=1
        )

        results.append(
            {
                "match_id": target_match.match_id,
                "home_team": target_match.home_team,
                "away_team": target_match.away_team,
                "league": target_match.league,
                "kickoff": target_match.kickoff,
                "market": market,
                "model_probability": model_probability,
                "odds": odds,
                "stake": settlement["stake"],
                "won": settlement["won"],
                "return_amount": settlement["return_amount"],
                "profit_loss": settlement["profit_loss"],
                "history_matches": len(previous_matches),
                "history_cutoff": history_cutoff,
                "history_last_match_id": previous_matches[-1].match_id,
            }
        )

    return results
