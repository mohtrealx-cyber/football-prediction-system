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

        # Preserve the complete odds dictionary.
        "odds": dict(fixture.odds),

        # Odds for this specific market.
        "selected_odds": selected_odds,

        "model_probability": model_probability,
        "implied_probability": implied_probability,
        "expected_value": expected_value,
        "value_edge": value_edge,
        "score": score,

        # Existing qualification rule is unchanged.
        "qualified": value_edge >= MINIMUM_VALUE_EDGE,
    }


def _print_fixture_diagnostics(
    fixture: Match,
    prior_history: list[HistoricalMatch],
    features: dict,
    predictions: dict,
    fixture_candidates: list[dict[str, Any]],
) -> None:
    """
    Print diagnostic information for one fixture.

    This function does not modify prediction logic.
    It only exposes the values already calculated by the model.
    """

    print()
    print("-" * 78)
    print("CANDIDATE DIAGNOSTICS")
    print("-" * 78)

    print(
        f"Match:   "
        f"{fixture.home_team} vs {fixture.away_team}"
    )

    print(
        f"League:  {fixture.league}"
    )

    print(
        f"Kickoff: {fixture.kickoff}"
    )

    print(
        f"History available before kickoff: "
        f"{len(prior_history)} matches"
    )

    expected_home = predictions.get(
        "expected_home_goals"
    )

    expected_away = predictions.get(
        "expected_away_goals"
    )

    print()
    print("MODEL EXPECTED GOALS")
    print(
        f"  Home: {expected_home:.4f}"
        if isinstance(expected_home, (int, float))
        else "  Home: unavailable"
    )

    print(
        f"  Away: {expected_away:.4f}"
        if isinstance(expected_away, (int, float))
        else "  Away: unavailable"
    )

    print()
    print("MARKET ANALYSIS")

    if not fixture_candidates:
        print("  No usable market candidates.")
        return

    for candidate in fixture_candidates:
        probability = candidate["model_probability"]
        implied = candidate["implied_probability"]
        odds = candidate["selected_odds"]
        edge = candidate["value_edge"]
        score = candidate["score"]
        qualified = candidate["qualified"]

        status = (
            "QUALIFIED"
            if qualified
            else "REJECTED"
        )

        print(
            f"  {candidate['selection']:<10}"
            f" odds={odds:.2f}"
            f" | model={probability * 100:.2f}%"
            f" | implied={implied * 100:.2f}%"
            f" | edge={edge:+.2f}%"
            f" | score={score:.2f}"
            f" | {status}"
        )


def build_daily_real_candidates(
    fixtures: list[Match],
    history: list[HistoricalMatch],
) -> list[dict[str, Any]]:
    """
    Build real daily market candidates.

    Only scheduled fixtures are processed.

    Only historical matches occurring strictly before each
    fixture kickoff are used for feature generation.

    The input fixture list and odds dictionaries are not modified.

    Diagnostic output is included so that rejected selections
    can be inspected without changing the qualification rules.
    """

    if not isinstance(fixtures, list):
        raise TypeError(
            "fixtures must be a list"
        )

    if not isinstance(history, list):
        raise TypeError(
            "history must be a list"
        )

    for fixture in fixtures:
        _validate_fixture(fixture)

    for historical_match in history:
        _validate_history_item(historical_match)

    candidates: list[dict[str, Any]] = []

    supported_markets = get_supported_markets()

    print()
    print("=" * 78)
    print("DAILY CANDIDATE ANALYSIS")
    print("=" * 78)

    scheduled_count = 0
    skipped_no_history = 0
    skipped_no_odds = 0
    skipped_invalid_odds = 0
    skipped_invalid_probability = 0

    for fixture in fixtures:

        # -----------------------------------------------------
        # ONLY SCHEDULED FIXTURES
        # -----------------------------------------------------
        if fixture.status != "scheduled":
            continue

        scheduled_count += 1

        # -----------------------------------------------------
        # HISTORICAL DATA BEFORE KICKOFF
        # -----------------------------------------------------
        prior_history = sorted(
            (
                historical_match
                for historical_match in history
                if historical_match.kickoff < fixture.kickoff
            ),
            key=lambda historical_match: historical_match.kickoff,
        )

        if not prior_history:
            skipped_no_history += 1

            print()
            print("-" * 78)
            print(
                f"SKIPPED: "
                f"{fixture.home_team} vs {fixture.away_team}"
            )
            print(
                "Reason: no historical matches before kickoff."
            )

            continue

        # -----------------------------------------------------
        # FEATURE ENGINEERING
        # -----------------------------------------------------
        features = build_match_features(
            prior_history,
            fixture,
        )

        # -----------------------------------------------------
        # MODEL PREDICTION
        # -----------------------------------------------------
        predictions = predict_match_from_features(
            features
        )

        fixture_candidates: list[
            dict[str, Any]
        ] = []

        # -----------------------------------------------------
        # MARKET ANALYSIS
        # -----------------------------------------------------
        for market in supported_markets:

            selected_odds = fixture.odds.get(
                market
            )

            # No odds for this market.
            if selected_odds is None:
                skipped_no_odds += 1
                continue

            # Odds must be numeric.
            if not isinstance(
                selected_odds,
                (int, float),
            ):
                skipped_invalid_odds += 1
                continue

            selected_odds = float(
                selected_odds
            )

            # Odds must be finite and > 1.
            if not math.isfinite(
                selected_odds
            ):
                skipped_invalid_odds += 1
                continue

            if selected_odds <= 1.0:
                skipped_invalid_odds += 1
                continue

            model_probability = predictions.get(
                market
            )

            # No model probability.
            if model_probability is None:
                skipped_invalid_probability += 1
                continue

            # Probability must be numeric.
            if not isinstance(
                model_probability,
                (int, float),
            ):
                skipped_invalid_probability += 1
                continue

            model_probability = float(
                model_probability
            )

            # Probability must be finite.
            if not math.isfinite(
                model_probability
            ):
                skipped_invalid_probability += 1
                continue

            # Probability must be between 0 and 1.
            if not 0.0 <= model_probability <= 1.0:
                skipped_invalid_probability += 1
                continue

            candidate = _build_candidate(
                fixture=fixture,
                market=market,
                model_probability=model_probability,
                selected_odds=selected_odds,
            )

            fixture_candidates.append(
                candidate
            )

            candidates.append(
                candidate
            )

        # -----------------------------------------------------
        # DIAGNOSTIC REPORT FOR THIS FIXTURE
        # -----------------------------------------------------
        _print_fixture_diagnostics(
            fixture=fixture,
            prior_history=prior_history,
            features=features,
            predictions=predictions,
            fixture_candidates=fixture_candidates,
        )

    # ---------------------------------------------------------
    # SORT ALL CANDIDATES
    # ---------------------------------------------------------
    candidates.sort(
        key=lambda item: (
            -float(item["score"]),
            item["kickoff"],
            item["home_team"],
            item["away_team"],
            item["market"],
        )
    )

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------
    qualified_count = sum(
        1
        for candidate in candidates
        if candidate["qualified"]
    )

    rejected_count = sum(
        1
        for candidate in candidates
        if not candidate["qualified"]
    )

    print()
    print("=" * 78)
    print("DAILY CANDIDATE SUMMARY")
    print("=" * 78)

    print(
        f"Scheduled fixtures processed: "
        f"{scheduled_count}"
    )

    print(
        f"Total market candidates: "
        f"{len(candidates)}"
    )

    print(
        f"Qualified candidates: "
        f"{qualified_count}"
    )

    print(
        f"Rejected candidates: "
        f"{rejected_count}"
    )

    print(
        f"Minimum value edge: "
        f"{MINIMUM_VALUE_EDGE:.2f}%"
    )

    print(
        f"Candidates skipped - no history: "
        f"{skipped_no_history}"
    )

    print(
        f"Markets skipped - no odds: "
        f"{skipped_no_odds}"
    )

    print(
        f"Markets skipped - invalid odds: "
        f"{skipped_invalid_odds}"
    )

    print(
        f"Markets skipped - invalid probability: "
        f"{skipped_invalid_probability}"
    )

    # ---------------------------------------------------------
    # TOP CANDIDATES
    # ---------------------------------------------------------
    print()
    print("TOP CANDIDATES")
    print("-" * 78)

    if not candidates:
        print("No candidates generated.")

    else:
        for index, candidate in enumerate(
            candidates[:20],
            start=1,
        ):
            status = (
                "QUALIFIED"
                if candidate["qualified"]
                else "REJECTED"
            )

            print(
                f"{index:02d}. "
                f"{candidate['home_team']} vs "
                f"{candidate['away_team']} | "
                f"{candidate['selection']} | "
                f"odds={candidate['selected_odds']:.2f} | "
                f"model={candidate['model_probability'] * 100:.2f}% | "
                f"edge={candidate['value_edge']:+.2f}% | "
                f"score={candidate['score']:.2f} | "
                f"{status}"
            )

    print("=" * 78)

    return candidates
