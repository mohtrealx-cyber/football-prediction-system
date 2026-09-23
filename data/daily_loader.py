from datetime import datetime

from data.daily_fixtures import get_daily_fixtures
from data.fixture_loader import load_fixtures


def load_daily_fixtures(
    destination_path: str,
    date: datetime,
    url: str = None,
    timeout: int = 30,
    start_hour: int = 0,
    end_hour: int = 6,
):
    """
    Download fixtures, load them, and return only
    the fixtures inside the Nairobi daily window.
    """

    matches = load_fixtures(
        destination_path=destination_path,
        url=url,
        timeout=timeout,
    )

    return get_daily_fixtures(
        matches=matches,
        date=date,
        start_hour=start_hour,
        end_hour=end_hour,
    )
