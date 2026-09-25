import math

from data.models import Match
from data.features import build_match_features
from prediction.feature_prediction import predict_match_from_features
from backtesting.engine import backtest_selection
from markets.engine import get_supported_markets
from data.historical_models import HistoricalMatch


# Small positive floor used only when a very small historical
# sample produces a zero league-goal baseline.
MIN_EXPECTED_GOALS = 0.0001


def _validate_stake(stake):
    if isinstance(stake, bool) or not isinstance(stake, (int, float)):
        raise ValueError("stake must be numeric")

    if not math.isfinite(stake):
        raise ValueError("stake must be finite")

    if stake <= 0:
        raise ValueError("stake must be greater than zero")


def _historical_to_match(
    historical_match: HistoricalMatch,
) -> Match:
    """
    Convert HistoricalMatch into the Match structure required
    by the feature-engineering layer.
    """

    return Match(
        match_id=historical_match.match_id,
        home_team=historical_match.home_team,
        away_team=historical_match.away_team,
        league=historical_match.league,
        kickoff=historical_match.kickoff,
        status="finished",
        odds=dict(historical_match.odds),
    )


def _stabilize_goal_baselines(features: dict) -> dict:
    """
    Prevent zero league-goal baselines from creating impossible
    expected-goal values during the earliest rolling windows.

    This only affects the rolling backtest. The core prediction
    engine continues to reject truly invalid zero expected goals.
    """

    stabilized = dict(features)

    for key in (
        "league_avg_home_goals",
        "league_avg_away_goals",
    ):
        value = stabilized.get(key)

        if value is None:
            raise ValueError(
                f"Missing required feature: {key}"
            )

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Feature {key} must be numeric"
            )

        if not math.isfinite(value):
            raise ValueError(
                f"Feature {key} must be finite"
            )

        if value <= 0:
            stabilized[key] = MIN_EXPECTED_GOALS

    return stabilized


def rolling_backtest(
    matches: list,
    market: str,
    stake: float = 1.0,
) -> list:
    """
    Perform a chronological historical backtest.

    Every target match is predicted using only historical
    matches that occurred strictly before the target kickoff.
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    if not isinstance(market, str):
        raise ValueError("market must be a string")

    if market not in get_supported_markets():
        raise ValueError(
            f"Unsupported market: {market}"
        )

    _validate_stake(stake)

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError(
                "Every item must be a HistoricalMatch"
            )

    ordered_matches = sorted(
        matches,
        key=lambda match: match.kickoff,
    )

    results = []

    for index, target_match in enumerate(ordered_matches):

        previous_matches = [
            historical_match
            for historical_match in ordered_matches[:index]
            if historical_match.kickoff < target_match.kickoff
        ]

        # No historical information exists yet.
        if not previous_matches:
            continue

        feature_target = _historical_to_match(
            target_match
        )

        features = build_match_features(
            target_match=feature_target,
            historical_matches=previous_matches,
        )

        # Early rolling windows can contain a zero league-goal
        # baseline. Stabilize that input without changing the
        # core prediction engine's validation rules.
        features = _stabilize_goal_baselines(
            features
        )

        predictions = predict_match_from_features(
            features
        )

        model_probability = predictions[market]

        odds = target_match.odds.get(market)

        if odds is None:
            continue

        result = backtest_selection(
            match=target_match,
            market=market,
            odds=odds,
            stake=stake,
        )

        results.append(
            {
                "match_id": target_match.match_id,
                "home_team": target_match.home_team,
                "away_team": target_match.away_team,
                "league": target_match.league,
                "kickoff": target_match.kickoff,
                "market": market,
                "model_probability": float(
                    model_probability
                ),
                "odds": float(odds),
                "stake": result["stake"],
                "won": result["won"],
                "return_amount": result["return_amount"],
                "profit_loss": result["profit_loss"],
                "history_matches": len(
                    previous_matches
                ),
                "history_cutoff": target_match.kickoff,
                "history_last_match_id": (
                    previous_matches[-1].match_id
                ),
            }
        )

    return results
