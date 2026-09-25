from __future__ import annotations

import unittest
from datetime import datetime, timezone

from data.models import Match
from pipeline.daily_time_guard import filter_upcoming_fixtures


class DailyTimeGuardTests(unittest.TestCase):

    def make_fixture(
        self,
        match_id: str,
        hour: int,
        status: str = "scheduled",
    ) -> Match:
        return Match(
            match_id=match_id,
            home_team=f"Home{match_id}",
            away_team=f"Away{match_id}",
            league="Test League",
            kickoff=datetime(
                2026,
                9,
                25,
                hour,
                0,
                tzinfo=timezone.utc,
            ),
            status=status,
            odds={
                "home_win": 1.80,
                "draw": 3.50,
                "away_win": 4.50,
            },
        )

    def test_future_scheduled_fixture_is_kept(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture(
                "m1",
                15,
            )
        ]

        result = filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            result,
            fixtures,
        )

    def test_past_fixture_is_removed(self):
        as_of = datetime(
            2026,
            9,
            25,
            16,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture(
                "m1",
                15,
            )
        ]

        result = filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            result,
            [],
        )

    def test_fixture_at_exact_as_of_is_removed(self):
        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture(
                "m1",
                15,
            )
        ]

        result = filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            result,
            [],
        )

    def test_finished_fixture_is_removed_even_when_kickoff_is_future(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture(
                "m1",
                15,
                status="finished",
            )
        ]

        result = filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            result,
            [],
        )

    def test_mixed_fixtures_are_filtered_correctly(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("past", 13),
            self.make_fixture("exact", 14),
            self.make_fixture("future1", 15),
            self.make_fixture("future2", 18),
            self.make_fixture(
                "finished",
                20,
                status="finished",
            ),
        ]

        result = filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            [fixture.match_id for fixture in result],
            [
                "future1",
                "future2",
            ],
        )

    def test_fixture_order_is_preserved(self):
        as_of = datetime(
            2026,
            9,
            25,
            12,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m3", 18),
            self.make_fixture("m1", 14),
            self.make_fixture("m2", 16),
        ]

        result = filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            [fixture.match_id for fixture in result],
            [
                "m3",
                "m1",
                "m2",
            ],
        )

    def test_input_list_is_not_modified(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
            self.make_fixture("m2", 16),
        ]

        original = list(fixtures)

        filter_upcoming_fixtures(
            fixtures,
            as_of,
        )

        self.assertEqual(
            fixtures,
            original,
        )

    def test_non_list_fixtures_are_rejected(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            filter_upcoming_fixtures(
                "not a list",
                as_of,
            )

    def test_non_datetime_as_of_is_rejected(self):
        fixtures = [
            self.make_fixture("m1", 15)
        ]

        with self.assertRaises(TypeError):
            filter_upcoming_fixtures(
                fixtures,
                "2026-09-25T14:00:00Z",
            )

    def test_naive_as_of_is_rejected(self):
        fixtures = [
            self.make_fixture("m1", 15)
        ]

        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
        )

        with self.assertRaises(ValueError):
            filter_upcoming_fixtures(
                fixtures,
                as_of,
            )


if __name__ == "__main__":
    unittest.main()
