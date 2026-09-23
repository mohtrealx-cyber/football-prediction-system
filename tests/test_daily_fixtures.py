import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from data.daily_fixtures import get_daily_fixtures
from data.models import Match


NAIROBI = ZoneInfo("Africa/Nairobi")


class TestDailyFixtures(unittest.TestCase):

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
                8,
                0,
                tzinfo=NAIROBI,
            ),
            status="scheduled",
            odds={"home_win": 2.0},
        )

    def test_returns_matches_inside_default_window(self):
        result = get_daily_fixtures(
            [self.match_inside, self.match_outside],
            self.date,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].match_id, "MATCH-001")

    def test_finished_matches_are_excluded(self):
        finished = Match(
            match_id="MATCH-003",
            home_team="Team E",
            away_team="Team F",
            league="League A",
            kickoff=datetime(
                2026,
                9,
                23,
                3,
                0,
                tzinfo=NAIROBI,
            ),
            status="finished",
            odds={"home_win": 2.0},
        )

        result = get_daily_fixtures(
            [finished],
            self.date,
        )

        self.assertEqual(result, [])

    def test_custom_window_is_used(self):
        result = get_daily_fixtures(
            [self.match_inside, self.match_outside],
            self.date,
            start_hour=7,
            end_hour=10,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].match_id,
            "MATCH-002",
        )

    def test_invalid_date_is_rejected(self):
        with self.assertRaises(TypeError):
            get_daily_fixtures(
                [],
                None,
            )

    def test_matches_must_be_list(self):
        with self.assertRaises(TypeError):
            get_daily_fixtures(
                None,
                self.date,
            )

    def test_invalid_start_hour_is_rejected(self):
        with self.assertRaises(ValueError):
            get_daily_fixtures(
                [],
                self.date,
                start_hour=24,
            )

    def test_invalid_end_hour_is_rejected(self):
        with self.assertRaises(ValueError):
            get_daily_fixtures(
                [],
                self.date,
                end_hour=24,
            )


if __name__ == "__main__":
    unittest.main()
