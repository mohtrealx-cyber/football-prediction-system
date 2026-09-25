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
# REQUIRED LEGACY/CORE CANDIDATE FIELDS
# ============================================================================

# IMPORTANT:
# "selection" is NOT required here.
#
# Older portfolio candidates use:
#   match_id
#   market
#   odds
#   score
#   value_edge
#
# The engine derives the Selection.selection value from the market when
# a separate "selection" field is not supplied.
REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


# ============================================================================
# GENERAL VALIDATION
# ============================================================================

def _validate_candidate(candidate: dict) -> None:
    """
    Validate the core candidate interface.

    A candidate must contain the five fields historically used by the
    portfolio engine. Additional fields are allowed.
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
# MATCH / MARKET / SELECTION RESOLUTION
# ============================================================================

def _resolve_match_id(candidate: dict) -> str:
    match_id = candidate.get("match_id")

    if match_id is None:
        raise ValueError("candidate match_id cannot be missing")

    match_id = str(match_id).strip()

    if not match_id:
        raise ValueError("candidate match_id cannot be empty")

    return match_id


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable match string required by Selection.
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

    # Older tests/candidates may not have team names.
    # The match_id is still sufficient for the Selection interface.
    return _resolve_match_id(candidate)


def _resolve_market(candidate: dict) -> str:
    market = candidate.get("market")

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market.strip()


def _normalise_market(market: str) -> str:
    return market.strip().upper().replace("-", "_").replace(" ", "_")


def _resolve_selection(candidate: dict) -> str:
    """
    Resolve Selection.selection.

    Newer candidates may explicitly provide "selection".

    Older candidates do not, so derive it from "market".
    """
    explicit_selection = candidate.get("selection")

    if explicit_selection is not None:
        selection = str(explicit_selection).strip()

        if selection:
            return selection

    market = _normalise_market(
        _resolve_market(candidate)
    )

    market_selection_map = {
        # Result markets
        "HOME_WIN": "HOME",
        "DRAW": "DRAW",
        "AWAY_WIN": "AWAY",

        # Common legacy names
        "HOME": "HOME",
        "AWAY": "AWAY",
        "1": "HOME",
        "X": "DRAW",
        "2": "AWAY",
        "1X": "1X",
        "X2": "X2",
        "12": "12",

        # Goals markets
        "OVER_2_5": "OVER_2_5",
        "UNDER_2_5": "UNDER_2_5",

        # BTTS markets
        "BTTS_YES": "BTTS_YES",
        "BTTS_NO": "BTTS_NO",
        "BTTS": "BTTS",
    }

    if market in market_selection_map:
        return market_selection_map[market]

    # Generic fallback.
    #
    # Selection.validate() only requires a non-empty string, so preserving
    # the market name is safer than inventing another value.
    return market


# ============================================================================
# ODDS RESOLUTION
# ============================================================================

def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the actual numeric odds used by Selection.

    Supported candidate formats:

        "odds": 1.80

    or:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    A numeric "selected_odds" value takes priority when available.
    """

    # ------------------------------------------------------------------------
    # Explicit selected odds
    # ------------------------------------------------------------------------

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

    raw_odds = candidate.get("odds")

    # ------------------------------------------------------------------------
    # Dictionary odds
    # ------------------------------------------------------------------------

    if isinstance(raw_odds, dict):
        market = _resolve_market(candidate)

        # Direct lookup.
        if market in raw_odds:
            odds = _safe_float(
                raw_odds[market],
                "odds",
            )

        else:
            market_normalised = _normalise_market(market)

            aliases = {
                "HOME_WIN": (
                    "home_win",
                    "HOME",
                    "1",
                ),
                "DRAW": (
                    "draw",
                    "DRAW",
                    "X",
                ),
                "AWAY_WIN": (
                    "away_win",
                    "AWAY",
                    "2",
                ),
                "OVER_2_5": (
                    "over_2_5",
                    "OVER_2_5",
                    "OVER 2.5",
                ),
                "UNDER_2_5": (
                    "under_2_5",
                    "UNDER_2_5",
                    "UNDER 2.5",
                ),
                "BTTS_YES": (
                    "btts_yes",
                    "BTTS_YES",
                    "BTTS YES",
                ),
                "BTTS_NO": (
                    "btts_no",
                    "BTTS_NO",
                    "BTTS NO",
                ),
                "1X": (
                    "1X",
                    "1x",
                ),
                "X2": (
                    "X2",
                    "x2",
                ),
                "12": (
                    "12",
                ),
            }

            found_value = None

            for key in aliases.get(
                market_normalised,
                (),
            ):
                if key in raw_odds:
                    found_value = raw_odds[key]
                    break

            # Explicit selection may also correspond to an odds dictionary
            # key.
            if found_value is None:
                selection = candidate.get("selection")

                if selection is not None:
                    selection = str(selection)

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

    # ------------------------------------------------------------------------
    # Numeric odds
    # ------------------------------------------------------------------------

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
# CONFIDENCE / VALUE
# ============================================================================

def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve Selection.confidence.

    Priority:
        1. explicit confidence
        2. model_probability * 100
        3. score
    """

    if "confidence" in candidate:
        value = _safe_float(
            candidate["confidence"],
            "confidence",
        )

    elif "model_probability" in candidate:
        probability = _safe_float(
            candidate["model_probability"],
            "model_probability",
        )

        value = probability * 100.0

    else:
        value = _safe_float(
            candidate["score"],
            "score",
        )

    # Selection.validate() requires 0 <= confidence <= 100.
    return max(
        0.0,
        min(100.0, value),
    )


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
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a portfolio candidate to the exact Selection structure from
    tickets/builder.py.
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

    # Use the validation already defined by tickets/builder.py.
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

    Candidates already used by other tickets receive a diversity penalty.

    A match can appear in at most MAX_MATCH_USAGE tickets.
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

        # Maximum reuse across the entire portfolio.
        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_metric = _candidate_metric(
            candidate,
            metric,
        )

        adjusted_metric = (
            base_metric
            - usage_count * DIVERSITY_PENALTY
        )

        ranked.append(
            (
                adjusted_metric,
                base_metric,
                candidate,
            )
        )

    # Highest adjusted metric first.
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

        # No duplicate match within the same ticket.
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
# MODERN MARKET PORTFOLIO
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the four-ticket portfolio.

    SAFE       = 40%
    BALANCED   = 30%
    AGGRESSIVE = 20%
    VALUE      = 10%

    Rules:
        - no forced ticket below 3 selections
        - SAFE max 4
        - BALANCED max 5
        - AGGRESSIVE max 6
        - VALUE max 5
        - no duplicate match inside one ticket
        - same match maximum two tickets
        - input candidates are not mutated
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    # Validate everything BEFORE modifying/processing it.
    _validate_candidates(candidates)

    # Never mutate caller-owned candidate dictionaries.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Tracks how many tickets already use each match.
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

        # Do not force weak/incomplete ticket.
        if ticket is None:
            continue

        portfolio.append(ticket)

        # Update global match usage.
        for selection in ticket.selections:
            usage_counts[selection.match_id] = (
                usage_counts.get(
                    selection.match_id,
                    0,
                )
                + 1
            )

    return portfolio


# ============================================================================
# LEGACY PUBLIC API
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Backward-compatible public function.

    Older tests and portfolio.market_portfolio.py import this function.
    Keep it available permanently.
    """
    return build_market_portfolio(candidates)


# ============================================================================
# OPTIONAL COMPATIBILITY ALIAS
# ============================================================================

def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Additional compatibility wrapper for older callers.
    """
    return build_market_portfolio(candidates)
