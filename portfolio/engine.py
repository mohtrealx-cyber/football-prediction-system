from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ============================================================
# PORTFOLIO CONFIGURATION
# ============================================================

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


# ============================================================
# REQUIRED CANDIDATE FIELDS
# ============================================================

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "selection",
    "odds",
    "score",
    "value_edge",
)


# ============================================================
# VALIDATION
# ============================================================

def _validate_candidate(candidate: dict) -> None:
    """
    Validate one candidate before portfolio processing.
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


# ============================================================
# NUMERIC HELPERS
# ============================================================

def _safe_float(value: Any, field_name: str) -> float:
    """
    Convert a value to a finite float.
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


# ============================================================
# FIELD RESOLUTION
# ============================================================

def _resolve_match_id(candidate: dict) -> str:
    """
    Resolve the match ID.
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

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market.strip()


def _resolve_selection(candidate: dict) -> str:
    """
    Resolve the selected outcome.
    """
    selection = candidate.get("selection")

    if not isinstance(selection, str) or not selection.strip():
        raise ValueError(
            "candidate selection must be a non-empty string"
        )

    return selection.strip()


def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the numeric odds used by Selection.

    Supported candidate forms:

        "odds": 1.80

    or:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    If selected_odds exists, it takes priority.
    """

    # --------------------------------------------------------
    # Preferred explicit selected odds
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Dictionary odds
    # --------------------------------------------------------

    if isinstance(raw_odds, dict):
        market = _resolve_market(candidate)

        if market in raw_odds:
            odds = _safe_float(
                raw_odds[market],
                "odds",
            )
        else:
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

            found_value = None

            for alias in aliases.get(market, ()):
                if alias in raw_odds:
                    found_value = raw_odds[alias]
                    break

            # Older candidate structures may key odds by the selection.
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

    # --------------------------------------------------------
    # Numeric odds
    # --------------------------------------------------------

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


def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve the confidence required by tickets.builder.Selection.

    Priority:

        1. explicit confidence
        2. model_probability * 100
        3. score

    Selection requires confidence to be 0–100.
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

    return max(
        0.0,
        min(
            100.0,
            confidence,
        ),
    )


def _resolve_value_edge(candidate: dict) -> float:
    """
    Resolve value edge.

    Selection.validate() does not allow negative value_edge.
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
    Resolve the human-readable match string.

    Supported forms:

        candidate["match"]

    or:

        candidate["home_team"] + candidate["away_team"]

    or:

        match_id
    """

    # --------------------------------------------------------
    # Existing explicit match string
    # --------------------------------------------------------

    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    # --------------------------------------------------------
    # Home/Away team fallback
    # --------------------------------------------------------

    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    # --------------------------------------------------------
    # Final fallback
    # --------------------------------------------------------

    return _resolve_match_id(candidate)


# ============================================================
# CANDIDATE -> SELECTION
# ============================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a portfolio candidate into the exact Selection interface
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

    # Use the existing Selection validation.
    selection.validate()

    return selection


# ============================================================
# RANKING
# ============================================================

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
    """
    Get the metric used for ticket ranking.
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

    Matches already used in another ticket receive a diversity penalty.

    A match used twice cannot be used again.
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


# ============================================================
# TICKET CONSTRUCTION
# ============================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    A ticket is not forced when fewer than three valid selections
    are available.
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

        # No duplicate match inside the same ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)

        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Do not force an incomplete ticket.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ============================================================
# MAIN PORTFOLIO BUILDER
# ============================================================

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

        - minimum 3 selections for a non-empty ticket
        - ticket-specific maximums
        - no duplicate match within a ticket
        - maximum two appearances of the same match
        - no forced weak/incomplete ticket
        - input candidates are not mutated
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    # Strict candidate interface validation.
    _validate_candidates(candidates)

    # Copy dictionaries so original input is untouched.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Track how many tickets each match has already appeared in.
    usage_counts: Dict[str, int] = {}

    # Build tickets in configured order.
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

        # Update global match usage counts.
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


# ============================================================
# CURRENT MARKET PORTFOLIO INTERFACE
# ============================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Current market-portfolio entry point.

    Internally uses the established smart portfolio builder.
    """
    return build_smart_portfolio(candidates)


# ============================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================

# Older modules/tests import build_smart_portfolio directly.
# Keep that public API available.
#
# The actual implementation is already build_smart_portfolio(),
# so no second implementation is necessary.
