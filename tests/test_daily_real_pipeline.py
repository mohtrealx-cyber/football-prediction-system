import unittest
from datetime import datetime, timezone

from data.models import Match
from data.historical_models import HistoricalMatch
from pipeline.daily_real import build_daily_real_candidates


class DailyRealPipelineTests(unittest.TestCase):

    def setUp(self):
        self.history = [
            HistoricalMatch(
                match_id="h1",
                home_team="Alpha",
                away_team="Beta",
                league="EPL",
                kickoff=datetime(2026, 9, 20, 15, 0, tzinfo=timezone.utc),
                home_goals=2,
                away_goals=0,
                odds={"home_win": 1.8, "draw": 3.5, "away_win": 4.5},
            ),
            HistoricalMatch(
                match_id="h2",
                home_team="Beta",
                away_team="Alpha",
                league="EPL",
                kickoff=datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc),
                home_goals=1,
                away_goals=1,
                odds={"home_win": 2.8, "draw": 3.2, "away_win": 2.3},
            ),
            HistoricalMatch(
                match_id="h3",
                home_team="Alpha",
                away_team="Gamma",
                league="EPL",
                kickoff=datetime(2026, 9, 22, 15, 0, tzinfo=timezone.utc),
                home_goals=3,
                away_goals=1,
                odds={"home_win": 1.7, "draw": 3.6, "away_win": 5.0},
            ),
            HistoricalMatch(
                match_id="h4",
                home_team="Gamma",
                away_team="Alpha",
                league="EPL",
                kickoff=datetime(2026, 9, 23, 15, 0, tzinfo=timezone.utc),
                home_goals=0,
                away_goals=2,
                odds={"home_win": 4.0, "draw": 3.4, "away_win": 1.8},
            ),
            HistoricalMatch(
                match_id="h5",
                home_team="Beta",
                away_team="Gamma",
                league="EPL",
                kickoff=datetime(2026, 9, 24, 15, 0, tzinfo=timezone.utc),
                home_goals=1,
                away_goals=2,
                odds={"home_win": 2.4, "draw": 3.3, "away_win": 2.7},
            ),
        ]

        self.fixtures = [
            Match(
                match_id="m1",
                home_team="Alpha",
                away_team="Beta",
                league="EPL",
                kickoff=datetime(2026, 9, 25, 15, 0, tzinfo=timezone.utc),
                status="scheduled",
                odds={
                    "home_win": 1.80,
                    "draw": 3.50,
                    "away_win": 4.50,
                },
            ),
            Match(
                match_id="m2",
                home_team="Beta",
                away_team="Gamma",
                league="EPL",
                kickoff=datetime(2026, 9, 25, 18, 0, tzinfo=timezone.utc),
                status="scheduled",
                odds={
                    "home_win": 2.40,
                    "draw": 3.30,
                    "away_win": 2.70,
                },
            ),
        ]

    def test_returns_list(self):
        result = build_daily_real_candidates(
            self.fixtures,
            self.history,
        )
        self.assertIsInstance(result, list)

    def test_only_scheduled_fixtures_are_processed(self):
        fixtures = self.fixtures + [
            Match(
                match_id="finished",
                home_team="Alpha",
                away_team="Gamma",
                league="EPL",
                kickoff=datetime(
                    2026,
                    9,
                    25,
                    20,
                    0,
                    tzinfo=timezone.utc,
                ),
                status="finished",
                odds={
                    "home_win": 1.80,
                    "draw": 3.50,
                    "away_win": 4.50,
                },
            )
        ]

        result = build_daily_real_candidates(
            fixtures,
            self.history,
        )

        match_ids = {item["match_id"] for item in result}

        self.assertNotIn("finished", match_ids)

    def test_fixture_match_id_is_preserved(self):
        result = build_daily_real_candidates(
            self.fixtures,
            self.history,
        )

        match_ids = {item["match_id"] for item in result}

        self.assertIn("m1", match_ids)
        self.assertIn("m2", match_ids)

    def test_fixture_information_is_preserved(self):
        result = build_daily_real_candidates(
            self.fixtures,
            self.history,
        )

        first = next(item for item in result if item["match_id"] == "m1")

        self.assertEqual(first["home_team"], "Alpha")
        self.assertEqual(first["away_team"], "Beta")
        self.assertEqual(first["league"], "EPL")

    def test_odds_are_preserved(self):
        result = build_daily_real_candidates(
            self.fixtures,
            self.history,
        )

        first = next(item for item in result if item["match_id"] == "m1")

        self.assertEqual(first["odds"]["home_win"], 1.80)
        self.assertEqual(first["odds"]["draw"], 3.50)
        self.assertEqual(first["odds"]["away_win"], 4.50)

    def test_future_history_is_not_used(self):
        future_history = self.history + [
            HistoricalMatch(
                match_id="future",
                home_team="Alpha",
                away_team="Beta",
                league="EPL",
                kickoff=datetime(
                    2026,
                    9,
                    26,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                home_goals=10,
                away_goals=0,
                odds={
                    "home_win": 1.2,
                    "draw": 5.0,
                    "away_win": 10.0,
                },
            )
        ]

        result_without_future = build_daily_real_candidates(
            self.fixtures,
            self.history,
        )

        result_with_future = build_daily_real_candidates(
            self.fixtures,
            future_history,
        )

        self.assertEqual(result_without_future, result_with_future)

    def test_finished_history_is_allowed_for_feature_generation(self):
        result = build_daily_real_candidates(
            self.fixtures,
            self.history,
        )

        self.assertIsInstance(result, list)

    def test_missing_fixture_list_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_real_candidates(
                None,
                self.history,
            )

    def test_missing_history_list_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_real_candidates(
                self.fixtures,
                None,
            )

    def test_empty_fixture_list_returns_empty_list(self):
        result = build_daily_real_candidates(
            [],
            self.history,
        )

        self.assertEqual(result, [])

    def test_input_fixtures_are_not_modified(self):
        original_ids = [fixture.match_id for fixture in self.fixtures]

        build_daily_real_candidates(
            self.fixtures,
            self.history,
        )

        self.assertEqual(
            [fixture.match_id for fixture in self.fixtures],
            original_ids,
        )


if __name__ == "__main__":
    unittest.main()
