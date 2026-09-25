import math

from data.features import build_match_features
from prediction.feature_prediction import predict_match_from_features
from backtesting.engine import backtest_selection
from markets.engine import get_supported_markets
from data.historical_models import HistoricalMatch


def _validate_stake(stake):
    if isinstance(stake, bool) or not isinstance(stake, (int, float)):
        raise ValueError("stake must be numeric")

    if not math.isfinite(stake):
        raise ValueError("stake must be finite")

    if stake <= 0:
        raise ValueError("stake must be greater than zero")


def rolling_backtest(
    matches: list,
    market: str,
    stake: float = 1.0,
) -> list:
    """
    Perform a chronological historical backtest.

    Each target match is predicted using only matches that
    occurred before that target match.
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    if not isinstance(market, str):
        raise ValueError("market must be a string")

    if market not in get_supported_markets():
        raise ValueError(f"Unsupported market: {market}")

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

        # There is no information available to make a
        # meaningful historical prediction for the first match.
        if not previous_matches:
            continue

        features = build_match_features(
            target_match=target_match,
            historical_matches=previous_matches,
        )

        predictions = predict_match_from_features(
            features
        )

        model_probability = predictions[market]

        odds = target_match.odds.get(market)

        # A historical selection cannot be backtested without
        # usable odds for the requested market.
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
                "history_matches": len(previous_matches),
                "history_cutoff": target_match.kickoff,
                "history_last_match_id": (
                    previous_matches[-1].match_id
                ),
            }
        )

    return results
