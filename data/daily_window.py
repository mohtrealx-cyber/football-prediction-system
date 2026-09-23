from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


NAIROBI_TIMEZONE = ZoneInfo("Africa/Nairobi")


def get_daily_window(
    date: datetime,
    start_hour: int = 0,
    end_hour: int = 6,
) -> tuple[datetime, datetime]:
    """
    Return the Nairobi-time analysis window for a given date.

    The default window runs from midnight until 06:00 Nairobi time.
    """

    if not isinstance(date, datetime):
        raise TypeError("date must be a datetime")

    if not 0 <= start_hour <= 23:
        raise ValueError("start_hour must be between 0 and 23")

    if not 0 <= end_hour <= 23:
        raise ValueError("end_hour must be between 0 and 23")

    local_date = date.astimezone(NAIROBI_TIMEZONE).date()

    start = datetime.combine(
        local_date,
        time(start_hour, 0),
        tzinfo=NAIROBI_TIMEZONE,
    )

    if end_hour <= start_hour:
        end_date = local_date + timedelta(days=1)
    else:
        end_date = local_date

    end = datetime.combine(
        end_date,
        time(end_hour, 0),
        tzinfo=NAIROBI_TIMEZONE,
    )

    return start, end
