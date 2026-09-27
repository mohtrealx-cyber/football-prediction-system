from __future__ import annotations

import json
import os
from datetime import date
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://v3.football.api-sports.io"

DEFAULT_TIMEOUT = 30

PREMIER_LEAGUE_ID = 39


class APIFootballError(RuntimeError):
    """Raised when API-Football returns an API-level error."""


class APIFootballClient:
    """Client for API-Football."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if api_key is None:
            api_key = os.getenv("API_FOOTBALL_KEY")

        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError(
                "API_FOOTBALL_KEY environment variable is missing"
            )

        if (
            not isinstance(timeout, int)
            or isinstance(timeout, bool)
            or timeout <= 0
        ):
            raise ValueError(
                "timeout must be a positive integer"
            )

        self.api_key = api_key.strip()
        self.timeout = timeout

    def _get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{BASE_URL}{endpoint}"

        if params:
            clean_params = {
                key: value
                for key, value in params.items()
                if value is not None
            }

            if clean_params:
                url = f"{url}?{urlencode(clean_params)}"

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

        if not raw_data:
            raise APIFootballError(
                "API-Football returned an empty response"
            )

        try:
            payload = json.loads(
                raw_data.decode("utf-8")
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise APIFootballError(
                "API-Football returned invalid JSON"
            ) from exc

        if not isinstance(payload, dict):
            raise APIFootballError(
                "API-Football response is not a JSON object"
            )

        errors = payload.get("errors")

        if errors:
            raise APIFootballError(
                f"API-Football returned errors: {errors}"
            )

        return payload

    def get_fixtures(
        self,
        fixture_date: date,
        league_id: int = PREMIER_LEAGUE_ID,
        season: int | None = None,
    ) -> list[dict]:

        if not isinstance(fixture_date, date):
            raise TypeError(
                "fixture_date must be a date"
            )

        if not isinstance(league_id, int):
            raise TypeError(
                "league_id must be an integer"
            )

        if season is None:
            season = fixture_date.year

        payload = self._get(
            "/fixtures",
            {
                "league": league_id,
                "season": season,
                "date": fixture_date.isoformat(),
                "timezone": "Africa/Nairobi",
            },
        )

        response = payload.get("response", [])

        if not isinstance(response, list):
            raise APIFootballError(
                "Invalid fixtures response"
            )

        return response

    def get_fixture_odds(
        self,
        fixture_id: int,
    ) -> list[dict]:

        if not isinstance(fixture_id, int):
            raise TypeError(
                "fixture_id must be an integer"
            )

        payload = self._get(
            "/odds",
            {
                "fixture": fixture_id,
            },
        )

        response = payload.get("response", [])

        if not isinstance(response, list):
            raise APIFootballError(
                "Invalid odds response"
            )

        return response
