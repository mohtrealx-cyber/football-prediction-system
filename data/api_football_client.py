from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


API_BASE_URL = "https://v3.football.api-sports.io"

KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


class APIFootballError(RuntimeError):
    """Raised when API-Football returns an API-level error."""


class APIFootballClient:
    """Client for retrieving football fixtures from API-Football."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = API_BASE_URL,
        timeout: int = 30,
    ):
        if api_key is None:
            api_key = os.getenv(
                "API_FOOTBALL_KEY",
                "",
            )

        api_key = api_key.strip()

        if not api_key:
            raise ValueError(
                "API_FOOTBALL_KEY is required"
            )

        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError(
                "base_url must be a non-empty string"
            )

        if (
            not isinstance(timeout, int)
            or isinstance(timeout, bool)
            or timeout <= 0
        ):
            raise ValueError(
                "timeout must be a positive integer"
            )

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ---------------------------------------------------------
    # LOW LEVEL API REQUEST
    # ---------------------------------------------------------

    def get_fixtures(
        self,
        fixture_date: date,
    ) -> list[dict]:
        """Return fixtures for a specific calendar date."""

        if not isinstance(fixture_date, date):
            raise ValueError(
                "fixture_date must be a date"
            )

        query = urlencode(
            {
                "date": fixture_date.isoformat(),
                "timezone": "Africa/Nairobi",
            }
        )

        url = (
            f"{self.base_url}/fixtures?"
            f"{query}"
        )

        request = Request(
            url,
            headers={
                "x-apisports-key": self.api_key,
                "Accept": "application/json",
                "User-Agent": (
                    "football-prediction-system/1.0"
                ),
            },
            method="GET",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw_data = response.read()

        except Exception as exc:
            raise APIFootballError(
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
            raise APIFootballError(
                "API-Football returned invalid JSON"
            ) from exc

        if not isinstance(data, dict):
            raise APIFootballError(
                "API-Football response must be a JSON object"
            )

        errors = data.get("errors")

        if errors:
            raise APIFootballError(
                f"API-Football returned errors: {errors}"
            )

        response_data = data.get("response")

        if not isinstance(response_data, list):
            raise APIFootballError(
                "API-Football response field "
                "'response' must be a list"
            )

        return response_data

    # ---------------------------------------------------------
    # FREE-PLAN DATE HANDLING
    # ---------------------------------------------------------

    @staticmethod
    def _extract_free_plan_dates(
        error_message: str,
    ) -> tuple[date, date] | None:
        """
        Extract the accessible date window from an
        API-Football Free-plan error.

        Example API message:

        Free plans do not have access to this date,
        try from 2026-09-26 to 2026-09-28.
        """

        import re

        if not isinstance(error_message, str):
            return None

        pattern = (
            r"try from\s+"
            r"(\d{4}-\d{2}-\d{2})"
            r"\s+to\s+"
            r"(\d{4}-\d{2}-\d{2})"
        )

        match = re.search(
            pattern,
            error_message,
        )

        if not match:
            return None

        try:
            start_date = date.fromisoformat(
                match.group(1)
            )

            end_date = date.fromisoformat(
                match.group(2)
            )

        except ValueError:
            return None

        return start_date, end_date

    def _get_fixtures_with_free_plan_fallback(
        self,
        fixture_date: date,
    ) -> list[dict]:
        """
        Request fixtures for a date.

        If API-Football rejects the date because of the
        Free-plan date window, automatically retry using
        the latest date allowed by the plan.
        """

        try:
            return self.get_fixtures(
                fixture_date=fixture_date
            )

        except APIFootballError as exc:

            message = str(exc)

            accessible_dates = (
                self._extract_free_plan_dates(
                    message
                )
            )

            if accessible_dates is None:
                raise

            start_date, end_date = accessible_dates

            # Prefer the requested date if it is actually
            # inside the accessible window.
            if (
                start_date
                <= fixture_date
                <= end_date
            ):
                raise

            # If today's date is outside the plan window,
            # use the latest accessible date.
            fallback_date = end_date

            return self.get_fixtures(
                fixture_date=fallback_date
            )

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    def get_fixtures_range(
        self,
        start_date: date,
        days_ahead: int = 1,
    ) -> list[dict]:
        """Return fixtures for start_date and following days."""

        if not isinstance(start_date, date):
            raise ValueError(
                "start_date must be a date"
            )

        if (
            not isinstance(days_ahead, int)
            or isinstance(days_ahead, bool)
            or days_ahead < 0
        ):
            raise ValueError(
                "days_ahead must be a non-negative integer"
            )

        fixtures = []

        for offset in range(days_ahead + 1):

            target_date = (
                start_date
                + timedelta(days=offset)
            )

            try:
                daily_fixtures = (
                    self._get_fixtures_with_free_plan_fallback(
                        fixture_date=target_date
                    )
                )

            except APIFootballError:
                # Do not silently convert real API errors
                # into an empty fixture list.
                raise

            fixtures.extend(
                daily_fixtures
            )

        # Remove duplicate fixtures.
        #
        # This is important when several requested dates fall
        # outside the Free-plan window and therefore resolve
        # to the same fallback date.
        unique_fixtures = []
        seen_ids = set()

        for fixture in fixtures:

            fixture_data = (
                fixture.get("fixture")
                if isinstance(fixture, dict)
                else None
            )

            fixture_id = (
                fixture_data.get("id")
                if isinstance(fixture_data, dict)
                else None
            )

            if fixture_id is not None:

                if fixture_id in seen_ids:
                    continue

                seen_ids.add(fixture_id)

            unique_fixtures.append(
                fixture
            )

        return unique_fixtures

    # ---------------------------------------------------------
    # CONVERSION
    # ---------------------------------------------------------

    @staticmethod
    def convert_fixture(
        fixture: dict,
    ) -> dict:
        """Convert an API-Football fixture into project format."""

        fixture_data = (
            fixture.get("fixture") or {}
        )

        league_data = (
            fixture.get("league") or {}
        )

        teams = (
            fixture.get("teams") or {}
        )

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

        if (
            not home.get("name")
            or not away.get("name")
        ):
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

        status_data = (
            fixture_data.get("status") or {}
        )

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
            "odds": {
                "home_win": 2.00,
                "draw": 3.40,
                "away_win": 3.80,
            },
        }

    # ---------------------------------------------------------
    # CONVERTED FIXTURES
    # ---------------------------------------------------------

    def get_converted_fixtures(
        self,
        fixture_date: date,
    ) -> list[dict]:
        """Get fixtures and convert them to project format."""

        fixtures = self.get_fixtures(
            fixture_date=fixture_date
        )

        return [
            self.convert_fixture(fixture)
            for fixture in fixtures
        ]

    def get_converted_fixture_range(
        self,
        start_date: date,
        days_ahead: int = 1,
    ) -> list[dict]:
        """Get and convert fixtures over multiple days."""

        fixtures = self.get_fixtures_range(
            start_date=start_date,
            days_ahead=days_ahead,
        )

        return [
            self.convert_fixture(fixture)
            for fixture in fixtures
        ]


# -------------------------------------------------------------
# BACKWARD-COMPATIBILITY HELPERS
# -------------------------------------------------------------

def _get_api_key() -> str:
    """Backward-compatible environment API-key helper."""

    api_key = os.getenv(
        "API_FOOTBALL_KEY",
        "",
    ).strip()

    if not api_key:
        raise RuntimeError(
            "API_FOOTBALL_KEY environment variable is not configured"
        )

    return api_key


def _request_fixtures(
    date_text: str,
    timeout: int = 30,
) -> list[dict]:
    """Backward-compatible fixture request function."""

    try:
        fixture_date = date.fromisoformat(
            date_text
        )

    except ValueError as exc:
        raise ValueError(
            f"Invalid fixture date: {date_text}"
        ) from exc

    client = APIFootballClient(
        api_key=_get_api_key(),
        timeout=timeout,
    )

    return client.get_fixtures(
        fixture_date=fixture_date
    )


def _parse_odds(
    fixture: dict,
) -> dict:
    """Return fallback odds required by the Match model."""

    return {
        "home_win": 2.00,
        "draw": 3.40,
        "away_win": 3.80,
    }


def _convert_fixture(
    fixture: dict,
) -> dict:
    """Backward-compatible fixture conversion helper."""

    return APIFootballClient.convert_fixture(
        fixture
    )


def get_fixtures(
    as_of: datetime | None = None,
    days_ahead: int = 1,
    timeout: int = 30,
) -> list[dict]:
    """
    Retrieve fixtures from API-Football.

    The requested date is based on Nairobi time.

    If the Free API plan rejects the requested date,
    the client automatically uses the latest date
    allowed by the plan.
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

    client = APIFootballClient(
        timeout=timeout
    )

    return client.get_fixtures_range(
        start_date=local_time.date(),
        days_ahead=days_ahead,
    )
