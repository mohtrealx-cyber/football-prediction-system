import unittest
from datetime import datetime, timezone

from data.fixture_filter import filter_fixtures_by_time
from data.models import Match


class TestFixtureFilter(unittest.TestCase):

    def setUp(self):
        self.start = datetime(
            2026,
            9,
            23,
            12,
            0,
            tzinfo=timezone.utc,
        )

        self.end = datetime(
            2026,
            9,
            23,
            22,
            0,
            tzinfo=timezone.utc,
        )

        self.match_inside = Match(
            match_id="MATCH-001",
            home_team="Team A",
            away_team="Team B",
            league="Test League",
            kickoff=datetime(
                2026,
                9,
                23,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            status="scheduled",
            odds={"home_win": 2.0},
        )

        self.match_outside = Match(
            match_id="MATCH-002",
            home_team="Team C",
            away_team="Team D",
            league="Test League",
            kickoff=datetime(
                2026,
                9,
                24,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            status="scheduled",
            odds={"home_win": 2.0},
        )

    def test_match_inside_window_is_kept(self):
        result = filter_fixtures_by_time(
            [self.match_inside],
            self.start,
            self.end,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].match_id, "MATCH-001")

    def test_match_outside_window_is_removed(self):
        result = filter_fixtures_by_time(
            [self.match_outside],
            self.start,
            self.end,
        )

        self.assertEqual(result, [])

    def test_start_boundary_is_included(self):
        match = Match(
            match_id="MATCH-003",
            home_team="Team E",
            away_team="Team F",
            league="Test League",
            kickoff=self.start,
            status="scheduled",
            odds={"home_win": 2.0},
        )

        result = filter_fixtures_by_time(
            [match],
            self.start,
            self.end,
        )

        self.assertEqual(len(result), 1)

    def test_end_boundary_is_included(self):
        match = Match(
            match_id="MATCH-004",
            home_team="Team G",
            away_team="Team H",
            league="Test League",
            kickoff=self.end,
            status="scheduled",
            odds={"home_win": 2.0},
        )

        result = filter_fixtures_by_time(
            [match],
            self.start,
            self.end,
        )

        self.assertEqual(len(result), 1)

    def test_finished_matches_are_removed(self):
        finished_match = Match(
            match_id="MATCH-005",
            home_team="Team I",
            away_team="Team J",
            league="Test League",
            kickoff=datetime(
                2026,
                9,
                23,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            status="finished",
            odds={"home_win": 2.0},
        )

        result = filter_fixtures_by_time(
            [finished_match],
            self.start,
            self.end,
        )

        self.assertEqual(result, [])

    def test_matches_must_be_list(self):
        with self.assertRaises(TypeError):
            filter_fixtures_by_time(
                None,
                self.start,
                self.end,
            )

    def test_naive_datetime_is_rejected(self):
        naive_start = datetime(2026, 9, 23, 12, 0)

        with self.assertRaises(ValueError):
            filter_fixtures_by_time(
                [self.match_inside],
                naive_start,
                self.end,
            )

    def test_invalid_window_is_rejected(self):
        with self.assertRaises(ValueError):
            filter_fixtures_by_time(
                [self.match_inside],
                self.end,
                self.start,
            )


if __name__ == "__main__":
    unittest.main()
