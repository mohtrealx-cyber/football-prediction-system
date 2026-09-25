import unittest
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch
from backtesting.multi_ticket import backtest_four_tickets


class MultiTicketBacktestTests(unittest.TestCase):

    def setUp(self):
        self.match1 = HistoricalMatch(
            match_id="M1",
            home_team="Team A",
            away_team="Team B",
            league="Test League",
            kickoff=datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc),
            home_goals=2,
            away_goals=0,
            odds={
                "home_win": 1.50,
                "draw": 4.00,
                "away_win": 6.00,
            },
        )

        self.match2 = HistoricalMatch(
            match_id="M2",
            home_team="Team C",
            away_team="Team D",
            league="Test League",
            kickoff=datetime(2026, 1, 2, 15, 0, tzinfo=timezone.utc),
            home_goals=1,
            away_goals=1,
            odds={
                "home_win": 2.00,
                "draw": 3.20,
                "away_win": 3.50,
            },
        )

        self.match3 = HistoricalMatch(
            match_id="M3",
            home_team="Team E",
            away_team="Team F",
            league="Test League",
            kickoff=datetime(2026, 1, 3, 15, 0, tzinfo=timezone.utc),
            home_goals=0,
            away_goals=2,
            odds={
                "home_win": 3.50,
                "draw": 3.20,
                "away_win": 2.00,
            },
        )

        self.match4 = HistoricalMatch(
            match_id="M4",
            home_team="Team G",
            away_team="Team H",
            league="Test League",
            kickoff=datetime(2026, 1, 4, 15, 0, tzinfo=timezone.utc),
            home_goals=3,
            away_goals=1,
            odds={
                "home_win": 1.70,
                "draw": 3.60,
                "away_win": 5.00,
            },
        )

    def make_selection(self, match, market, odds):
        return {
            "match": match,
            "market": market,
            "odds": odds,
        }

    def make_ticket(self, name, selections, stake):
        return {
            "ticket_name": name,
            "selections": selections,
            "stake": stake,
        }

    def make_four_tickets(self):
        return [
            self.make_ticket(
                "SAFE",
                [
                    self.make_selection(self.match1, "home_win", 1.50),
                    self.make_selection(self.match2, "draw", 3.20),
                    self.make_selection(self.match4, "home_win", 1.70),
                ],
                40,
            ),
            self.make_ticket(
                "BALANCED",
                [
                    self.make_selection(self.match1, "home_win", 1.50),
                    self.make_selection(self.match3, "away_win", 2.00),
                    self.make_selection(self.match4, "home_win", 1.70),
                ],
                30,
            ),
            self.make_ticket(
                "AGGRESSIVE",
                [
                    self.make_selection(self.match2, "home_win", 2.00),
                    self.make_selection(self.match3, "away_win", 2.00),
                    self.make_selection(self.match4, "home_win", 1.70),
                ],
                20,
            ),
            self.make_ticket(
                "VALUE",
                [
                    self.make_selection(self.match1, "home_win", 1.50),
                    self.make_selection(self.match2, "draw", 3.20),
                    self.make_selection(self.match3, "away_win", 2.00),
                ],
                10,
            ),
        ]

    def test_returns_dictionary(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertIsInstance(result, dict)

    def test_four_tickets_are_evaluated(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertEqual(result["total_tickets"], 4)

    def test_all_required_ticket_names_are_preserved(self):
        result = backtest_four_tickets(self.make_four_tickets())

        expected_names = {
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        }

        self.assertEqual(
            set(result["ticket_breakdown"].keys()),
            expected_names,
        )

    def test_ticket_results_are_settled(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertIn("won", result["ticket_breakdown"]["SAFE"])
        self.assertIn("won", result["ticket_breakdown"]["BALANCED"])
        self.assertIn("won", result["ticket_breakdown"]["AGGRESSIVE"])
        self.assertIn("won", result["ticket_breakdown"]["VALUE"])

    def test_portfolio_stake_is_total_of_all_four_tickets(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertEqual(result["total_stake"], 100.0)

    def test_ticket_stakes_are_preserved(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertEqual(
            result["ticket_breakdown"]["SAFE"]["stake"],
            40.0,
        )
        self.assertEqual(
            result["ticket_breakdown"]["BALANCED"]["stake"],
            30.0,
        )
        self.assertEqual(
            result["ticket_breakdown"]["AGGRESSIVE"]["stake"],
            20.0,
        )
        self.assertEqual(
            result["ticket_breakdown"]["VALUE"]["stake"],
            10.0,
        )

    def test_winning_ticket_is_identified(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertTrue(
            result["ticket_breakdown"]["SAFE"]["won"]
        )

    def test_losing_ticket_is_identified(self):
        result = backtest_four_tickets(self.make_four_tickets())

        self.assertFalse(
            result["ticket_breakdown"]["AGGRESSIVE"]["won"]
        )

    def test_duplicate_ticket_name_is_rejected(self):
        tickets = self.make_four_tickets()
        tickets[1]["ticket_name"] = "SAFE"

        with self.assertRaises(ValueError):
            backtest_four_tickets(tickets)

    def test_missing_ticket_name_is_rejected(self):
        tickets = self.make_four_tickets()
        del tickets[0]["ticket_name"]

        with self.assertRaises(ValueError):
            backtest_four_tickets(tickets)

    def test_missing_selections_are_rejected(self):
        tickets = self.make_four_tickets()
        del tickets[0]["selections"]

        with self.assertRaises(ValueError):
            backtest_four_tickets(tickets)

    def test_missing_stake_is_rejected(self):
        tickets = self.make_four_tickets()
        del tickets[0]["stake"]

        with self.assertRaises(ValueError):
            backtest_four_tickets(tickets)

    def test_invalid_ticket_list_is_rejected(self):
        with self.assertRaises(TypeError):
            backtest_four_tickets("not a list")

    def test_invalid_ticket_item_is_rejected(self):
        tickets = self.make_four_tickets()
        tickets[0] = "invalid ticket"

        with self.assertRaises(TypeError):
            backtest_four_tickets(tickets)

    def test_fewer_than_four_tickets_are_rejected(self):
        tickets = self.make_four_tickets()[:3]

        with self.assertRaises(ValueError):
            backtest_four_tickets(tickets)


if __name__ == "__main__":
    unittest.main()
