```python
import unittest

from portfolio.market_portfolio import build_market_portfolio


class TestMarketPortfolio(unittest.TestCase):

    def setUp(self):
        self.candidates = []

        for index in range(12):
            self.candidates.append(
                {
                    "match_id": f"match_{index + 1:03d}",
                    "home_team": f"Home Team {index + 1}",
                    "away_team": f"Away Team {index + 1}",
                    "market": "home_win",
                    "model_probability": 0.70,
                    "odds": 1.80,
                    "market_probability": 1 / 1.80,
                    "expected_value": 0.26,
                    "value_edge": 14.44,
                    "qualified": True,
                    "score": 80.0 - index,
                }
            )

    def test_builds_four_ticket_portfolio(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        self.assertEqual(
            len(portfolio),
            4,
        )

    def test_portfolio_has_expected_ticket_names(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        ticket_names = [
            ticket.name
            for ticket in portfolio
        ]

        self.assertEqual(
            ticket_names,
            [
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            ],
        )

    def test_ticket_stake_allocations_are_correct(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        stakes = {
            ticket.name: ticket.stake_percent
            for ticket in portfolio
        }

        self.assertEqual(
            stakes,
            {
                "IRONCLAD": 40.0,
                "BALANCED": 30.0,
                "VOLATILITY": 20.0,
                "BENCHMARK": 10.0,
            },
        )

    def test_each_ticket_has_at_least_three_matches(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        for ticket in portfolio:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_no_ticket_has_more_than_six_matches(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        for ticket in portfolio:
            self.assertLessEqual(
                len(ticket.selections),
                6,
            )

    def test_match_reuse_limit_is_respected(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        usage = {}

        for ticket in portfolio:
            for selection in ticket.selections:
                match_id = selection.match_id
                usage[match_id] = (
                    usage.get(match_id, 0) + 1
                )

        for count in usage.values():
            self.assertLessEqual(
                count,
                2,
            )

    def test_empty_candidates_return_empty_portfolio(self):
        portfolio = build_market_portfolio([])

        self.assertEqual(
            portfolio,
            [],
        )

    def test_non_list_candidates_are_rejected(self):
        with self.assertRaises(TypeError):
            build_market_portfolio({})


if __name__ == "__main__":
    unittest.main()
```

This fixes the exact old-name assertions shown in your failure. The original test was explicitly checking `SAFE`, `AGGRESSIVE`, and `VALUE`.

---

### 2. Replace `tests/test_final_daily_system.py` with this FULL code

Only the ticket naming/stake expectations are changed here; the rest of the test logic stays intact.

```python
import json
import unittest
from datetime import datetime, timedelta, timezone

from data.historical_models import HistoricalMatch
from data.models import Match
from pipeline.daily_report_output import build_daily_report_output


MARKETS = (
    "home_win",
    "draw",
    "away_win",
    "over_2_5",
    "under_2_5",
    "btts_yes",
    "btts_no",
)


class FinalDailySystemTests(unittest.TestCase):

    def setUp(self):
        self.as_of = datetime(
            2026,
            9,
            25,
            10,
            0,
            tzinfo=timezone.utc,
        )

    def _history(self):
        base_time = datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        )

        historical_pairs = [
            ("TeamA", "TeamB"),
            ("TeamC", "TeamD"),
            ("TeamE", "TeamF"),
            ("TeamG", "TeamH"),
            ("TeamI", "TeamJ"),
            ("TeamK", "TeamL"),
            ("TeamA", "TeamC"),
            ("TeamD", "TeamE"),
            ("TeamF", "TeamG"),
            ("TeamH", "TeamI"),
            ("TeamJ", "TeamK"),
            ("TeamL", "TeamA"),
        ]

        results = [
            (2, 0),
            (1, 1),
            (2, 1),
            (1, 0),
            (3, 1),
            (1, 2),
            (2, 0),
            (0, 0),
            (2, 1),
            (1, 1),
            (3, 0),
            (0, 2),
        ]

        history = []

        for index, (
            (home_team, away_team),
            (home_goals, away_goals),
        ) in enumerate(
            zip(historical_pairs, results)
        ):
            history.append(
                HistoricalMatch(
                    match_id=f"h{index + 1}",
                    home_team=home_team,
                    away_team=away_team,
                    league="TEST_LEAGUE",
                    kickoff=base_time + timedelta(
                        hours=index * 6
                    ),
                    home_goals=home_goals,
                    away_goals=away_goals,
                    odds={},
                )
            )

        return history

    def _fixtures(self):
        fixture_pairs = [
            ("TeamA", "TeamB"),
            ("TeamC", "TeamD"),
            ("TeamE", "TeamF"),
            ("TeamG", "TeamH"),
            ("TeamI", "TeamJ"),
            ("TeamK", "TeamL"),
            ("TeamA", "TeamC"),
            ("TeamD", "TeamE"),
            ("TeamF", "TeamG"),
            ("TeamH", "TeamI"),
            ("TeamJ", "TeamK"),
            ("TeamL", "TeamA"),
        ]

        fixtures = []

        for index, (
            home_team,
            away_team,
        ) in enumerate(fixture_pairs):

            odds = {
                market: 10.0
                for market in MARKETS
            }

            fixtures.append(
                Match(
                    match_id=f"m{index + 1}",
                    home_team=home_team,
                    away_team=away_team,
                    league="TEST_LEAGUE",
                    kickoff=datetime(
                        2026,
                        9,
                        25,
                        12,
                        0,
                        tzinfo=timezone.utc,
                    ) + timedelta(hours=index),
                    status="scheduled",
                    odds=odds,
                )
            )

        return fixtures

    def test_complete_daily_system_returns_report(self):
        fixtures = self._fixtures()
        history = self._history()

        result = build_daily_report_output(
            fixtures,
            history,
            self.as_of,
        )

        self.assertIsInstance(
            result,
            dict,
        )

        self.assertEqual(
            result["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )

        self.assertIn(
            result["status"],
            {
                "READY",
                "NO_BET",
            },
        )

    def test_complete_daily_system_is_json_serializable(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        serialized = json.dumps(
            result
        )

        self.assertIsInstance(
            serialized,
            str,
        )

    def test_daily_metadata_is_correct(self):
        fixtures = self._fixtures()

        result = build_daily_report_output(
            fixtures,
            self._history(),
            self.as_of,
        )

        self.assertEqual(
            result["fixtures_received"],
            12,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            12,
        )

    def test_ready_portfolio_has_four_tickets(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        if result["status"] == "NO_BET":
            self.skipTest(
                "No qualifying portfolio was produced."
            )

        portfolio = result["portfolio"]

        self.assertIsInstance(
            portfolio,
            list,
        )

        self.assertEqual(
            len(portfolio),
            4,
        )

        ticket_names = {
            ticket["name"]
            for ticket in portfolio
        }

        self.assertEqual(
            ticket_names,
            {
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            },
        )

    def test_ready_portfolio_has_valid_stakes(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        if result["status"] == "NO_BET":
            self.skipTest(
                "No qualifying portfolio was produced."
            )

        portfolio = result["portfolio"]

        expected_stakes = {
            "IRONCLAD": 40.0,
            "BALANCED": 30.0,
            "VOLATILITY": 20.0,
            "BENCHMARK": 10.0,
        }

        for ticket in portfolio:
            self.assertEqual(
                ticket["stake_percent"],
                expected_stakes[ticket["name"]],
            )

    def test_empty_inputs_produce_no_bet(self):
        result = build_daily_report_output(
            [],
            [],
            self.as_of,
        )

        self.assertEqual(
            result["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["fixtures_received"],
            0,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            0,
        )

        self.assertEqual(
            result["portfolio"]["status"],
            "NO_BET",
        )

    def test_inputs_are_not_modified(self):
        fixtures = self._fixtures()
        history = self._history()

        original_fixture_ids = [
            fixture.match_id
            for fixture in fixtures
        ]

        original_history_ids = [
            match.match_id
            for match in history
        ]

        build_daily_report_output(
            fixtures,
            history,
            self.as_of,
        )

        self.assertEqual(
            [
                fixture.match_id
                for fixture in fixtures
            ],
            original_fixture_ids,
        )

        self.assertEqual(
            [
                match.match_id
                for match in history
            ],
            original_history_ids,
        )

    def test_naive_as_of_is_rejected(self):
        naive_as_of = datetime(
            2026,
            9,
            25,
            10,
            0,
        )

        with self.assertRaises(ValueError):
            build_daily_report_output(
                self._fixtures(),
                self._history(),
                naive_as_of,
            )

    def test_invalid_fixture_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
                "not-a-list",
                self._history(),
                self.as_of,
            )

    def test_invalid_history_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
                self._fixtures(),
                "not-a-list",
                self.as_of,
            )


if __name__ == "__main__":
    unittest.main()
```

The original final-system test was also still expecting the old four names and old mapping.

### 3. Do **not** change `test_daily_ticket_validation.py`

Your current `test_daily_ticket_validation.py` at commit `44050f7` is already correctly configured for:

```text
IRONCLAD   40%
BALANCED   30%
VOLATILITY 20%
BENCHMARK  10%
```

It also already includes `selected_odds` in the normal candidates.

### 4. Commit and push

Run:

```bash
git add tests/test_market_portfolio.py tests/test_final_daily_system.py
git commit -m "Align portfolio tests with ticket naming"
git push
```

Then GitHub Actions should run again.

### Important: don't fix `selected_odds` yet

Your #70 run also reports:

```text
test_missing_selected_odds_is_rejected
AssertionError: ValueError not raised
```

That is a **separate engine validation issue**. The current `engine.py` deliberately allows ordinary numeric `"odds"` as a fallback when `"selected_odds"` is absent.

So for this step, **leave that alone**. We're isolating the naming/configuration change first, exactly as requested.

After this push, send me the next Actions result. Then we'll fix the `selected_odds` contract without mixing another change into the ticket naming fix.
