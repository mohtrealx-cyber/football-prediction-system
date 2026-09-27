from datetime import date

from data.api_fixture_provider import APIFixtureProvider


def load_fixtures(
    destination_path: str | None = None,
    url: str | None = None,
    timeout: int = 30,
    fixture_date: date | None = None,
):
    """
    Load fixtures from API-Football.

    destination_path, url and timeout are retained for
    backwards compatibility with the previous CSV loader.
    """

    provider = APIFixtureProvider()

    return provider.get_matches(
        fixture_date=fixture_date,
    )
