from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ============================================================================
# PORTFOLIO CONFIGURATION
# ============================================================================

TICKET_SPECS = {
    "IRONCLAD": {
        "stake_percent": 40.0,
        "preferred_matches": 3,
        "max_matches": 4,
        "metric": "confidence",
        "minimum_confidence": 0.0,
    },
    "BALANCED": {
        "stake_percent": 20.0,
        "preferred_matches": 3,
        "max_matches": 5,
        "metric": "confidence",
        "minimum_confidence": 0.0,
    },
    "VOLATILITY": {
        "stake_percent": 10.0,
        "preferred_matches": 3,
        "max_matches": 6,
        "metric": "value_edge",
        "minimum_value_edge": 5.0,
    },
    "BENCHMARK": {
        "stake_percent": 30.0,
        "preferred_matches": 3,
        "max_matches": 6,
        "metric": "score",
        "minimum_combined_odds": 1.40,
        "maximum_combined_odds": 1.85,
    },
}


TICKET_ORDER = (
    "IRONCLAD",
    "BALANCED",
    "VOLATILITY",
    "BENCHMARK",
)


MIN_SELECTIONS = 3

# A match can appear in at most two tickets.
MAX_MATCH_USAGE = 2

# Matches already used receive a ranking penalty.
DIVERSITY_PENALTY = 6.0


# ============================================================================
# CANDIDATE VALIDATION
# ============================================================================

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


def _validate_candidate(candidate: dict) -> None:
    """Validate one portfolio candidate."""

    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")

    missing = [
        field
        for field in REQUIRED_CANDIDATE_FIELDS
        if field not in candidate
    ]

    if missing:
        raise ValueError(
            "candidate is missing required field(s): "
            + ", ".join(missing)
        )


def _validate_candidates(
    candidates: Sequence[dict],
) -> None:
    """Validate the complete candidate collection."""

    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================================
# NUMERIC HELPERS
# ============================================================================

def _safe_float(
    value: Any,
    field_name: str,
) -> float:
    """Convert a value to a finite float."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{field_name} must be a numeric value"
        ) from None

    if not math.isfinite(number):
        raise ValueError(
            f"{field_name} must be finite"
        )

    return number


# ============================================================================
# FIELD RESOLUTION
# ============================================================================

def _resolve_match_id(candidate: dict) -> str:
    """Return the candidate match ID."""

    match_id = candidate.get("match_id")

    if match_id is None:
        raise ValueError(
            "candidate match_id cannot be missing"
        )

    match_id = str(match_id).strip()

    if not match_id:
        raise ValueError(
            "candidate match_id cannot be empty"
        )

    return match_id


def _resolve_market(candidate: dict) -> str:
    """Return the candidate market."""

    market = candidate.get("market")

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market.strip()


def _resolve_candidate_odds(
    candidate: dict,
) -> float:
    """
    Resolve the odds used by Selection.

    Supported formats:

    1. Explicit selected odds:
        "selected_odds": 1.80

    2. Numeric odds:
        "odds": 1.80

    3. Full odds dictionary:
        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
        }
    """

    if "selected_odds" in candidate:
        selected_odds = candidate.get(
            "selected_odds"
        )

        if selected_odds is not None:
            odds = _safe_float(
                selected_odds,
                "selected_odds",
            )

            if odds <= 1.0:
                raise ValueError(
                    "selected_odds must be greater than 1.0"
                )

            return odds

    raw_odds = candidate.get("odds")

    # Numeric odds.
    if not isinstance(raw_odds, dict):
        odds = _safe_float(
            raw_odds,
            "odds",
        )

        if odds <= 1.0:
            raise ValueError(
                "odds must be greater than 1.0"
            )

        return odds

    # Dictionary odds.
    market = _resolve_market(candidate)

    if market in raw_odds:
        odds = _safe_float(
            raw_odds[market],
            "odds",
        )

        if odds <= 1.0:
            raise ValueError(
                "odds must be greater than 1.0"
            )

        return odds

    market_aliases = {
        "home_win": (
            "HOME",
            "1",
            "home",
        ),
        "draw": (
            "DRAW",
            "X",
            "draw",
        ),
        "away_win": (
            "AWAY",
            "2",
            "away",
        ),
        "over_2_5": (
            "OVER_2_5",
            "OVER 2.5",
            "OVER",
        ),
        "under_2_5": (
            "UNDER_2_5",
            "UNDER 2.5",
            "UNDER",
        ),
        "btts_yes": (
            "BTTS_YES",
            "BTTS YES",
            "YES",
        ),
        "btts_no": (
            "BTTS_NO",
            "BTTS NO",
            "NO",
        ),
    }

    for alias in market_aliases.get(
        market,
        (),
    ):
        if alias in raw_odds:
            odds = _safe_float(
                raw_odds[alias],
                "odds",
            )

            if odds <= 1.0:
                raise ValueError(
                    "odds must be greater than 1.0"
                )

            return odds

    raise ValueError(
        f"no odds found for market: {market}"
    )


def _resolve_confidence(
    candidate: dict,
) -> float:
    """
    Resolve confidence for Selection.

    Priority:

    1. explicit confidence
    2. model_probability * 100
    3. score
    """

    if "confidence" in candidate:
        confidence = _safe_float(
            candidate["confidence"],
            "confidence",
        )

    elif "model_probability" in candidate:
        probability = _safe_float(
            candidate["model_probability"],
            "model_probability",
        )

        confidence = probability * 100.0

    else:
        confidence = _safe_float(
            candidate["score"],
            "score",
        )

    confidence = max(
        0.0,
        min(100.0, confidence),
    )

    return confidence


def _resolve_value_edge(
    candidate: dict,
) -> float:
    """Resolve and validate value edge."""

    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        raise ValueError(
            "value_edge cannot be negative"
        )

    return value_edge


def _resolve_match(
    candidate: dict,
) -> str:
    """Resolve the human-readable match string."""

    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if (
        home_team is not None
        and away_team is not None
    ):
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    return _resolve_match_id(candidate)


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(
    candidate: dict,
) -> Selection:
    """Convert a candidate into a Selection."""

    _validate_candidate(candidate)

    selection = Selection(
        match_id=_resolve_match_id(candidate),
        match=_resolve_match(candidate),
        market=_resolve_market(candidate),
        odds=_resolve_candidate_odds(candidate),
        confidence=_resolve_confidence(candidate),
        value_edge=_resolve_value_edge(candidate),
    )

    selection.validate()

    return selection


# ============================================================================
# RANKING
# ============================================================================

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
    """Return the metric used for ticket ranking."""

    if metric == "score":
        return _safe_float(
            candidate["score"],
            "score",
        )

    if metric == "confidence":
        return _resolve_confidence(candidate)

    if metric == "value_edge":
        return _safe_float(
            candidate["value_edge"],
            "value_edge",
        )

    raise ValueError(
        f"unsupported ranking metric: {metric}"
    )


def _passes_ticket_filter(
    candidate: dict,
    ticket_name: str,
) -> bool:
    """Check whether a candidate satisfies ticket-specific requirements."""

    spec = TICKET_SPECS[ticket_name]

    if spec["metric"] == "confidence":
        confidence = _resolve_confidence(candidate)

        return (
            confidence
            >= spec["minimum_confidence"]
        )

    if spec["metric"] == "value_edge":
        value_edge = _resolve_value_edge(candidate)

        return (
            value_edge
            >= spec["minimum_value_edge"]
        )

    return True


def _rank_candidates_for_ticket(
    candidates: Sequence[dict],
    ticket_name: str,
    usage_counts: Dict[str, int] | None = None,
    excluded_match_ids: set[str] | None = None,
) -> List[dict]:
    """
    Rank candidates for a ticket.

    Previously used matches receive a diversity penalty.

    Matches listed in excluded_match_ids are completely excluded.
    """

    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    if usage_counts is None:
        usage_counts = {}

    if excluded_match_ids is None:
        excluded_match_ids = set()

    spec = TICKET_SPECS[ticket_name]
    metric = spec["metric"]

    ranked = []

    for candidate in candidates:
        _validate_candidate(candidate)

        if not _passes_ticket_filter(
            candidate,
            ticket_name,
        ):
            continue

        match_id = _resolve_match_id(candidate)

        if match_id in excluded_match_ids:
            continue

        usage_count = usage_counts.get(
            match_id,
            0,
        )

        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_metric = _candidate_metric(
            candidate,
            metric,
        )

        adjusted_score = (
            base_metric
            - usage_count * DIVERSITY_PENALTY
        )

        ranked.append(
            {
                "adjusted_score": adjusted_score,
                "base_metric": base_metric,
                "candidate": candidate,
            }
        )

    ranked.sort(
        key=lambda item: (
            item["adjusted_score"],
            item["base_metric"],
        ),
        reverse=True,
    )

    return [
        item["candidate"]
        for item in ranked
    ]


# ============================================================================
# TICKET ODDS
# ============================================================================

def _calculate_combined_odds(
    candidates: Sequence[dict],
) -> float:
    """Calculate combined decimal odds."""

    combined = 1.0

    for candidate in candidates:
        odds = _resolve_candidate_odds(candidate)
        combined *= odds

    return round(combined, 4)


def _benchmark_odds_valid(
    candidates: Sequence[dict],
) -> bool:
    """Check the BENCHMARK combined-odds range."""

    if len(candidates) < MIN_SELECTIONS:
        return False

    combined_odds = _calculate_combined_odds(
        candidates
    )

    return (
        combined_odds
        >= TICKET_SPECS["BENCHMARK"][
            "minimum_combined_odds"
        ]
        and combined_odds
        <= TICKET_SPECS["BENCHMARK"][
            "maximum_combined_odds"
        ]
    )


# ============================================================================
# SINGLE TICKET BUILDING
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    Never fabricates weak selections merely to reach
    the minimum number.
    """

    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    spec = TICKET_SPECS[ticket_name]

    selections: List[Selection] = []
    seen_match_ids = set()

    for candidate in candidates:
        _validate_candidate(candidate)

        match_id = _resolve_match_id(candidate)

        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)
        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


def _build_benchmark_ticket(
    candidates: Sequence[dict],
    usage_counts: Dict[str, int],
    excluded_match_ids: set[str],
) -> Ticket | None:
    """
    Build BENCHMARK while enforcing its 1.40-1.85
    combined-odds target.

    We try the strongest valid combinations first.
    """

    ranked = _rank_candidates_for_ticket(
        candidates=candidates,
        ticket_name="BENCHMARK",
        usage_counts=usage_counts,
        excluded_match_ids=excluded_match_ids,
    )

    if len(ranked) < MIN_SELECTIONS:
        return None

    max_matches = TICKET_SPECS[
        "BENCHMARK"
    ]["max_matches"]

    # Try progressively larger tickets.
    for size in range(
        MIN_SELECTIONS,
        max_matches + 1,
    ):
        if len(ranked) < size:
            break

        # First try the strongest consecutive group.
        for start in range(
            0,
            len(ranked) - size + 1,
        ):
            group = ranked[
                start:start + size
            ]

            unique_ids = {
                _resolve_match_id(candidate)
                for candidate in group
            }

            if len(unique_ids) != size:
                continue

            if not _benchmark_odds_valid(
                group
            ):
                continue

            ticket = _build_ticket(
                "BENCHMARK",
                group,
            )

            if ticket is not None:
                return ticket

    return None


# ============================================================================
# MAIN PORTFOLIO BUILDER
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the four-ticket portfolio.

    Portfolio allocation:

        IRONCLAD   40%
        BALANCED   20%
        VOLATILITY 10%
        BENCHMARK  30%

    Rules:

        - minimum 3 selections per created ticket
        - no duplicate match within a ticket
        - maximum two-ticket match reuse
        - IRONCLAD and BENCHMARK cannot share matches
        - BENCHMARK targets combined odds 1.40-1.85
        - weak tickets are not fabricated
        - input candidates are not mutated
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    _validate_candidates(candidates)

    # Never mutate caller data.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    usage_counts: Dict[str, int] = {}

    # Matches used by IRONCLAD are deliberately
    # unavailable to BENCHMARK.
    ironclad_match_ids: set[str] = set()

    # ------------------------------------------------------------------
    # IRONCLAD
    # ------------------------------------------------------------------

    ranked_ironclad = _rank_candidates_for_ticket(
        candidates=available,
        ticket_name="IRONCLAD",
        usage_counts=usage_counts,
    )

    ironclad = _build_ticket(
        "IRONCLAD",
        ranked_ironclad,
    )

    if ironclad is not None:
        portfolio.append(ironclad)

        for selection in ironclad.selections:
            match_id = selection.match_id

            ironclad_match_ids.add(
                match_id
            )

            usage_counts[match_id] = (
                usage_counts.get(
                    match_id,
                    0,
                )
                + 1
            )

    # ------------------------------------------------------------------
    # BALANCED
    # ------------------------------------------------------------------

    ranked_balanced = _rank_candidates_for_ticket(
        candidates=available,
        ticket_name="BALANCED",
        usage_counts=usage_counts,
    )

    balanced = _build_ticket(
        "BALANCED",
        ranked_balanced,
    )

    if balanced is not None:
        portfolio.append(balanced)

        for selection in balanced.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(
                    match_id,
                    0,
                )
                + 1
            )

    # ------------------------------------------------------------------
    # VOLATILITY
    # ------------------------------------------------------------------

    ranked_volatility = _rank_candidates_for_ticket(
        candidates=available,
        ticket_name="VOLATILITY",
        usage_counts=usage_counts,
    )

    volatility = _build_ticket(
        "VOLATILITY",
        ranked_volatility,
    )

    if volatility is not None:
        portfolio.append(volatility)

        for selection in volatility.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(
                    match_id,
                    0,
                )
                + 1
            )

    # ------------------------------------------------------------------
    # BENCHMARK
    # ------------------------------------------------------------------

    benchmark = _build_benchmark_ticket(
        candidates=available,
        usage_counts=usage_counts,
        excluded_match_ids=ironclad_match_ids,
    )

    if benchmark is not None:
        portfolio.append(benchmark)

        for selection in benchmark.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(
                    match_id,
                    0,
                )
                + 1
            )

    # ------------------------------------------------------------------
    # FINAL VALIDATION
    # ------------------------------------------------------------------

    if len(portfolio) == 4:
        total_stake = round(
            sum(
                ticket.stake_percent
                for ticket in portfolio
            ),
            6,
        )

        if abs(total_stake - 100.0) > 1e-6:
            raise AssertionError(
                "Four-ticket portfolio must allocate "
                "exactly 100% of stake"
            )

        names = [
            ticket.name
            for ticket in portfolio
        ]

        expected_names = list(
            TICKET_ORDER
        )

        if names != expected_names:
            raise AssertionError(
                "Ticket order is incorrect: "
                f"{names}"
            )

    return portfolio


# ============================================================================
# PUBLIC COMPATIBILITY FUNCTIONS
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """Legacy/public portfolio entry point."""

    return build_market_portfolio(
        candidates
    )


def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """Compatibility alias."""

    return build_market_portfolio(
        candidates
    )
