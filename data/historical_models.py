from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HistoricalMatch:
    """A completed football match used for model training."""

    match_id: str
    home_team: str
    away_team: str
    league: str
    kickoff: datetime
    home_goals: int
    away_goals: int
    odds: dict

    def __post_init__(self):
        if not isinstance(self.match_id, str) or not self.match_id.strip():
            raise ValueError("match_id must be a non-empty string")

        if not isinstance(self.home_team, str) or not self.home_team.strip():
            raise ValueError("home_team must be a non-empty string")

        if not isinstance(self.away_team, str) or not self.away_team.strip():
            raise ValueError("away_team must be a non-empty string")

        if not isinstance(self.league, str) or not self.league.strip():
            raise ValueError("league must be a non-empty string")

        if not isinstance(self.kickoff, datetime):
            raise TypeError("kickoff must be a datetime")

        if self.kickoff.tzinfo is None:
            raise ValueError("kickoff must be timezone-aware")

        if not isinstance(self.home_goals, int):
            raise TypeError("home_goals must be an integer")

        if not isinstance(self.away_goals, int):
            raise TypeError("away_goals must be an integer")

        if self.home_goals < 0:
            raise ValueError("home_goals cannot be negative")

        if self.away_goals < 0:
            raise ValueError("away_goals cannot be negative")

        if not isinstance(self.odds, dict):
            raise TypeError("odds must be a dictionary")
