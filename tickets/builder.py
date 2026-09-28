from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass(frozen=True)
class Selection:
    match_id: str
    match: str
    market: str
    odds: float
    confidence: float
    value_edge: float

    def validate(self) -> None:
        if not isinstance(self.match_id, str) or not self.match_id.strip():
            raise ValueError("match_id cannot be empty")

        if not isinstance(self.match, str) or not self.match.strip():
            raise ValueError("match cannot be empty")

        if not isinstance(self.market, str) or not self.market.strip():
            raise ValueError("market cannot be empty")

        if self.odds <= 1.0:
            raise ValueError("odds must be greater than 1.0")

        if not 0 <= self.confidence <= 100:
            raise ValueError(
                "confidence must be between 0 and 100"
            )

        if self.value_edge < 0:
            raise ValueError(
                "value_edge cannot be negative"
            )


@dataclass
class Ticket:
    name: str
    stake_percent: float
    selections: List[Selection]

    @property
    def combined_odds(self) -> float:
        result = 1.0

        for selection in self.selections:
            result *= selection.odds

        return round(result, 4)

    @property
    def average_confidence(self) -> float:
        if not self.selections:
            return 0.0

        return round(
            sum(
                selection.confidence
                for selection in self.selections
            )
            / len(self.selections),
            2,
        )

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "stake_percent": self.stake_percent,
            "combined_odds": self.combined_odds,
            "average_confidence": self.average_confidence,
            "selections": [
                asdict(selection)
                for selection in self.selections
            ],
        }


class TicketBuilder:
    """
    Build the four daily portfolio tickets.

    Strategy:

        IRONCLAD   = 40%
        BALANCED   = 20%
        VOLATILITY = 10%
        BENCHMARK  = 30%

    All tickets require at least three selections.

    A match may appear only once inside an individual ticket.

    The builder does not force weak selections merely to fill
    a ticket.
    """

    TICKET_SPECS = (
        (
            "IRONCLAD",
            40.0,
            "confidence",
            80.0,
            3,
            4,
        ),
        (
            "BALANCED",
            20.0,
            "confidence",
            70.0,
            3,
            5,
        ),
        (
            "VOLATILITY",
            10.0,
            "value_edge",
            5.0,
            3,
            6,
        ),
        (
            "BENCHMARK",
            30.0,
            "confidence",
            65.0,
            3,
            6,
        ),
    )

    def __init__(
        self,
        min_matches: int = 3,
        max_matches: int = 6,
    ):
        if not isinstance(min_matches, int):
            raise TypeError(
                "min_matches must be an integer"
            )

        if not isinstance(max_matches, int):
            raise TypeError(
                "max_matches must be an integer"
            )

        if min_matches < 1:
            raise ValueError(
                "min_matches must be at least 1"
            )

        if max_matches < min_matches:
            raise ValueError(
                "max_matches must be >= min_matches"
            )

        self.min_matches = min_matches
        self.max_matches = max_matches

    def build(
        self,
        selections: List[Selection],
    ) -> List[Ticket]:

        if not isinstance(selections, list):
            raise TypeError(
                "selections must be a list"
            )

        validated = []
        seen_ids = set()

        for selection in selections:

            if not isinstance(selection, Selection):
                raise TypeError(
                    "every selection must be a Selection"
                )

            selection.validate()

            # A single match can have multiple markets in the
            # candidate engine, but each ticket may contain the
            # match only once.
            if selection.match_id in seen_ids:
                continue

            seen_ids.add(selection.match_id)
            validated.append(selection)

        if not validated:
            return []

        tickets = []

        for (
            name,
            stake,
            metric,
            threshold,
            default_min,
            default_max,
        ) in self.TICKET_SPECS:

            min_required = max(
                self.min_matches,
                default_min,
            )

            max_allowed = min(
                self.max_matches,
                default_max,
            )

            eligible = self._eligible(
                validated,
                metric,
                threshold,
            )

            if metric == "confidence":

                eligible.sort(
                    key=lambda selection: (
                        selection.confidence,
                        selection.value_edge,
                        selection.odds,
                    ),
                    reverse=True,
                )

            elif metric == "value_edge":

                eligible.sort(
                    key=lambda selection: (
                        selection.value_edge,
                        selection.confidence,
                        selection.odds,
                    ),
                    reverse=True,
                )

            chosen = self._select_without_conflicts(
                eligible,
                max_allowed,
            )

            # Do not manufacture a ticket using weak selections.
            if len(chosen) < min_required:
                continue

            tickets.append(
                Ticket(
                    name=name,
                    stake_percent=stake,
                    selections=chosen,
                )
            )

        return tickets

    @staticmethod
    def _eligible(
        selections: List[Selection],
        metric: str,
        threshold: float,
    ) -> List[Selection]:

        if metric == "confidence":

            return [
                selection
                for selection in selections
                if selection.confidence >= threshold
            ]

        if metric == "value_edge":

            return [
                selection
                for selection in selections
                if selection.value_edge >= threshold
            ]

        raise ValueError(
            f"Unsupported metric: {metric}"
        )

    @staticmethod
    def _select_without_conflicts(
        selections: List[Selection],
        max_allowed: int,
    ) -> List[Selection]:

        chosen = []
        used_matches = set()

        for candidate in selections:

            if candidate.match_id in used_matches:
                continue

            chosen.append(candidate)

            used_matches.add(
                candidate.match_id
            )

            if len(chosen) >= max_allowed:
                break

        return chosen

    @staticmethod
    def validate_tickets(
        tickets: List[Ticket],
    ) -> None:

        if not isinstance(tickets, list):
            raise TypeError(
                "tickets must be a list"
            )

        total_stake = round(
            sum(
                ticket.stake_percent
                for ticket in tickets
            ),
            6,
        )

        # If all four tickets exist, their allocation MUST
        # equal exactly 100%.
        if len(tickets) == 4:

            if abs(
                total_stake - 100.0
            ) > 1e-6:

                raise AssertionError(
                    f"Stake allocation is "
                    f"{total_stake}%, "
                    f"expected 100%"
                )

        for ticket in tickets:

            if not isinstance(
                ticket,
                Ticket,
            ):
                raise TypeError(
                    "every item must be a Ticket"
                )

            match_ids = [
                selection.match_id
                for selection in ticket.selections
            ]

            if len(match_ids) != len(
                set(match_ids)
            ):

                raise AssertionError(
                    f"{ticket.name} contains "
                    f"a duplicate match"
                )

            if not (
                3
                <= len(ticket.selections)
                <= 6
            ):

                raise AssertionError(
                    f"{ticket.name} has "
                    f"{len(ticket.selections)} "
                    f"selections; expected 3-6"
                )

        # Validate the intended four-ticket allocation.
        if len(tickets) == 4:

            expected_stakes = {
                "IRONCLAD": 40.0,
                "BALANCED": 20.0,
                "VOLATILITY": 10.0,
                "BENCHMARK": 30.0,
            }

            actual_stakes = {
                ticket.name: ticket.stake_percent
                for ticket in tickets
            }

            for (
                ticket_name,
                expected_stake,
            ) in expected_stakes.items():

                if ticket_name not in actual_stakes:
                    raise AssertionError(
                        f"Missing required ticket: "
                        f"{ticket_name}"
                    )

                if abs(
                    actual_stakes[ticket_name]
                    - expected_stake
                ) > 1e-6:

                    raise AssertionError(
                        f"{ticket_name} stake is "
                        f"{actual_stakes[ticket_name]}%, "
                        f"expected "
                        f"{expected_stake}%"
                    )
