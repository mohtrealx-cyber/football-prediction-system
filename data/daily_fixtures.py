from datetime import datetime

from data.daily_window import get_daily_window
from data.fixture_filter import filter_fixtures_by_time
from data.models import Match


def get_daily_fixtures(
    matches: list[Match],
    date: datetime,
    start_hour: int = 0,
    end_hour: int = 6,
) -> list[Match]:
    """Return scheduled fixtures inside the Nairobi daily window."""

    if not isinstance(date, datetime):
        raise TypeError("date must be a datetime")

    start, end = get_daily_window(
        date=date,
        start_hour=start_hour,
        end_hour=end_hour,
    )

    return filter_fixtures_by_time(
        matches=matches,
        start=start,
        end=end,
    )
