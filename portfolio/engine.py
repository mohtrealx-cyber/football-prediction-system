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
        "metric": "score",
    },
    "BALANCED": {
        "stake_percent": 30.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "score",
    },
    "VOLATILITY": {
        "stake_percent": 20.0,
        "preferred_matches": 5,
        "max_matches": 6,
        "metric": "score",
    },
    "BENCHMARK": {
        "stake_percent": 10.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "value_edge",
    },
}


TICKET_ORDER = (
    "IRONCLAD",
    "BALANCED",
    "VOLATILITY",
    "BENCHMARK",
)


MIN_SELECTIONS = 3
MAX_MATCH_USAGE = 2
DIVERSITY_PENALTY = 6.0


# ============================================================================
# REQUIRED CANDIDATE FIELDS
# ============================================================================

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "selection",
    "odds",
    "score",
    "value_edge",
)


# ============================================================================
# VALIDATION
# ============================================================================

def _validate_candidate(candidate: dict) -> None:
    """
    Validate one candidate.

    Core fields are mandatory.

    Compatibility:
    - Older candidates may use numeric odds directly.
    - Newer candidates may contain an odds dictionary plus selected_odds.
    """

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

    # Basic required-value validation.
    match_id = candidate.get("match_id")

    if match_id is None or not str(match_id).strip():
        raise ValueError("candidate match_id cannot be empty")

    market = candidate.get("market")

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    selection = candidate.get("selection")

    if not isinstance(selection, str) or not selection.strip():
        raise ValueError(
            "candidate selection must be a non-empty string"
        )

    # Important compatibility rule:
    #
    # If odds is a dictionary, selected_odds must exist because the
    # portfolio needs to know which actual price belongs to the selected
    # market.
    #
    # If odds is already numeric, selected_odds is optional because odds
    # itself is the selected price.
    odds = candidate.get("odds")

    if isinstance(odds, dict):
        if "selected_odds" not in candidate:
            raise ValueError(
                "candidate is missing required field: selected_odds"
            )

        if candidate.get("selected_odds") is None:
            raise ValueError(
                "selected_odds cannot be missing or None"
            )

    # Validate score and value edge as numeric values.
    _safe_float(candidate.get("score"), "score")
    _safe_float(candidate.get("value_edge"), "value_edge")


def _validate_candidates(candidates: Sequence[dict]) -> None:
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================================
# NUMERIC HELPERS
# ============================================================================

def _safe_float(value: Any, field_name: str) -> float:
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
# CANDIDATE FIELD RESOLUTION
# ============================================================================

def _resolve_match_id(candidate: dict) -> str:
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
    market = candidate.get("market")

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market.strip()


def _resolve_selection(candidate: dict) -> str:
    selection = candidate.get("selection")

    if not isinstance(selection, str) or not selection.strip():
        raise ValueError(
            "candidate selection must be a non-empty string"
        )

    return selection.strip()


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable fixture name.

    Supported forms:

        match
        home_team + away_team
        match_id
    """

    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    return _resolve_match_id(candidate)


# ============================================================================
# ODDS RESOLUTION
# ============================================================================

def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the actual odds for the selected candidate.

    Supported:

        "odds": 1.80

    or:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50
        },
        "selected_odds": 1.80

    selected_odds takes priority when supplied.
    """

    # ------------------------------------------------------------
    # Explicit selected odds always take priority.
    # ------------------------------------------------------------

    if "selected_odds" in candidate:
        selected_odds = candidate.get("selected_odds")

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

    # ------------------------------------------------------------
    # Odds dictionary
    # ------------------------------------------------------------

    if isinstance(raw_odds, dict):
        market = _resolve_market(candidate)

        # Direct market lookup.
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

        # Compatibility aliases.
        aliases = {
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
            "over_1_5": (
                "OVER_1_5",
                "OVER 1.5",
                "over_1_5",
            ),
            "under_1_5": (
                "UNDER_1_5",
                "UNDER 1.5",
                "under_1_5",
            ),
            "over_2_5": (
                "OVER_2_5",
                "OVER 2.5",
                "over_2_5",
            ),
            "under_2_5": (
                "UNDER_2_5",
                "UNDER 2.5",
                "under_2_5",
            ),
            "btts_yes": (
                "BTTS_YES",
                "BTTS YES",
                "YES",
                "btts_yes",
            ),
            "btts_no": (
                "BTTS_NO",
                "BTTS NO",
                "NO",
                "btts_no",
            ),
        }

        found_value = None

        for alias in aliases.get(market, ()):
            if alias in raw_odds:
                found_value = raw_odds[alias]
                break

        # Selection lookup.
        if found_value is None:
            selection = candidate.get("selection")

            if selection in raw_odds:
                found_value = raw_odds[selection]

        if found_value is None:
            raise ValueError(
                f"no odds found for market: {market}"
            )

        odds = _safe_float(
            found_value,
            "odds",
        )

    # ------------------------------------------------------------
    # Numeric odds
    # ------------------------------------------------------------

    else:
        odds = _safe_float(
            raw_odds,
            "odds",
        )

    if odds <= 1.0:
        raise ValueError(
            "odds must be greater than 1.0"
        )

    return odds


# ============================================================================
# CONFIDENCE RESOLUTION
# ============================================================================

def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve Selection.confidence.

    Priority:

        1. confidence
        2. model_probability * 100
        3. score
    """

    if "confidence" in candidate:
        value = _safe_float(
            candidate["confidence"],
            "confidence",
        )

    elif "model_probability" in candidate:
        value = (
            _safe_float(
                candidate["model_probability"],
                "model_probability",
            )
            * 100.0
        )

    else:
        value = _safe_float(
            candidate["score"],
            "score",
        )

    # Keep confidence within the Selection contract.
    return max(
        0.0,
        min(100.0, value),
    )


# ============================================================================
# VALUE EDGE
# ============================================================================

def _resolve_value_edge(candidate: dict) -> float:
    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        value_edge = 0.0

    return value_edge


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a validated candidate into the project's Selection object.
    """

    _validate_candidate(candidate)

    match_id = _resolve_match_id(candidate)
    match = _resolve_match(candidate)
    market = _resolve_market(candidate)
    odds = _resolve_candidate_odds(candidate)
    confidence = _resolve_confidence(candidate)
    value_edge = _resolve_value_edge(candidate)

    selection = Selection(
        match_id=match_id,
        match=match,
        market=market,
        selected_odds=odds,
        confidence=confidence,
        value_edge=value_edge,
    )

    # Respect the existing Selection validation contract.
    selection.validate()

    return selection


# ============================================================================
# RANKING
# ============================================================================

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:

    if metric == "score":
        return _safe_float(
            candidate["score"],
            "score",
        )

    if metric == "value_edge":
        return _safe_float(
            candidate["value_edge"],
            "value_edge",
        )

    raise ValueError(
        f"unsupported ranking metric: {metric}"
    )


def _rank_candidates_for_ticket(
    candidates: Sequence[dict],
    ticket_name: str,
    usage_counts: Dict[str, int] | None = None,
) -> List[dict]:
    """
    Rank candidates for one ticket.

    Previously used matches receive a diversity penalty.

    A match cannot appear more than MAX_MATCH_USAGE times.
    """

    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    if usage_counts is None:
        usage_counts = {}

    spec = TICKET_SPECS[ticket_name]

    metric = spec["metric"]

    ranked = []

    for candidate in candidates:

        _validate_candidate(candidate)

        match_id = _resolve_match_id(candidate)

        usage_count = usage_counts.get(
            match_id,
            0,
        )

        # Do not use a match more than twice.
        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_metric = _candidate_metric(
            candidate,
            metric,
        )

        adjusted_score = (
            base_metric
            - (
                usage_count
                * DIVERSITY_PENALTY
            )
        )

        ranked.append(
            (
                adjusted_score,
                base_metric,
                candidate,
            )
        )

    # Highest adjusted score first.
    ranked.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return [
        candidate
        for _, _, candidate in ranked
    ]


# ============================================================================
# SINGLE TICKET BUILDER
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    A ticket requires at least three unique matches.
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

        # Never duplicate a match inside a single ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)

        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Never fabricate a ticket.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ============================================================================
# MAIN PORTFOLIO BUILDER
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the four-ticket portfolio.

    Strategy:

        IRONCLAD    40%
        BALANCED    30%
        VOLATILITY  20%
        BENCHMARK   10%

    Rules:

        - minimum 3 selections per ticket
        - ticket-specific maximum selections
        - no duplicate match inside a ticket
        - maximum two-ticket match reuse
        - diversity penalty for reused matches
        - no fabricated weak tickets
        - caller input is never mutated
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    # IMPORTANT:
    # Validate EVERY candidate before ranking/building.
    _validate_candidates(candidates)

    # Never mutate caller data.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Tracks cross-ticket match usage.
    usage_counts: Dict[str, int] = {}

    # Build in the required order.
    for ticket_name in TICKET_ORDER:

        ranked_candidates = (
            _rank_candidates_for_ticket(
                available,
                ticket_name,
                usage_counts,
            )
        )

        ticket = _build_ticket(
            ticket_name,
            ranked_candidates,
        )

        # Do not force a ticket if there aren't enough valid matches.
        if ticket is None:
            continue

        portfolio.append(ticket)

        # Update cross-ticket usage.
        for selection in ticket.selections:

            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(
                    match_id,
                    0,
                )
                + 1
            )

    return portfolio


# ============================================================================
# PUBLIC COMPATIBILITY ENTRY POINTS
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Primary public portfolio entry point.

    Kept for backward compatibility with existing modules/tests.

    Returns tickets in this order:

        IRONCLAD
        BALANCED
        VOLATILITY
        BENCHMARK
    """

    return build_market_portfolio(
        candidates
    )


def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Backward-compatible alias.
    """

    return build_market_portfolio(
        candidates
    )
