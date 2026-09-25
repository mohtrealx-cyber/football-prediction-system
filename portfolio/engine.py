from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ---------------------------------------------------------------------------
# Portfolio configuration
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Required candidate interface
# ---------------------------------------------------------------------------

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "selection",
    "odds",
    "score",
    "value_edge",
)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_candidate(candidate: dict) -> None:
    """
    Validate the minimum candidate structure required by the portfolio layer.
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


# ---------------------------------------------------------------------------
# Candidate field resolution
# ---------------------------------------------------------------------------

def _resolve_match_id(candidate: dict) -> str:
    match_id = candidate.get("match_id")

    if match_id is None:
        raise ValueError("candidate match_id cannot be missing")

    match_id = str(match_id).strip()

    if not match_id:
        raise ValueError("candidate match_id cannot be empty")

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


def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the numerical odds required by Selection.

    Supported candidate formats include:

        "odds": 1.80

    and:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    A numeric selected_odds field takes priority when available.
    """

    # -------------------------------------------------------
    # Preferred explicit selected odds
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # Dictionary odds
    # -------------------------------------------------------
    if isinstance(raw_odds, dict):
        market = _resolve_market(candidate)

        if market in raw_odds:
            odds = _safe_float(
                raw_odds[market],
                "odds",
            )

        else:
            # Compatibility aliases for older candidate formats.
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

            # Compatibility with selection-keyed dictionaries.
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

    # -------------------------------------------------------
    # Numeric odds
    # -------------------------------------------------------
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
    Resolve confidence for the Selection object.

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


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable match string required by Selection.
    """

    # Direct match field.
    if "match" in candidate:
        direct_match = candidate["match"]

        if direct_match is not None:
            match = str(direct_match).strip()

            if match:
                return match

    # Home/away compatibility fields.
    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    # Final safe fallback.
    return _resolve_match_id(candidate)


# ---------------------------------------------------------------------------
# Candidate -> Selection
# ---------------------------------------------------------------------------

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a portfolio candidate into the exact Selection interface
    defined in tickets/builder.py.
    """

    _validate_candidate(candidate)

    match_id = _resolve_match_id(candidate)
    match = _resolve_match(candidate)
    market = _resolve_market(candidate)
    selection_name = _resolve_selection(candidate)
    odds = _resolve_candidate_odds(candidate)
    confidence = _resolve_confidence(candidate)
    value_edge = _resolve_value_edge(candidate)

    # Keep selection_name referenced intentionally for validation and
    # compatibility. The tickets.builder.Selection interface stores the
    # market in the "market" field and does not have a separate "selection"
    # constructor field.
    _ = selection_name

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


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

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
    Rank candidates for a specific ticket.

    Matches already used once receive a diversity penalty.
    Matches used twice are excluded.
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


# ---------------------------------------------------------------------------
# Ticket construction
# ---------------------------------------------------------------------------

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    A ticket is skipped when fewer than three valid selections are available.
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

        # No duplicate match within a ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)
        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Do not force a weak/incomplete ticket.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ---------------------------------------------------------------------------
# Main portfolio builder
# ---------------------------------------------------------------------------

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
        - minimum 3 selections for a ticket
        - ticket-specific maximum selection count
        - no duplicate match within a ticket
        - maximum two ticket appearances per match
        - no forcing of incomplete tickets
        - input candidates are not mutated
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    _validate_candidates(candidates)

    # Work with copied dictionaries so the caller's input is untouched.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Tracks how many tickets each match has already entered.
    usage_counts: Dict[str, int] = {}

    for ticket_name in TICKET_ORDER:

        ranked = _rank_candidates_for_ticket(
            available,
            ticket_name,
            usage_counts,
        )

        ticket = _build_ticket(
            ticket_name,
            ranked,
        )

        if ticket is None:
            continue

        portfolio.append(ticket)

        for selection in ticket.selections:
            usage_counts[selection.match_id] = (
                usage_counts.get(
                    selection.match_id,
                    0,
                )
                + 1
            )

    return portfolio


# ---------------------------------------------------------------------------
# Backward-compatible public API
# ---------------------------------------------------------------------------

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Backward-compatible public entry point.

    Older modules/tests import this function directly.
    Keep it available so the existing project architecture continues
    to work.
    """

    return build_market_portfolio(candidates)


def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Additional compatibility wrapper for older callers.
    """

    return build_market_portfolio(candidates)
