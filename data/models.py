from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class Match:
    match_id: str
    home_team: str
    away_team: str
    league: str
    kickoff: datetime
    status: str
    odds: Dict[str, float]

    def validate(self) -> None:
        if not self.match_id.strip():
            raise ValueError("match_id cannot be empty")

        if not self.home_team.strip():
            raise ValueError("home_team cannot be empty")

        if not self.away_team.strip():
            raise ValueError("away_team cannot be empty")

        if not self.league.strip():
            raise ValueError("league cannot be empty")

        if self.status not in {"scheduled", "live", "finished"}:
            raise ValueError(
                "status must be scheduled, live, or finished"
            )

        if not isinstance(self.kickoff, datetime):
            raise ValueError("kickoff must be a datetime")

        if not self.odds:
            raise ValueError("odds cannot be empty")

        for market, odd in self.odds.items():
            if odd <= 1.0:
                raise ValueError(
                    f"Invalid odds for {market}: {odd}"
                )
