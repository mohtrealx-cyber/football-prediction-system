from __future__ import annotations

from data.api_football_client import (
    APIFootballClient,
    get_fixtures,
)


def load_fixtures(
    destination_path: str,
    url: str | None = None,
    timeout: int = 30,
):
    """
    Load fixtures from API-Football and convert them into
    the project's Match objects.

    The destination_path and url arguments are retained for
    compatibility with the existing loader interface.

    API-Football is now the live fixture source.
    """

    if not isinstance(destination_path, str):
        raise TypeError(
            "destination_path must be a string"
        )

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if url is not None and (
        not isinstance(url, str)
        or not url.strip()
    ):
        raise ValueError(
            "url must be a non-empty string"
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError(
            "timeout must be a positive integer"
        )

    # The API-Football client handles the current date.
    #
    # Keep this call deliberately simple because the existing
    # test suite expects timeout to be passed directly.
    raw_fixtures = get_fixtures(
        timeout=timeout,
    )

    matches = []

    for fixture in raw_fixtures:

        # API-Football fixtures returned by the client are normally
        # raw API dictionaries. Convert them into the project's
        # normalized fixture structure.
        if "match_id" not in fixture:
            fixture = APIFootballClient.convert_fixture(
                fixture
            )

        matches.append(fixture)

    return matches
