from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

TICKET_CONFIG = (
    ("SAFE", 40.0),
    ("BALANCED", 30.0),
    ("AGGRESSIVE", 20.0),
    ("VALUE", 10.0),
)

MIN_TICKETS = 4
MIN_SELECTIONS_PER_TICKET = 3
MAX_SELECTIONS_PER_TICKET = 6
MAX_MATCH_REUSE = 2


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass(frozen=True)
class Selection:
    """
    Normalized portfolio selection.

    The portfolio engine accepts the project's candidate dictionaries
    and converts them into Selection objects.
    """

    match_id: str
    home_team: str
    away_team: str
    market: str
    odds: float
    model_probability: float
    value_edge: float
    score: float

    @property
    def selected_odds(self) -> float:
        """
        Compatibility alias.

        Some parts of the project may refer to the selected price as
        selected_odds while older candidate data uses odds.
        """
        return self.odds


@dataclass
class Ticket:
    """
    One portfolio ticket.
    """

    name: str
    stake_percent: float
    selections: list[Selection] = field(default_factory=list)


# ============================================================
# CANDIDATE VALIDATION
# ============================================================

REQUIRED_CANDIDATE_FIELDS = {
    "match_id",
    "home_team",
    "away_team",
    "market",
    "model_probability",
    "value_edge",
    "score",
}


def _validate_candidate(candidate: Any) -> None:
    """
    Validate one candidate.

    The project historically uses `odds`, while some newer code may
    use `selected_odds`.

    Therefore either `odds` OR `selected_odds` is accepted.

    `value_edge` remains mandatory because it is a core portfolio
    qualification metric.
    """

    if not isinstance(candidate, dict):
        raise ValueError(
            "candidate must be a dictionary"
        )

    missing = sorted(
        field
        for field in REQUIRED_CANDIDATE_FIELDS
        if field not in candidate
    )

    if missing:
        raise ValueError(
            f"candidate missing required fields: {missing}"
        )

    if (
        "odds" not in candidate
        and "selected_odds" not in candidate
    ):
        raise ValueError(
            "candidate missing required fields: ['selected_odds']"
        )

    # --------------------------------------------------------
    # String fields
    # --------------------------------------------------------

    for field in (
        "match_id",
        "home_team",
        "away_team",
        "market",
    ):
        value = candidate[field]

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"candidate field '{field}' must be a non-empty string"
            )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    numeric_fields = (
        "model_probability",
        "value_edge",
        "score",
    )

    for field in numeric_fields:
        value = candidate[field]

        if isinstance(value, bool):
            raise ValueError(
                f"candidate field '{field}' must be numeric"
            )

        try:
            float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"candidate field '{field}' must be numeric"
            ) from exc

    # --------------------------------------------------------
    # Odds
    # --------------------------------------------------------

    odds = (
        candidate.get("selected_odds")
        if "selected_odds" in candidate
        else candidate.get("odds")
    )

    if isinstance(odds, bool):
        raise ValueError(
            "candidate odds must be numeric"
        )

    try:
        odds = float(odds)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "candidate odds must be numeric"
        ) from exc

    if odds <= 0:
        raise ValueError(
            "candidate odds must be greater than zero"
        )


def _validate_candidates(
    candidates: Any,
) -> None:
    """
    Validate the complete candidate collection.
    """

    if not isinstance(candidates, list):
        raise ValueError(
            "candidates must be a list"
        )

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================
# NORMALIZATION
# ============================================================

def _get_odds(candidate: dict) -> float:
    """
    Read odds from either supported candidate field.
    """

    if "selected_odds" in candidate:
        return float(candidate["selected_odds"])

    return float(candidate["odds"])


def _normalize_candidate(
    candidate: dict,
) -> Selection:
    """
    Convert a candidate dictionary into a Selection object.
    """

    _validate_candidate(candidate)

    return Selection(
        match_id=str(candidate["match_id"]).strip(),
        home_team=str(candidate["home_team"]).strip(),
        away_team=str(candidate["away_team"]).strip(),
        market=str(candidate["market"]).strip(),
        odds=_get_odds(candidate),
        model_probability=float(
            candidate["model_probability"]
        ),
        value_edge=float(
            candidate["value_edge"]
        ),
        score=float(
            candidate["score"]
        ),
    )


def _normalize_candidates(
    candidates: list[dict],
) -> list[Selection]:
    """
    Normalize candidates while preserving their order.
    """

    return [
        _normalize_candidate(candidate)
        for candidate in candidates
    ]


# ============================================================
# CANDIDATE DEDUPLICATION
# ============================================================

def _deduplicate_candidates(
    candidates: list[Selection],
) -> list[Selection]:
    """
    Keep only the strongest selection for each match.

    A match can have multiple markets in the source candidate list,
    but a single ticket must never contain the same match twice.

    The strongest candidate is determined by:
        1. score
        2. value edge
        3. model probability
    """

    best_by_match: dict[str, Selection] = {}

    for candidate in candidates:
        current = best_by_match.get(
            candidate.match_id
        )

        if current is None:
            best_by_match[candidate.match_id] = candidate
            continue

        current_rank = (
            current.score,
            current.value_edge,
            current.model_probability,
        )

        candidate_rank = (
            candidate.score,
            candidate.value_edge,
            candidate.model_probability,
        )

        if candidate_rank > current_rank:
            best_by_match[candidate.match_id] = candidate

    return list(best_by_match.values())


# ============================================================
# RANKING
# ============================================================

def _rank_candidates(
    candidates: list[Selection],
) -> list[Selection]:
    """
    Rank candidates from strongest to weakest.

    Score is the primary ranking metric.
    Value edge and model probability provide tie-breaking.
    """

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.score,
            candidate.value_edge,
            candidate.model_probability,
        ),
        reverse=True,
    )


# ============================================================
# TICKET HELPERS
# ============================================================

def _new_tickets() -> list[Ticket]:
    """
    Create the four portfolio tickets.
    """

    return [
        Ticket(
            name=name,
            stake_percent=stake_percent,
        )
        for name, stake_percent in TICKET_CONFIG
    ]


def _ticket_contains_match(
    ticket: Ticket,
    match_id: str,
) -> bool:
    """
    Check whether a ticket already contains a match.
    """

    return any(
        selection.match_id == match_id
        for selection in ticket.selections
    )


def _current_match_usage(
    tickets: list[Ticket],
) -> dict[str, int]:
    """
    Count how many tickets currently contain each match.
    """

    usage: dict[str, int] = {}

    for ticket in tickets:
        for selection in ticket.selections:
            usage[selection.match_id] = (
                usage.get(selection.match_id, 0) + 1
            )

    return usage


def _can_add_selection(
    ticket: Ticket,
    selection: Selection,
    usage: dict[str, int],
) -> bool:
    """
    Determine whether a selection can be added to a ticket.
    """

    if len(ticket.selections) >= MAX_SELECTIONS_PER_TICKET:
        return False

    # Never duplicate the same match inside one ticket.
    if _ticket_contains_match(
        ticket,
        selection.match_id,
    ):
        return False

    # Never use the same match more than twice across the
    # complete portfolio.
    if usage.get(selection.match_id, 0) >= MAX_MATCH_REUSE:
        return False

    return True


# ============================================================
# PORTFOLIO CONSTRUCTION
# ============================================================

def _allocate_initial_round(
    tickets: list[Ticket],
    candidates: list[Selection],
    usage: dict[str, int],
) -> None:
    """
    Give each ticket its minimum number of selections.

    Candidates are distributed in a round-robin manner so that
    the portfolio does not concentrate every top candidate into
    the first ticket.
    """

    ticket_index = 0

    for candidate in candidates:

        if all(
            len(ticket.selections)
            >= MIN_SELECTIONS_PER_TICKET
            for ticket in tickets
        ):
            break

        attempts = 0

        while attempts < len(tickets):

            ticket = tickets[
                ticket_index % len(tickets)
            ]

            ticket_index += 1
            attempts += 1

            if not _can_add_selection(
                ticket,
                candidate,
                usage,
            ):
                continue

            ticket.selections.append(candidate)

            usage[candidate.match_id] = (
                usage.get(candidate.match_id, 0) + 1
            )

            break


def _fill_remaining_slots(
    tickets: list[Ticket],
    candidates: list[Selection],
    usage: dict[str, int],
) -> None:
    """
    Fill available ticket slots without violating reuse limits.
    """

    # Prioritize tickets with fewer selections.
    while True:

        target_ticket = min(
            tickets,
            key=lambda ticket: len(ticket.selections),
        )

        if (
            len(target_ticket.selections)
            >= MAX_SELECTIONS_PER_TICKET
        ):
            break

        added = False

        for candidate in candidates:

            if not _can_add_selection(
                target_ticket,
                candidate,
                usage,
            ):
                continue

            target_ticket.selections.append(
                candidate
            )

            usage[candidate.match_id] = (
                usage.get(candidate.match_id, 0) + 1
            )

            added = True
            break

        if not added:
            break

        # Stop once every ticket has at least the minimum.
        if all(
            len(ticket.selections)
            >= MIN_SELECTIONS_PER_TICKET
            for ticket in tickets
        ):
            break


def _build_portfolio(
    candidates: list[Selection],
) -> list[Ticket]:
    """
    Internal portfolio builder.
    """

    if len(candidates) < MIN_TICKETS:
        return []

    tickets = _new_tickets()

    usage: dict[str, int] = {}

    ranked_candidates = _rank_candidates(
        candidates
    )

    _allocate_initial_round(
        tickets=tickets,
        candidates=ranked_candidates,
        usage=usage,
    )

    # Four tickets require at least twelve total selections.
    # With ten unique candidates and a maximum reuse of two,
    # this is possible.
    _fill_remaining_slots(
        tickets=tickets,
        candidates=ranked_candidates,
        usage=usage,
    )

    # --------------------------------------------------------
    # Verify minimum ticket size.
    # --------------------------------------------------------

    if any(
        len(ticket.selections)
        < MIN_SELECTIONS_PER_TICKET
        for ticket in tickets
    ):
        return []

    return tickets


# ============================================================
# PUBLIC API
# ============================================================

def build_market_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Build a four-ticket market portfolio.

    Ticket allocation:

        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    Rules:

        - minimum 3 selections per ticket
        - maximum 6 selections per ticket
        - maximum 2 appearances of a match across the portfolio
        - no duplicate match within one ticket
        - candidates must contain value_edge
        - candidates may use either odds or selected_odds
    """

    _validate_candidates(candidates)

    if len(candidates) < MIN_SELECTIONS_PER_TICKET:
        return []

    normalized = _normalize_candidates(
        candidates
    )

    # Remove weaker duplicate markets belonging to
    # the same match.
    unique_candidates = _deduplicate_candidates(
        normalized
    )

    if len(unique_candidates) < MIN_SELECTIONS_PER_TICKET:
        return []

    return _build_portfolio(
        unique_candidates
    )


def build_smart_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Public compatibility entry point.

    Existing tests and callers use build_smart_portfolio().
    """

    return build_market_portfolio(
        candidates
    )


# ============================================================
# OPTIONAL UTILITY FUNCTIONS
# ============================================================

def get_ticket_stakes(
    tickets: list[Ticket],
) -> list[float]:
    """
    Return ticket stake percentages in portfolio order.
    """

    return [
        float(ticket.stake_percent)
        for ticket in tickets
    ]


def get_ticket_names(
    tickets: list[Ticket],
) -> list[str]:
    """
    Return ticket names in portfolio order.
    """

    return [
        ticket.name
        for ticket in tickets
    ]


def get_match_usage(
    tickets: list[Ticket],
) -> dict[str, int]:
    """
    Return match reuse counts across the portfolio.
    """

    return _current_match_usage(
        tickets
    )
