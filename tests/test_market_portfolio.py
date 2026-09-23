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

        self.assertIn("SAFE", ticket_names)
        self.assertIn("BALANCED", ticket_names)
        self.assertIn("AGGRESSIVE", ticket_names)
        self.assertIn("VALUE", ticket_names)

    def test_ticket_stake_allocations_are_correct(self):
        portfolio = build_market_portfolio(
            self.candidates,
        )

        stakes = {
            ticket.name: ticket.stake_percentage
            for ticket in portfolio
        }

        self.assertEqual(stakes["SAFE"], 40.0)
        self.assertEqual(stakes["BALANCED"], 30.0)
        self.assertEqual(stakes["AGGRESSIVE"], 20.0)
        self.assertEqual(stakes["VALUE"], 10.0)

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
                usage[match_id] = usage.get(match_id, 0) + 1

        for count in usage.values():
            self.assertLessEqual(count, 2)

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
