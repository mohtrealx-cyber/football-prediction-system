import unittest

from markets.full_pipeline import run_full_market_pipeline
from candidates.market_adapter import adapt_markets_to_candidates
from candidates.market_pool import build_market_candidate_pool
from portfolio.market_portfolio import build_market_portfolio


class TestEndToEnd(unittest.TestCase):

    def setUp(self):
        self.predictions = {
            "home_win": 0.70,
            "draw": 0.15,
            "away_win": 0.15,
            "over_2_5": 0.60,
            "under_2_5": 0.40,
            "btts_yes": 0.55,
            "btts_no": 0.45,
        }

        self.odds = {
            "home_win": 1.80,
            "draw": 4.50,
            "away_win": 5.00,
            "over_2_5": 1.90,
            "under_2_5": 2.20,
            "btts_yes": 2.00,
            "btts_no": 2.30,
        }

    def _build_all_match_candidates(self):
        candidates = []

        for index in range(12):
            match_id = f"match_{index + 1:03d}"

            scored_markets = run_full_market_pipeline(
                predictions=self.predictions,
                odds=self.odds,
            )

            match_candidates = adapt_markets_to_candidates(
                match_id=match_id,
                scored_markets=scored_markets,
            )

            for candidate in match_candidates:
                candidate["home_team"] = (
                    f"Home Team {index + 1}"
                )
                candidate["away_team"] = (
                    f"Away Team {index + 1}"
                )

            candidates.extend(match_candidates)

        return candidates

    def test_market_pipeline_produces_markets(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        self.assertEqual(
            len(results),
            7,
        )

    def test_market_results_become_candidates(self):
        candidates = self._build_all_match_candidates()

        self.assertEqual(
            len(candidates),
            84,
        )

    def test_candidate_pool_reduces_to_one_per_match(self):
        candidates = self._build_all_match_candidates()

        pool = build_market_candidate_pool(
            candidates,
        )

        self.assertEqual(
            len(pool),
            12,
        )

        match_ids = [
            candidate["match_id"]
            for candidate in pool
        ]

        self.assertEqual(
            len(match_ids),
            len(set(match_ids)),
        )

    def test_candidate_pool_contains_only_qualified_selections(self):
        candidates = self._build_all_match_candidates()

        pool = build_market_candidate_pool(
            candidates,
        )

        for candidate in pool:
            self.assertTrue(
                candidate["qualified"]
            )

    def test_full_chain_builds_four_tickets(self):
        candidates = self._build_all_match_candidates()

        pool = build_market_candidate_pool(
            candidates,
        )

        portfolio = build_market_portfolio(
            pool,
        )

        self.assertEqual(
            len(portfolio),
            4,
        )

    def test_each_ticket_has_at_least_three_selections(self):
        candidates = self._build_all_match_candidates()

        pool = build_market_candidate_pool(
            candidates,
        )

        portfolio = build_market_portfolio(
            pool,
        )

        for ticket in portfolio:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_match_reuse_limit_is_respected(self):
        candidates = self._build_all_match_candidates()

        pool = build_market_candidate_pool(
            candidates,
        )

        portfolio = build_market_portfolio(
            pool,
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


if __name__ == "__main__":
    unittest.main()
