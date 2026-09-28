from __future__ import annotations

import math
from typing import Any

from tickets.builder import Selection, Ticket


# ============================================================
# PORTFOLIO CONFIGURATION
# ============================================================

TICKET_SPECS = (
    ("IRONCLAD", 40.0),
    ("BALANCED", 30.0),
    ("VOLATILITY", 20.0),
    ("BENCHMARK", 10.0),
)

LEGACY_TICKET_NAMES = {
    "IRONCLAD": "SAFE",
    "BALANCED": "BALANCED",
    "VOLATILITY": "AGGRESSIVE",
    "BENCHMARK": "VALUE",
}

MIN_SELECTIONS = 3
MAX_SELECTIONS = 6


TICKET_RULES = {
    "IRONCLAD": {
        "metric": "confidence",
        "threshold": 70.0,
    },
    "BALANCED": {
        "metric": "confidence",
        "threshold": 55.0,
    },
    "VOLATILITY": {
        "metric": "value_edge",
        "threshold": 5.0,
    },
    "BENCHMARK": {
        "metric": "value_edge",
        "threshold": 5.0,
    },
}


# ============================================================
# NUMERIC HELPERS
# ============================================================

def _safe_float(
    value: Any,
    default: float | None = None,
) -> float | None:
    """Safely convert a value to float."""

    try:
        result = float(value)
    except (TypeError, ValueError):
        return default

    if not math.isfinite(result):
        return default

    return result


# ============================================================
# CANDIDATE NORMALIZATION
# ============================================================

def _extract_selected_odds(
    candidate: dict[str, Any],
) -> float | None:
    """
    Extract odds from either the modern or legacy candidate schema.

    Supported:

        selected_odds: 2.10

    or:

        odds: 2.10

    or:

        odds: {
            "home_win": 2.10,
            ...
        }

    or:

        odds: {
            "HOME": 2.10,
            ...
        }
    """

    # --------------------------------------------------------
    # Modern schema
    # --------------------------------------------------------

    if "selected_odds" in candidate:
        value = _safe_float(
            candidate.get("selected_odds")
        )

        if value is not None:
            return value

    # --------------------------------------------------------
    # Direct legacy odds
    # --------------------------------------------------------

    raw_odds = candidate.get("odds")

    if isinstance(raw_odds, (int, float)):
        value = _safe_float(raw_odds)

        if value is not None:
            return value

    # --------------------------------------------------------
    # Odds dictionary
    # --------------------------------------------------------

    if isinstance(raw_odds, dict):

        market = str(
            candidate.get(
                "market",
                "",
            )
        )

        selection = str(
            candidate.get(
                "selection",
                "",
            )
        )

        possible_keys = [
            market,
            selection,
            market.lower(),
            selection.lower(),
        ]

        aliases = {
            "HOME": "home_win",
            "DRAW": "draw",
            "AWAY": "away_win",
            "OVER_2_5": "over_2_5",
            "UNDER_2_5": "under_2_5",
            "BTTS_YES": "btts_yes",
            "BTTS_NO": "btts_no",
        }

        for key in list(possible_keys):
            if key in aliases:
                possible_keys.append(
                    aliases[key]
                )

        for key in possible_keys:
            if not key:
                continue

            if key not in raw_odds:
                continue

            value = _safe_float(
                raw_odds.get(key)
            )

            if value is not None:
                return value

    return None


def _extract_probability(
    candidate: dict[str, Any],
) -> float | None:
    """
    Extract model probability.

    Supports:

        model_probability = 0.75

    and legacy:

        probability = 0.75

    and:

        confidence = 75
    """

    value = _safe_float(
        candidate.get("model_probability")
    )

    if value is not None:
        if 0.0 <= value <= 1.0:
            return value

        # Allow percentage representation.
        if 0.0 <= value <= 100.0:
            return value / 100.0

    value = _safe_float(
        candidate.get("probability")
    )

    if value is not None:
        if 0.0 <= value <= 1.0:
            return value

        if 0.0 <= value <= 100.0:
            return value / 100.0

    value = _safe_float(
        candidate.get("confidence")
    )

    if value is not None:
        if 0.0 <= value <= 1.0:
            return value

        if 0.0 <= value <= 100.0:
            return value / 100.0

    return None


def _extract_value_edge(
    candidate: dict[str, Any],
) -> float:
    """Extract value edge from a candidate."""

    value = _safe_float(
        candidate.get("value_edge")
    )

    if value is not None:
        return value

    # Legacy candidates may use "edge".
    value = _safe_float(
        candidate.get("edge")
    )

    if value is not None:
        return value

    # If edge is not explicitly supplied, calculate it.
    probability = _extract_probability(candidate)
    odds = _extract_selected_odds(candidate)

    if (
        probability is not None
        and odds is not None
        and odds > 1.0
    ):
        implied_probability = 1.0 / odds

        return (
            probability
            - implied_probability
        ) * 100.0

    return 0.0


def _extract_confidence(
    candidate: dict[str, Any],
) -> float:
    """Return model confidence as a percentage."""

    probability = _extract_probability(candidate)

    if probability is not None:
        return probability * 100.0

    value = _safe_float(
        candidate.get("confidence")
    )

    if value is not None:
        if value <= 1.0:
            return value * 100.0

        return value

    return 0.0


# ============================================================
# CANDIDATE VALIDATION
# ============================================================

def _validate_candidate(
    candidate: Any,
) -> None:
    """Validate one candidate while supporting old and new schemas."""

    if not isinstance(candidate, dict):
        raise TypeError(
            "each candidate must be a dictionary"
        )

    required_identity_fields = {
        "match_id",
        "home_team",
        "away_team",
    }

    missing_identity = (
        required_identity_fields
        - candidate.keys()
    )

    if missing_identity:
        raise ValueError(
            "candidate missing required fields: "
            f"{sorted(missing_identity)}"
        )

    odds = _extract_selected_odds(
        candidate
    )

    if odds is None:
        raise ValueError(
            "candidate must contain valid odds "
            "through selected_odds or odds"
        )

    if odds <= 1.0:
        raise ValueError(
            "candidate odds must be greater than 1.0"
        )

    probability = _extract_probability(
        candidate
    )

    if probability is None:
        raise ValueError(
            "candidate must contain a valid "
            "model probability"
        )

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "candidate probability must be "
            "between 0 and 1"
        )


def _validate_candidates(
    candidates: list[dict[str, Any]],
) -> None:
    """Validate all candidates."""

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================
# CANDIDATE SORTING
# ============================================================

def _candidate_score(
    candidate: dict[str, Any],
) -> float:
    """Get candidate score with legacy fallback."""

    score = _safe_float(
        candidate.get("score")
    )

    if score is not None:
        return score

    confidence = _extract_confidence(
        candidate
    )

    edge = _extract_value_edge(
        candidate
    )

    return (
        confidence * 0.7
        + max(edge, 0.0) * 0.3
    )


def _sort_candidates(
    candidates: list[dict[str, Any]],
    metric: str,
) -> list[dict[str, Any]]:
    """Sort candidates for a ticket."""

    if metric == "confidence":
        return sorted(
            candidates,
            key=lambda candidate: (
                _extract_confidence(candidate),
                _extract_value_edge(candidate),
                _candidate_score(candidate),
            ),
            reverse=True,
        )

    if metric == "value_edge":
        return sorted(
            candidates,
            key=lambda candidate: (
                _extract_value_edge(candidate),
                _extract_confidence(candidate),
                _candidate_score(candidate),
            ),
            reverse=True,
        )

    if metric == "score":
        return sorted(
            candidates,
            key=lambda candidate: (
                _candidate_score(candidate),
                _extract_confidence(candidate),
                _extract_value_edge(candidate),
            ),
            reverse=True,
        )

    raise ValueError(
        f"Unsupported portfolio metric: {metric}"
    )


# ============================================================
# ELIGIBILITY
# ============================================================

def _eligible_candidates(
    candidates: list[dict[str, Any]],
    metric: str,
    threshold: float,
) -> list[dict[str, Any]]:
    """Filter candidates according to ticket rules."""

    if metric == "confidence":
        return [
            candidate
            for candidate in candidates
            if _extract_confidence(candidate)
            >= threshold
        ]

    if metric == "value_edge":
        return [
            candidate
            for candidate in candidates
            if _extract_value_edge(candidate)
            >= threshold
        ]

    raise ValueError(
        f"Unsupported portfolio metric: {metric}"
    )


# ============================================================
# UNIQUE MATCH SELECTION
# ============================================================

def _select_unique_matches(
    candidates: list[dict[str, Any]],
    maximum: int,
    blocked_matches: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Select unique matches."""

    if blocked_matches is None:
        blocked_matches = set()

    selected = []
    used_matches = set()

    for candidate in candidates:

        match_id = str(
            candidate["match_id"]
        )

        if match_id in used_matches:
            continue

        if match_id in blocked_matches:
            continue

        selected.append(candidate)
        used_matches.add(match_id)

        if len(selected) >= maximum:
            break

    return selected


# ============================================================
# FALLBACK
# ============================================================

def _fill_ticket(
    selected: list[dict[str, Any]],
    all_candidates: list[dict[str, Any]],
    maximum: int,
    blocked_matches: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Fill a ticket without creating fake selections."""

    if blocked_matches is None:
        blocked_matches = set()

    result = list(selected)

    selected_matches = {
        str(candidate["match_id"])
        for candidate in result
    }

    for candidate in all_candidates:

        if len(result) >= maximum:
            break

        match_id = str(
            candidate["match_id"]
        )

        if match_id in selected_matches:
            continue

        if match_id in blocked_matches:
            continue

        result.append(candidate)
        selected_matches.add(match_id)

    return result


# ============================================================
# CONVERT TO SELECTION
# ============================================================

def _candidate_to_selection(
    candidate: dict[str, Any],
) -> Selection:
    """Convert candidate to Ticket Selection."""

    odds = _extract_selected_odds(
        candidate
    )

    if odds is None:
        raise ValueError(
            "Cannot create selection without odds"
        )

    market = str(
        candidate.get(
            "selection",
            candidate.get(
                "market",
                "UNKNOWN",
            ),
        )
    )

    return Selection(
        match_id=str(
            candidate["match_id"]
        ),
        match=(
            f"{candidate['home_team']} "
            f"vs "
            f"{candidate['away_team']}"
        ),
        market=market,
        odds=odds,
        confidence=_extract_confidence(
            candidate
        ),
        value_edge=_extract_value_edge(
            candidate
        ),
    )


# ============================================================
# BUILD ONE TICKET
# ============================================================

def _build_ticket(
    name: str,
    stake_percent: float,
    candidates: list[dict[str, Any]],
    blocked_matches: set[str] | None = None,
) -> Ticket | None:
    """Build one ticket."""

    if blocked_matches is None:
        blocked_matches = set()

    rules = TICKET_RULES[name]

    eligible = _eligible_candidates(
        candidates,
        rules["metric"],
        rules["threshold"],
    )

    ordered = _sort_candidates(
        eligible,
        rules["metric"],
    )

    selected = _select_unique_matches(
        ordered,
        MAX_SELECTIONS,
        blocked_matches,
    )

    # If there are not enough candidates satisfying
    # the strict rule, use the strongest remaining
    # candidates rather than manufacturing selections.
    if len(selected) < MIN_SELECTIONS:

        fallback = _sort_candidates(
            candidates,
            "score",
        )

        selected = _fill_ticket(
            selected=selected,
            all_candidates=fallback,
            maximum=MAX_SELECTIONS,
            blocked_matches=blocked_matches,
        )

    if len(selected) < MIN_SELECTIONS:
        return None

    selections = [
        _candidate_to_selection(candidate)
        for candidate in selected
    ]

    return Ticket(
        name=name,
        stake_percent=stake_percent,
        selections=selections,
    )


# ============================================================
# MODERN PORTFOLIO
# ============================================================

def build_market_portfolio(
    candidates: list[dict[str, Any]],
) -> list[Ticket]:
    """
    Build the four-ticket portfolio.

    IRONCLAD   40%
    BALANCED   30%
    VOLATILITY 20%
    BENCHMARK  10%
    """

    _validate_candidates(
        candidates
    )

    if len(candidates) < MIN_SELECTIONS:
        return []

    # Remove exact duplicate candidate records.
    unique_candidates = []
    seen = set()

    for candidate in candidates:

        key = (
            str(candidate["match_id"]),
            str(
                candidate.get(
                    "market",
                    candidate.get(
                        "selection",
                        "",
                    ),
                )
            ),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_candidates.append(candidate)

    ordered = _sort_candidates(
        unique_candidates,
        "score",
    )

    # --------------------------------------------------------
    # IRONCLAD
    # --------------------------------------------------------

    ironclad = _build_ticket(
        name="IRONCLAD",
        stake_percent=40.0,
        candidates=ordered,
    )

    if ironclad is None:
        return []

    # --------------------------------------------------------
    # BALANCED
    # --------------------------------------------------------

    balanced = _build_ticket(
        name="BALANCED",
        stake_percent=30.0,
        candidates=ordered,
    )

    if balanced is None:
        return []

    # --------------------------------------------------------
    # VOLATILITY
    # --------------------------------------------------------

    volatility = _build_ticket(
        name="VOLATILITY",
        stake_percent=20.0,
        candidates=ordered,
    )

    if volatility is None:
        return []

    # --------------------------------------------------------
    # BENCHMARK
    # --------------------------------------------------------

    ironclad_matches = {
        selection.match_id
        for selection in ironclad.selections
    }

    benchmark = _build_ticket(
        name="BENCHMARK",
        stake_percent=10.0,
        candidates=ordered,
        blocked_matches=ironclad_matches,
    )

    if benchmark is None:
        return []

    tickets = [
        ironclad,
        balanced,
        volatility,
        benchmark,
    ]

    total_stake = round(
        sum(
            float(ticket.stake_percent)
            for ticket in tickets
        ),
        6,
    )

    if total_stake != 100.0:
        raise AssertionError(
            "Portfolio stake allocation must equal 100%"
        )

    return tickets


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

def build_smart_portfolio(
    candidates: list[dict[str, Any]],
) -> list[Ticket]:
    """
    Backward-compatible portfolio API.

    Older tests expect:

        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    Internally the production system uses:

        IRONCLAD   40%
        BALANCED   30%
        VOLATILITY 20%
        BENCHMARK  10%
    """

    tickets = build_market_portfolio(
        candidates
    )

    if not tickets:
        return []

    for ticket in tickets:
        ticket.name = LEGACY_TICKET_NAMES[
            ticket.name
        ]

    return tickets


__all__ = [
    "TICKET_SPECS",
    "TICKET_RULES",
    "MIN_SELECTIONS",
    "MAX_SELECTIONS",
    "build_market_portfolio",
    "build_smart_portfolio",
]
