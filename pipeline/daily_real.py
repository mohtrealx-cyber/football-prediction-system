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
    """Validate one scheduled fixture."""
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
    Calculate the candidate score.

    70% comes from model probability.
    30% comes from positive value edge, capped at 20 percentage points.
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
    odds: float,
) -> dict[str, Any]:
    """Build one scored market candidate."""
    implied_probability = 1.0 / odds

    expected_value = (
        model_probability * odds
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
        "model_probability": model_probability,
        "odds": odds,
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
    Build market candidates from scheduled fixtures using only
    historical matches that occurred before each fixture kickoff.
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
        # Only scheduled fixtures belong in the daily candidate pipeline.
        if fixture.status != "scheduled":
            continue

        # Never use historical information from the future.
        prior_history = sorted(
            (
                historical_match
                for historical_match in history
                if historical_match.kickoff < fixture.kickoff
            ),
            key=lambda historical_match: historical_match.kickoff,
        )

        # Without any prior history, there is not enough information
        # for the feature model.
        if not prior_history:
            continue

        # IMPORTANT:
        # build_match_features expects historical_matches FIRST,
        # then the target fixture.
        features = build_match_features(
            prior_history,
            fixture,
        )

        predictions = predict_match_from_features(
            features
        )

        for market in supported_markets:
            odds = fixture.odds.get(market)

            # Missing market odds are skipped.
            if odds is None:
                continue

            # Reject invalid odds values.
            if not isinstance(odds, (int, float)):
                continue

            odds = float(odds)

            if not math.isfinite(odds):
                continue

            if odds <= 1.0:
                continue

            model_probability = predictions.get(market)

            # Missing model probabilities are skipped.
            if model_probability is None:
                continue

            if not isinstance(
                model_probability,
                (int, float),
            ):
                continue

            model_probability = float(model_probability)

            # Reject invalid model probabilities.
            if not math.isfinite(model_probability):
                continue

            if not 0.0 <= model_probability <= 1.0:
                continue

            candidate = _build_candidate(
                fixture=fixture,
                market=market,
                model_probability=model_probability,
                odds=odds,
            )

            candidates.append(candidate)

    # Highest score first.
    # Deterministic secondary ordering keeps test runs reproducible.
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
