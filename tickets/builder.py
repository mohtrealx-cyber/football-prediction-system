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
        if not self.match_id.strip():
            raise ValueError("match_id cannot be empty")
        if not self.match.strip():
            raise ValueError("match cannot be empty")
        if not self.market.strip():
            raise ValueError("market cannot be empty")
        if self.odds <= 1.0:
            raise ValueError("odds must be greater than 1.0")
        if not 0 <= self.confidence <= 100:
            raise ValueError("confidence must be between 0 and 100")
        if self.value_edge < 0:
            raise ValueError("value_edge cannot be negative")


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
            sum(s.confidence for s in self.selections)
            / len(self.selections),
            2,
        )

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "stake_percent": self.stake_percent,
            "combined_odds": self.combined_odds,
            "average_confidence": self.average_confidence,
            "selections": [asdict(s) for s in self.selections],
        }


class TicketBuilder:
    TICKET_SPECS = (
        ("SAFE", 40.0, "confidence", 80.0, 3, 4),
        ("BALANCED", 30.0, "confidence", 70.0, 3, 5),
        ("AGGRESSIVE", 20.0, "confidence", 60.0, 3, 6),
        ("VALUE", 10.0, "value_edge", 5.0, 3, 6),
    )

    def __init__(self, min_matches: int = 3, max_matches: int = 6):
        if min_matches < 1:
            raise ValueError("min_matches must be at least 1")

        if max_matches < min_matches:
            raise ValueError("max_matches must be >= min_matches")

        self.min_matches = min_matches
        self.max_matches = max_matches

    def build(self, selections: List[Selection]) -> List[Ticket]:
        validated = []
        seen_ids = set()

        for selection in selections:
            selection.validate()

            if selection.match_id in seen_ids:
                continue

            seen_ids.add(selection.match_id)
            validated.append(selection)

        if not validated:
            return []

        tickets = []

        for name, stake, metric, threshold, default_min, default_max in self.TICKET_SPECS:
            min_required = max(self.min_matches, default_min)
            max_allowed = min(self.max_matches, default_max)

            eligible = self._eligible(
                validated,
                metric,
                threshold,
            )

            if metric == "confidence":
                eligible.sort(
                    key=lambda s: (
                        s.confidence,
                        s.value_edge,
                        s.odds,
                    ),
                    reverse=True,
                )
            else:
                eligible.sort(
                    key=lambda s: (
                        s.value_edge,
                        s.confidence,
                        s.odds,
                    ),
                    reverse=True,
                )

            chosen = self._select_without_conflicts(
                eligible,
                max_allowed,
            )

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
                s for s in selections
                if s.confidence >= threshold
            ]

        if metric == "value_edge":
            return [
                s for s in selections
                if s.value_edge >= threshold
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
            used_matches.add(candidate.match_id)

            if len(chosen) >= max_allowed:
                break

        return chosen

    @staticmethod
    def validate_tickets(tickets: List[Ticket]) -> None:

        total_stake = round(
            sum(t.stake_percent for t in tickets),
            6,
        )

        if len(tickets) == 4:
            if abs(total_stake - 100.0) > 1e-6:
                raise AssertionError(
                    f"Stake allocation is {total_stake}%, expected 100%"
                )

        for ticket in tickets:

            match_ids = [
                s.match_id
                for s in ticket.selections
            ]

            if len(match_ids) != len(set(match_ids)):
                raise AssertionError(
                    f"{ticket.name} contains a duplicate match"
                )

            if not (
                3 <= len(ticket.selections) <= 6
            ):
                raise AssertionError(
                    f"{ticket.name} has "
                    f"{len(ticket.selections)} selections; "
                    f"expected 3-6"
                )
