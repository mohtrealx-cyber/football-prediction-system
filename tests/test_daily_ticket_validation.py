import copy
import unittest
from dataclasses import replace

from portfolio.market_portfolio import build_market_portfolio
from portfolio.daily_validator import validate_daily_portfolio


def make_candidate(
    index,
    score=90.0,
    qualified=True,
):
    return {
        "match_id": f"M{index}",
        "home_team": f"Home{index}",
        "away_team": f"Away{index}",
        "league": "Test League",
        "market": "home_win",
        "selection": "HOME",
        "qualified": qualified,
        "model_probability": 0.70,
        "odds": 1.80,
        "selected_odds": 1.80,
        "implied_probability": 1 / 1.80,
        "expected_value": 0.26,
        "value_edge": 14.44,
        "score": score,
    }


class DailyTicketValidationTests(unittest.TestCase):

    def test_valid_four_ticket_portfolio_passes(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        result = validate_daily_portfolio(
            portfolio
        )

        self.assertTrue(result)

    def test_four_ticket_structure_is_required(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        invalid_portfolio = portfolio[:3]

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                invalid_portfolio
            )

    def test_ticket_stakes_are_40_30_20_10(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        expected = {
            "SAFE": 40.0,
            "BALANCED": 30.0,
            "AGGRESSIVE": 20.0,
            "VALUE": 10.0,
        }

        actual = {
            ticket.name: ticket.stake_percent
            for ticket in portfolio
        }

        self.assertEqual(
            actual,
            expected,
        )

        self.assertTrue(
            validate_daily_portfolio(
                portfolio
            )
        )

    def test_ticket_cannot_have_duplicate_match(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        ticket = portfolio[0]

        ticket.selections.append(
            copy.deepcopy(
                ticket.selections[0]
            )
        )

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                portfolio
            )

    def test_match_reuse_above_two_tickets_is_rejected(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        reused_match = copy.deepcopy(
            portfolio[0].selections[0]
        )

        portfolio[1].selections.append(
            copy.deepcopy(reused_match)
        )

        portfolio[2].selections.append(
            copy.deepcopy(reused_match)
        )

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                portfolio
            )

    def test_ticket_with_one_selection_is_rejected(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        portfolio[0].selections = (
            portfolio[0].selections[:1]
        )

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                portfolio
            )

    def test_ticket_with_two_selections_is_rejected(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        portfolio[0].selections = (
            portfolio[0].selections[:2]
        )

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                portfolio
            )

    def test_ticket_with_more_than_six_selections_is_rejected(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        extra = copy.deepcopy(
            portfolio[0].selections
        )

        portfolio[0].selections.extend(
            extra[:4]
        )

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                portfolio
            )

    def test_empty_ticket_is_allowed_when_no_selection_exists(self):
        candidates = [
            make_candidate(index)
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        portfolio[0].selections = []

        result = validate_daily_portfolio(
            portfolio
        )

        self.assertTrue(result)

    def test_unqualified_selection_is_rejected(self):
        candidates = [
            make_candidate(
                index,
                qualified=True,
            )
            for index in range(1, 13)
        ]

        portfolio = build_market_portfolio(
            candidates
        )

        original_selection = (
            portfolio[0].selections[0]
        )

        unqualified_selection = replace(
            original_selection,
            qualified=False,
        )

        portfolio[0].selections[0] = (
            unqualified_selection
        )

        with self.assertRaises(ValueError):
            validate_daily_portfolio(
                portfolio
            )

    def test_non_list_portfolio_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_daily_portfolio(
                {}
            )


if __name__ == "__main__":
    unittest.main()
