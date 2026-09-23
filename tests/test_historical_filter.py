import unittest
from datetime import datetime, timezone, timedelta

from data.historical_models import HistoricalMatch
from data.historical_filter import filter_matches_before


class TestHistoricalFilter(unittest.TestCase):

    def setUp(self):
        base = datetime(
            2026,
            9,
            1,
            15,
            0,
            tzinfo=timezone.utc,
        )

        self.matches = [
            HistoricalMatch(
                match_id="1",
                home_team="Arsenal",
                away_team="Chelsea",
                league="Premier League",
                kickoff=base,
                home_goals=2,
                away_goals=1,
                odds={"home_win": 2.0},
            ),
            HistoricalMatch(
                match_id="2",
                home_team="Liverpool",
                away_team="Everton",
                league="Premier League",
                kickoff=base + timedelta(days=5),
                home_goals=3,
                away_goals=0,
                odds={"home_win": 1.8},
            ),
            HistoricalMatch(
                match_id="3",
                home_team="Chelsea",
                away_team="Liverpool",
                league="Premier League",
                kickoff=base + timedelta(days=10),
                home_goals=1,
                away_goals=2,
                odds={"home_win": 2.1},
            ),
        ]

    def test_returns_matches_before_cutoff(self):
        cutoff = datetime(
            2026,
            9,
            8,
            15,
            0,
            tzinfo=timezone.utc,
        )

        result = filter_matches_before(
            self.matches,
            cutoff,
        )

        self.assertEqual(len(result), 2)

    def test_cutoff_match_is_excluded(self):
        cutoff = self.matches[1].kickoff

        result = filter_matches_before(
            self.matches,
            cutoff,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].match_id, "1")

    def test_matches_after_cutoff_are_excluded(self):
        cutoff = datetime(
            2026,
            9,
            6,
            15,
            0,
            tzinfo=timezone.utc,
        )

        result = filter_matches_before(
            self.matches,
            cutoff,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].match_id, "1")

    def test_original_order_is_preserved(self):
        cutoff = datetime(
            2026,
            9,
            20,
            15,
            0,
            tzinfo=timezone.utc,
        )

        result = filter_matches_before(
            self.matches,
            cutoff,
        )

        self.assertEqual(
            [match.match_id for match in result],
            ["1", "2", "3"],
        )

    def test_empty_list_returns_empty_list(self):
        cutoff = datetime(
            2026,
            9,
            8,
            15,
            0,
            tzinfo=timezone.utc,
        )

        result = filter_matches_before(
            [],
            cutoff,
        )

        self.assertEqual(result, [])

    def test_non_list_is_rejected(self):
        cutoff = datetime(
            2026,
            9,
            8,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            filter_matches_before(None, cutoff)

    def test_invalid_match_item_is_rejected(self):
        cutoff = datetime(
            2026,
            9,
            8,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            filter_matches_before(
                [self.matches[0], "invalid"],
                cutoff,
            )

    def test_naive_cutoff_is_rejected(self):
        cutoff = datetime(
            2026,
            9,
            8,
            15,
            0,
        )

        with self.assertRaises(ValueError):
            filter_matches_before(
                self.matches,
                cutoff,
            )


if __name__ == "__main__":
    unittest.main()
