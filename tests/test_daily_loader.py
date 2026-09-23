import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from data.daily_loader import load_daily_fixtures
from data.models import Match


NAIROBI = ZoneInfo("Africa/Nairobi")


class TestDailyLoader(unittest.TestCase):

    def setUp(self):
        self.date = datetime(
            2026,
            9,
            23,
            10,
            0,
            tzinfo=NAIROBI,
        )

        self.match_inside = Match(
            match_id="MATCH-001",
            home_team="Team A",
            away_team="Team B",
            league="League A",
            kickoff=datetime(
                2026,
                9,
                23,
                3,
                0,
                tzinfo=NAIROBI,
            ),
            status="scheduled",
            odds={"home_win": 2.0},
        )

        self.match_outside = Match(
            match_id="MATCH-002",
            home_team="Team C",
            away_team="Team D",
            league="League A",
            kickoff=datetime(
                2026,
                9,
                23,
                10,
                0,
                tzinfo=NAIROBI,
            ),
            status="scheduled",
            odds={"home_win": 2.0},
        )

    def test_returns_only_daily_fixtures(self):
        with patch(
            "data.daily_loader.load_fixtures",
            return_value=[
                self.match_inside,
                self.match_outside,
            ],
        ):
            result = load_daily_fixtures(
                destination_path="fixtures.csv",
                date=self.date,
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].match_id,
            "MATCH-001",
        )

    def test_passes_download_parameters(self):
        with patch(
            "data.daily_loader.load_fixtures",
            return_value=[self.match_inside],
        ) as mock_loader:

            load_daily_fixtures(
                destination_path="data.csv",
                date=self.date,
                url="https://example.com/data.csv",
                timeout=15,
            )

        mock_loader.assert_called_once_with(
            destination_path="data.csv",
            url="https://example.com/data.csv",
            timeout=15,
        )

    def test_custom_daily_window_is_used(self):
        with patch(
            "data.daily_loader.load_fixtures",
            return_value=[
                self.match_inside,
                self.match_outside,
            ],
        ):
            result = load_daily_fixtures(
                destination_path="fixtures.csv",
                date=self.date,
                start_hour=9,
                end_hour=11,
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].match_id,
            "MATCH-002",
        )


if __name__ == "__main__":
    unittest.main()
