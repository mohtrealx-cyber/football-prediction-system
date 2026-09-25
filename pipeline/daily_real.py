from __future__ import annotations

import math
from typing import Any

from data.historical_models import HistoricalMatch
from data.models import Match
from data.features import build_match_features
from markets.engine import get_supported_markets
from prediction.feature_prediction import predict_match_from_features


MINIMUM_VALUE_EDGE = 5.0
VALUE_EDGE_CAP = 20.0


MARKET_SELECTIONS = {
    "home_win": "HOME",
    "draw": "DRAW",
    "away_win": "AWAY",
    "over_2_5": "OVER_2_5",
    "under_2_5": "UNDER_2_5",
    "btts_yes": "BTTS_YES",
    "btts_no": "BTTS_NO",
}


def _validate_fixture(fixture: Any) -> None:
    """Validate one fixture."""
    if not isinstance(fixture, Match):
        raise TypeError("each fixture must be a Match")


def _validate_history_item(history_match: Any) -> None:
    """Validate one historical match."""
    if not isinstance(history_match, HistoricalMatch):
        raise TypeError(
            "each historical match must be a HistoricalMatch"
        )


def _calculate_score(
    model_probability: float,
    value_edge: float,
) -> float:
    """
    Calculate candidate score.

    70% = model probability.
    30% = positive value edge, capped at 20 percentage points.
    """
    capped_edge = min(
        max(value_edge, 0.0),
        VALUE_EDGE_CAP,
    )

    probability_component = model_probability * 70.0

    value_component = (
        capped_edge / VALUE_EDGE_CAP
    ) * 30.0

    return probability_component + value_component


def _build_candidate(
    fixture: Match,
    market: str,
    model_probability: float,
    selected_odds: float,
) -> dict[str, Any]:
    """Build one market candidate while preserving all fixture odds."""
    implied_probability = 1.0 / selected_odds

    expected_value = (
        model_probability * selected_odds
    ) - 1.0

    value_edge = (
        model_probability - implied_probability
    ) * 100.0

    score = _calculate_score(
        model_probability=model_probability,
        value_edge=value_edge,
    )

    return {
        "match_id": fixture.match_id,
        "home_team": fixture.home_team,
        "away_team": fixture.away_team,
        "league": fixture.league,
        "kickoff": fixture.kickoff,
        "market": market,
        "selection": MARKET_SELECTIONS[market],

        # Preserve the complete odds dictionary from the fixture.
        "odds": dict(fixture.odds),

        # Numeric odds for the specific selected market.
        "selected_odds": selected_odds,

        "model_probability": model_probability,
        "implied_probability": implied_probability,
        "expected_value": expected_value,
        "value_edge": value_edge,
        "score": score,
        "qualified": value_edge >= MINIMUM_VALUE_EDGE,
    }


def build_daily_real_candidates(
    fixtures: list[Match],
    history: list[HistoricalMatch],
) -> list[dict[str, Any]]:
    """
    Build real daily market candidates.

    Only scheduled fixtures are processed.

    Only historical matches occurring strictly before each
    fixture kickoff are used for feature generation.

    The input fixture list and its odds dictionaries are not modified.
    """
    if not isinstance(fixtures, list):
        raise TypeError("fixtures must be a list")

    if not isinstance(history, list):
        raise TypeError("history must be a list")

    for fixture in fixtures:
        _validate_fixture(fixture)

    for historical_match in history:
        _validate_history_item(historical_match)

    candidates: list[dict[str, Any]] = []

    supported_markets = get_supported_markets()

    for fixture in fixtures:
        # Process scheduled fixtures only.
        if fixture.status != "scheduled":
            continue

        # Use only historical matches before kickoff.
        prior_history = sorted(
            (
                historical_match
                for historical_match in history
                if historical_match.kickoff < fixture.kickoff
            ),
            key=lambda historical_match: historical_match.kickoff,
        )

        # No prior history means there is not enough information
        # for feature generation.
        if not prior_history:
            continue

        # IMPORTANT:
        # build_match_features expects historical_matches FIRST,
        # followed by the target fixture.
        features = build_match_features(
            prior_history,
            fixture,
        )

        predictions = predict_match_from_features(
            features
        )

        for market in supported_markets:
            selected_odds = fixture.odds.get(market)

            # No odds for this market.
            if selected_odds is None:
                continue

            # Odds must be numeric.
            if not isinstance(
                selected_odds,
                (int, float),
            ):
                continue

            selected_odds = float(selected_odds)

            # Odds must be finite and greater than 1.
            if not math.isfinite(selected_odds):
                continue

            if selected_odds <= 1.0:
                continue

            model_probability = predictions.get(market)

            # No prediction for this market.
            if model_probability is None:
                continue

            # Probability must be numeric.
            if not isinstance(
                model_probability,
                (int, float),
            ):
                continue

            model_probability = float(model_probability)

            # Probability must be finite and between 0 and 1.
            if not math.isfinite(model_probability):
                continue

            if not 0.0 <= model_probability <= 1.0:
                continue

            candidate = _build_candidate(
                fixture=fixture,
                market=market,
                model_probability=model_probability,
                selected_odds=selected_odds,
            )

            candidates.append(candidate)

    # Highest score first.
    # Secondary keys make ordering deterministic.
    candidates.sort(
        key=lambda item: (
            -float(item["score"]),
            item["kickoff"],
            item["home_team"],
            item["away_team"],
            item["market"],
        )
    )

    return candidates
