import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from data.daily_window import (
    NAIROBI_TIMEZONE,
    get_daily_window,
)


class TestDailyWindow(unittest.TestCase):

    def test_default_window_is_midnight_to_0600(self):
        date = datetime(
            2026,
            9,
            23,
            12,
            0,
            tzinfo=NAIROBI_TIMEZONE,
        )

        start, end = get_daily_window(date)

        self.assertEqual(start.hour, 0)
        self.assertEqual(start.minute, 0)

        self.assertEqual(end.hour, 6)
        self.assertEqual(end.minute, 0)

    def test_window_uses_nairobi_timezone(self):
        date = datetime(
            2026,
            9,
            23,
            12,
            0,
            tzinfo=ZoneInfo("UTC"),
        )

        start, end = get_daily_window(date)

        self.assertEqual(
            start.tzinfo,
            NAIROBI_TIMEZONE,
        )

        self.assertEqual(
            end.tzinfo,
            NAIROBI_TIMEZONE,
        )

    def test_date_is_converted_to_nairobi_date(self):
        date = datetime(
            2026,
            9,
            23,
            23,
            30,
            tzinfo=ZoneInfo("UTC"),
        )

        start, end = get_daily_window(date)

        self.assertEqual(start.date(), date.astimezone(
            NAIROBI_TIMEZONE
        ).date())

        self.assertEqual(end.date(), start.date())

    def test_custom_window_is_supported(self):
        date = datetime(
            2026,
            9,
            23,
            10,
            0,
            tzinfo=NAIROBI_TIMEZONE,
        )

        start, end = get_daily_window(
            date,
            start_hour=8,
            end_hour=14,
        )

        self.assertEqual(start.hour, 8)
        self.assertEqual(end.hour, 14)

    def test_overnight_window_crosses_into_next_day(self):
        date = datetime(
            2026,
            9,
            23,
            10,
            0,
            tzinfo=NAIROBI_TIMEZONE,
        )

        start, end = get_daily_window(
            date,
            start_hour=22,
            end_hour=4,
        )

        self.assertEqual(start.day, 23)
        self.assertEqual(start.hour, 22)

        self.assertEqual(end.day, 24)
        self.assertEqual(end.hour, 4)

    def test_invalid_date_is_rejected(self):
        with self.assertRaises(TypeError):
            get_daily_window(None)

    def test_invalid_start_hour_is_rejected(self):
        date = datetime(
            2026,
            9,
            23,
            tzinfo=NAIROBI_TIMEZONE,
        )

        with self.assertRaises(ValueError):
            get_daily_window(
                date,
                start_hour=24,
            )

    def test_invalid_end_hour_is_rejected(self):
        date = datetime(
            2026,
            9,
            23,
            tzinfo=NAIROBI_TIMEZONE,
        )

        with self.assertRaises(ValueError):
            get_daily_window(
                date,
                end_hour=24,
            )


if __name__ == "__main__":
    unittest.main()
