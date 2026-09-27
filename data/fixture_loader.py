from __future__ import annotations

from data.api_football_client import get_fixtures
from data.models import Match


def load_fixtures(
    destination_path: str,
    url: str = None,
    timeout: int = 30,
):
    """
    Load current and upcoming football fixtures from API-Football.

    destination_path and url are retained for compatibility with
    the existing loader interface.

    API_FOOTBALL_KEY is read from the environment.
    """

    if not isinstance(destination_path, str):
        raise TypeError(
            "destination_path must be a string"
        )

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError(
            "timeout must be a positive integer"
        )

    raw_fixtures = get_fixtures(
        timeout=timeout,
    )

    matches = []

    for fixture in raw_fixtures:
        match = Match(
            match_id=str(
                fixture["fixture"]["id"]
            ),
            home_team=fixture["teams"]["home"]["name"],
            away_team=fixture["teams"]["away"]["name"],
            league=fixture["league"]["name"],
            kickoff=_parse_kickoff(
                fixture["fixture"]["date"]
            ),
            status=_convert_status(
                fixture["fixture"]["status"]["short"]
            ),
            odds={
                "home_win": 2.00,
                "draw": 3.40,
                "away_win": 3.80,
            },
        )

        match.validate()

        matches.append(match)

    return matches


def _parse_kickoff(value: str):
    from datetime import datetime
    from zoneinfo import ZoneInfo

    kickoff = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    return kickoff.astimezone(
        ZoneInfo("Africa/Nairobi")
    )


def _convert_status(status: str) -> str:
    if status in {
        "NS",
        "TBD",
        "PST",
    }:
        return "scheduled"

    if status in {
        "1H",
        "HT",
        "2H",
        "ET",
        "BT",
        "P",
        "LIVE",
    }:
        return "live"

    return "finished"
