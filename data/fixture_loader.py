from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from data.api_football_client import get_fixtures
from data.models import Match


KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


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
        fixture_data = fixture.get("fixture") or {}
        teams = fixture.get("teams") or {}
        league = fixture.get("league") or {}
        status_data = fixture_data.get("status") or {}

        fixture_id = fixture_data.get("id")
        kickoff_text = fixture_data.get("date")

        home = teams.get("home") or {}
        away = teams.get("away") or {}

        league_name = league.get("name")
        home_name = home.get("name")
        away_name = away.get("name")
        status_short = status_data.get("short", "")

        if fixture_id is None:
            raise ValueError(
                "API-Football fixture is missing fixture ID"
            )

        if not kickoff_text:
            raise ValueError(
                f"Fixture {fixture_id} is missing kickoff time"
            )

        if not home_name or not away_name:
            raise ValueError(
                f"Fixture {fixture_id} is missing team information"
            )

        if not league_name:
            raise ValueError(
                f"Fixture {fixture_id} is missing league information"
            )

        kickoff = _parse_kickoff(
            kickoff_text
        )

        match = Match(
            match_id=str(fixture_id),
            home_team=home_name.strip(),
            away_team=away_name.strip(),
            league=league_name.strip(),
            kickoff=kickoff,
            status=_convert_status(
                status_short
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


def _parse_kickoff(
    value: str,
) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "kickoff must be a non-empty string"
        )

    try:
        kickoff = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid kickoff datetime: {value}"
        ) from exc

    if kickoff.tzinfo is None:
        raise ValueError(
            "API-Football kickoff must be timezone-aware"
        )

    return kickoff.astimezone(
        KENYA_TIMEZONE
    )


def _convert_status(
    status: str,
) -> str:
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
