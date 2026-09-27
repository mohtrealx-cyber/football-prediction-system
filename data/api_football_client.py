from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


API_BASE_URL = "https://v3.football.api-sports.io"

KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


def _get_api_key() -> str:
    api_key = os.getenv("API_FOOTBALL_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "API_FOOTBALL_KEY environment variable is not configured"
        )

    return api_key


def _request_fixtures(
    date_text: str,
    timeout: int = 30,
) -> list[dict]:
    api_key = _get_api_key()

    query = urlencode(
        {
            "date": date_text,
            "timezone": "Africa/Nairobi",
        }
    )

    url = f"{API_BASE_URL}/fixtures?{query}"

    request = Request(
        url,
        headers={
            "x-apisports-key": api_key,
            "Accept": "application/json",
            "User-Agent": "football-prediction-system/1.0",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=timeout,
        ) as response:
            raw_data = response.read()

    except Exception as exc:
        raise RuntimeError(
            f"API-Football request failed: {exc}"
        ) from exc

    try:
        data = json.loads(
            raw_data.decode("utf-8")
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ValueError(
            "API-Football returned invalid JSON"
        ) from exc

    errors = data.get("errors")

    if errors:
        raise RuntimeError(
            f"API-Football returned errors: {errors}"
        )

    response_data = data.get("response")

    if not isinstance(response_data, list):
        raise ValueError(
            "API-Football response field "
            "'response' must be a list"
        )

    return response_data


def _parse_odds(fixture: dict) -> dict:
    """
    API-Football's fixtures endpoint does not reliably provide
    bookmaker odds.

    The Match model requires odds, so we use conservative
    placeholder market values when odds are unavailable.

    These values are NOT prediction odds and should not be
    treated as bookmaker prices.
    """

    return {
        "home_win": 2.00,
        "draw": 3.40,
        "away_win": 3.80,
    }


def _convert_fixture(fixture: dict) -> dict:
    fixture_data = fixture.get("fixture") or {}
    league_data = fixture.get("league") or {}
    teams = fixture.get("teams") or {}

    home = teams.get("home") or {}
    away = teams.get("away") or {}

    fixture_id = fixture_data.get("id")

    kickoff_text = fixture_data.get("date")

    if fixture_id is None:
        raise ValueError(
            "API-Football fixture is missing fixture ID"
        )

    if not kickoff_text:
        raise ValueError(
            f"Fixture {fixture_id} is missing kickoff time"
        )

    if not home.get("name") or not away.get("name"):
        raise ValueError(
            f"Fixture {fixture_id} is missing team information"
        )

    if not league_data.get("name"):
        raise ValueError(
            f"Fixture {fixture_id} is missing league information"
        )

    try:
        kickoff = datetime.fromisoformat(
            kickoff_text.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid kickoff time for fixture "
            f"{fixture_id}: {kickoff_text}"
        ) from exc

    kickoff = kickoff.astimezone(
        KENYA_TIMEZONE
    )

    status_data = fixture_data.get("status") or {}

    status_short = status_data.get(
        "short",
        "",
    )

    if status_short in {
        "NS",
        "TBD",
        "PST",
    }:
        status = "scheduled"
    elif status_short in {
        "1H",
        "HT",
        "2H",
        "ET",
        "BT",
        "P",
        "LIVE",
    }:
        status = "live"
    else:
        status = "finished"

    return {
        "match_id": str(fixture_id),
        "home_team": home["name"].strip(),
        "away_team": away["name"].strip(),
        "league": league_data["name"].strip(),
        "kickoff": kickoff,
        "status": status,
        "odds": _parse_odds(fixture),
    }


def get_fixtures(
    as_of: datetime | None = None,
    days_ahead: int = 1,
    timeout: int = 30,
) -> list[dict]:
    """
    Retrieve fixtures from API-Football for today and the
    following configurable number of days.

    The returned dictionaries are ready to be converted into
    Match objects.
    """

    if as_of is None:
        as_of = datetime.now(
            KENYA_TIMEZONE
        )

    if (
        not isinstance(as_of, datetime)
        or as_of.tzinfo is None
        or as_of.utcoffset() is None
    ):
        raise ValueError(
            "as_of must be a timezone-aware datetime"
        )

    if (
        not isinstance(days_ahead, int)
        or isinstance(days_ahead, bool)
        or days_ahead < 0
    ):
        raise ValueError(
            "days_ahead must be a non-negative integer"
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError(
            "timeout must be a positive integer"
        )

    local_time = as_of.astimezone(
        KENYA_TIMEZONE
    )

    fixtures = []

    for offset in range(days_ahead + 1):
        target_date = (
            local_time + timedelta(days=offset)
        ).date()

        date_text = target_date.isoformat()

        fixtures.extend(
            _request_fixtures(
                date_text=date_text,
                timeout=timeout,
            )
        )

    return fixtures
