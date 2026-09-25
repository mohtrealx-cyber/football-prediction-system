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
# CANDIDATE INTERFACE
# ============================================================================
#
# These are the fields the portfolio layer genuinely needs.
#
# "selection" is NOT required here because older candidates do not contain
# that field. It can be derived from "market".
#
# "home_team" and "away_team" are also NOT required because older tests may
# omit them. A match string can be built from the available information.
#
# ============================================================================

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


# ============================================================================
# VALIDATION
# ============================================================================

def _validate_candidate(candidate: dict) -> None:
    """
    Validate the core candidate structure.

    The portfolio layer requires:
        match_id
        market
        odds
        score
        value_edge

    The following are optional for backward compatibility:
        selection
        match
        home_team
        away_team
        confidence
        model_probability
        selected_odds
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
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


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
# BASIC FIELD RESOLUTION
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


# ============================================================================
# SELECTION RESOLUTION
# ============================================================================

def _resolve_selection(candidate: dict) -> str:
    """
    Resolve the selection required by tickets.builder.Selection.

    Newer candidates may explicitly provide:
        selection="HOME"

    Older candidates may only provide:
        market="home_win"

    In that case the selection is derived automatically.
    """

    # ------------------------------------------------------------------------
    # New candidate format
    # ------------------------------------------------------------------------
    explicit_selection = candidate.get("selection")

    if explicit_selection is not None:
        if not isinstance(explicit_selection, str):
            raise ValueError(
                "candidate selection must be a string"
            )

        explicit_selection = explicit_selection.strip()

        if explicit_selection:
            return explicit_selection

    # ------------------------------------------------------------------------
    # Legacy / derived format
    # ------------------------------------------------------------------------
    market = _resolve_market(candidate)

    market_to_selection = {
        # Match result
        "home_win": "HOME",
        "draw": "DRAW",
        "away_win": "AWAY",

        # Goals
        "over_2_5": "OVER_2_5",
        "under_2_5": "UNDER_2_5",

        # BTTS
        "btts_yes": "BTTS_YES",
        "btts_no": "BTTS_NO",

        # Common legacy formats
        "1": "HOME",
        "X": "DRAW",
        "2": "AWAY",
        "HOME": "HOME",
        "DRAW": "DRAW",
        "AWAY": "AWAY",

        # Double chance
        "1X": "1X",
        "X2": "X2",
        "12": "12",
    }

    normalized_market = market.strip()

    if normalized_market in market_to_selection:
        return market_to_selection[normalized_market]

    # Case-insensitive compatibility
    lowered_market = normalized_market.lower()

    case_insensitive_map = {
        "home_win": "HOME",
        "draw": "DRAW",
        "away_win": "AWAY",
        "over_2_5": "OVER_2_5",
        "under_2_5": "UNDER_2_5",
        "btts_yes": "BTTS_YES",
        "btts_no": "BTTS_NO",
        "home": "HOME",
        "away": "AWAY",
    }

    if lowered_market in case_insensitive_map:
        return case_insensitive_map[lowered_market]

    # Final compatibility fallback:
    # use the market itself as the selection.
    #
    # This allows newly introduced markets to pass through without requiring
    # another hard-coded mapping immediately.
    return normalized_market


# ============================================================================
# ODDS RESOLUTION
# ============================================================================

def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the numeric odds required by Selection.odds.

    Supported formats:

        odds = 1.80

    or:

        odds = {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    If selected_odds exists, it takes priority.
    """

    # ------------------------------------------------------------------------
    # Explicit selected_odds
    # ------------------------------------------------------------------------
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

    # ------------------------------------------------------------------------
    # Numeric odds
    # ------------------------------------------------------------------------
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

    # ------------------------------------------------------------------------
    # Dictionary odds
    # ------------------------------------------------------------------------
    market = _resolve_market(candidate)

    # Direct market lookup
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

    # Standard aliases
    aliases = {
        "home_win": (
            "HOME",
            "home",
            "1",
        ),
        "draw": (
            "DRAW",
            "draw",
            "X",
        ),
        "away_win": (
            "AWAY",
            "away",
            "2",
        ),
        "over_2_5": (
            "OVER_2_5",
            "OVER 2.5",
        ),
        "under_2_5": (
            "UNDER_2_5",
            "UNDER 2.5",
        ),
        "btts_yes": (
            "BTTS_YES",
            "BTTS YES",
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

    # Explicit selection lookup
    selection = candidate.get("selection")

    if isinstance(selection, str):
        selection = selection.strip()

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


# ============================================================================
# CONFIDENCE RESOLUTION
# ============================================================================

def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve the confidence percentage required by Selection.

    Priority:
        1. confidence
        2. model_probability * 100
        3. score

    Selection.validate() requires 0 <= confidence <= 100.
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

    # Keep it within Selection's valid interface.
    confidence = max(
        0.0,
        min(100.0, confidence),
    )

    return confidence


# ============================================================================
# VALUE EDGE RESOLUTION
# ============================================================================

def _resolve_value_edge(candidate: dict) -> float:
    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        raise ValueError(
            "value_edge cannot be negative"
        )

    return value_edge


# ============================================================================
# MATCH STRING RESOLUTION
# ============================================================================

def _resolve_match(candidate: dict) -> str:
    """
    Resolve the match string required by Selection.match.

    Preferred:
        candidate["match"]

    Then:
        home_team + away_team

    Final fallback:
        match_id

    This intentionally does NOT require home_team/away_team because older
    portfolio tests may not provide them.
    """

    direct_match = candidate.get("match")

    if direct_match is not None:
        direct_match = str(direct_match).strip()

        if direct_match:
            return direct_match

    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    return _resolve_match_id(candidate)


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a portfolio candidate into the exact Selection interface defined
    in tickets/builder.py.
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
    Rank candidates for a ticket.

    A match already used once receives a diversity penalty.

    A match already used twice is not eligible for the ticket.
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

        # If a candidate explicitly says it is not qualified, do not use it.
        if "qualified" in candidate:
            qualified = candidate["qualified"]

            if qualified is False:
                continue

        match_id = _resolve_match_id(candidate)

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
    # Base metric acts as a deterministic secondary sort.
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
# TICKET CONSTRUCTION
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build a single ticket.

    A ticket is not forced when fewer than three valid selections are
    available.
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

        # Never repeat the same match inside one ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)

        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Never force a weak / incomplete ticket.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ============================================================================
# MAIN SMART PORTFOLIO BUILDER
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the four-ticket portfolio.

    Ticket allocation:
        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    Rules:
        - no duplicate match inside a ticket
        - maximum two uses of the same match across the whole portfolio
        - minimum three selections for a built ticket
        - no forced ticket when insufficient candidates exist
        - SAFE/BALANCED/AGGRESSIVE rank by score
        - VALUE ranks by value_edge
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    _validate_candidates(candidates)

    # Never mutate the caller's list or dictionaries.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    usage_counts: Dict[str, int] = {}

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

        if ticket is None:
            continue

        portfolio.append(ticket)

        # Update global match usage.
        for selection in ticket.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(match_id, 0)
                + 1
            )

    return portfolio


# ============================================================================
# MARKET PORTFOLIO ENTRY POINT
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Public market-portfolio entry point.

    market_portfolio.py imports this function.
    """

    return build_smart_portfolio(
        candidates
    )


# ============================================================================
# BACKWARD-COMPATIBILITY ALIAS
# ============================================================================

def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Compatibility alias for older callers.
    """

    return build_smart_portfolio(
        candidates
    )
