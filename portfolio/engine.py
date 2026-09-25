from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ============================================================================
# PORTFOLIO CONFIGURATION
# ============================================================================

TICKET_SPECS = {
    "SAFE": {
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
    "AGGRESSIVE": {
        "stake_percent": 20.0,
        "preferred_matches": 5,
        "max_matches": 6,
        "metric": "score",
    },
    "VALUE": {
        "stake_percent": 10.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "value_edge",
    },
}

TICKET_ORDER = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)

MIN_SELECTIONS = 3
MAX_MATCH_USAGE = 2
DIVERSITY_PENALTY = 6.0


# ============================================================================
# REQUIRED CANDIDATE INTERFACE
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
    Validate a single portfolio candidate.

    Required fields are deliberately checked here so malformed candidates
    cannot silently pass through fallback logic.
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


def _validate_candidates(candidates: Sequence[dict]) -> None:
    """
    Validate the complete candidate collection.
    """
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


def _safe_float(value: Any, field_name: str) -> float:
    """
    Convert a value to finite float.
    """
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
    """
    Resolve the unique match ID.
    """
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
    """
    Resolve the market name.
    """
    market = candidate.get("market")

    if not isinstance(market, str):
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    market = market.strip()

    if not market:
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market


def _resolve_selection(candidate: dict) -> str:
    """
    Resolve the actual selection string.

    Examples:
        HOME
        DRAW
        AWAY
        OVER_2_5
        UNDER_2_5
        BTTS_YES
        BTTS_NO
        1X
        X2
        12
    """
    selection = candidate.get("selection")

    if not isinstance(selection, str):
        raise ValueError(
            "candidate selection must be a non-empty string"
        )

    selection = selection.strip()

    if not selection:
        raise ValueError(
            "candidate selection must be a non-empty string"
        )

    return selection


def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the actual odds for the candidate.

    Supported formats:

        "odds": 1.80

    or:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    When selected_odds exists, it is preferred.
    """
    # ------------------------------------------------------------
    # 1. Explicit selected_odds
    # ------------------------------------------------------------
    if "selected_odds" in candidate:
        selected_odds = candidate["selected_odds"]

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

    # ------------------------------------------------------------
    # 2. Raw odds
    # ------------------------------------------------------------
    raw_odds = candidate.get("odds")

    # Numeric odds
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

    # ------------------------------------------------------------
    # 3. Dictionary odds
    # ------------------------------------------------------------
    market = _resolve_market(candidate)
    selection = _resolve_selection(candidate)

    # Direct market key
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

    # ------------------------------------------------------------
    # Market aliases
    # ------------------------------------------------------------
    aliases = {
        "home_win": (
            "HOME",
            "1",
        ),
        "draw": (
            "DRAW",
            "X",
        ),
        "away_win": (
            "AWAY",
            "2",
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
            "BTTS",
        ),
        "btts_no": (
            "BTTS_NO",
            "BTTS NO",
        ),
    }

    for alias in aliases.get(market, ()):
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

    # ------------------------------------------------------------
    # Selection key fallback
    # ------------------------------------------------------------
    if selection in raw_odds:
        odds = _safe_float(
            raw_odds[selection],
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


def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve Selection.confidence.

    Priority:
        1. explicit confidence
        2. model_probability * 100
        3. score

    The tickets/builder.py Selection interface requires 0–100.
    """
    if "confidence" in candidate:
        confidence = _safe_float(
            candidate["confidence"],
            "confidence",
        )

    elif "model_probability" in candidate:
        confidence = (
            _safe_float(
                candidate["model_probability"],
                "model_probability",
            )
            * 100.0
        )

    else:
        confidence = _safe_float(
            candidate["score"],
            "score",
        )

    # Keep within Selection's required range.
    return max(
        0.0,
        min(100.0, confidence),
    )


def _resolve_value_edge(candidate: dict) -> float:
    """
    Resolve the candidate value edge.
    """
    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        value_edge = 0.0

    return value_edge


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable match string required by Selection.

    Priority:
        1. candidate["match"]
        2. home_team + away_team
        3. match_id

    We intentionally do not require home_team/away_team because some older
    portfolio candidates use the direct "match" field.
    """
    # Direct match
    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    # Home + away
    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    # Final fallback
    return _resolve_match_id(candidate)


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a candidate dictionary into the exact Selection interface
    defined in tickets/builder.py.
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
        odds=odds,
        confidence=confidence,
        value_edge=value_edge,
    )

    # Use the validation already defined in tickets/builder.py.
    selection.validate()

    return selection


# ============================================================================
# RANKING
# ============================================================================

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
    """
    Get the ranking metric for a candidate.
    """
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

    A diversity penalty is applied when a match has already been used in
    earlier tickets.

    MAX_MATCH_USAGE = 2 means the same match cannot appear more than twice
    across the complete four-ticket portfolio.
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

        # Do not allow more than two portfolio appearances.
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
# TICKET BUILDING
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    Returns None when fewer than three valid selections are available.
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

        # Never duplicate the same match within one ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)
        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Never force a weak/incomplete ticket.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ============================================================================
# MAIN SMART PORTFOLIO ENGINE
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the complete four-ticket smart portfolio.

    Ticket allocation:
        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    Rules:
        - minimum 3 selections per built ticket
        - ticket-specific maximums
        - no duplicate match inside a ticket
        - same match may appear in at most 2 tickets
        - no forced weak ticket
        - candidates are not mutated
    """
    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    # Strict upfront validation.
    _validate_candidates(candidates)

    # Copy candidates so the caller's data is not modified.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Match usage across the complete portfolio.
    usage_counts: Dict[str, int] = {}

    # ------------------------------------------------------------
    # Build tickets in priority order.
    # ------------------------------------------------------------
    for ticket_name in TICKET_ORDER:

        ranked_candidates = _rank_candidates_for_ticket(
            available,
            ticket_name,
            usage_counts,
        )

        ticket = _build_ticket(
            ticket_name,
            ranked_candidates,
        )

        # Do not force an incomplete ticket.
        if ticket is None:
            continue

        portfolio.append(ticket)

        # Update portfolio-wide match usage.
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
# MARKET PORTFOLIO NAME
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Current market-portfolio entry point.

    Kept as a separate public function because newer modules use this name.
    It delegates to the original smart portfolio implementation.
    """
    return build_smart_portfolio(candidates)
