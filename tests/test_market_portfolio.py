import unittest

from portfolio.engine import (
    TICKET_ORDER,
    TICKET_SPECS,
    build_market_portfolio,
    build_smart_portfolio,
)


class TestMarketPortfolio(unittest.TestCase):

    def setUp(self):
        self.candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "model_probability": 0.88,
                "value_edge": 8.2,
                "score": 88.0,
            },
            {
                "match_id": "M2",
                "home_team": "Barcelona",
                "away_team": "Valencia",
                "market": "Home Win",
                "odds": 1.50,
                "model_probability": 0.84,
                "value_edge": 7.1,
                "score": 84.0,
            },
            {
                "match_id": "M3",
                "home_team": "Inter",
                "away_team": "Torino",
                "market": "DNB",
                "odds": 1.40,
                "model_probability": 0.82,
                "value_edge": 5.8,
                "score": 82.0,
            },
            {
                "match_id": "M4",
                "home_team": "Milan",
                "away_team": "Lazio",
                "market": "Over 1.5",
                "odds": 1.30,
                "model_probability": 0.78,
                "value_edge": 6.9,
                "score": 78.0,
            },
            {
                "match_id": "M5",
                "home_team": "Dortmund",
                "away_team": "Mainz",
                "market": "Home Win",
                "odds": 1.60,
                "model_probability": 0.74,
                "value_edge": 9.4,
                "score": 74.0,
            },
            {
                "match_id": "M6",
                "home_team": "PSG",
                "away_team": "Lille",
                "market": "Over 1.5",
                "odds": 1.28,
                "model_probability": 0.69,
                "value_edge": 4.2,
                "score": 69.0,
            },
            {
                "match_id": "M7",
                "home_team": "Porto",
                "away_team": "Braga",
                "market": "1X",
                "odds": 1.37,
                "model_probability": 0.65,
                "value_edge": 7.8,
                "score": 65.0,
            },
            {
                "match_id": "M8",
                "home_team": "Ajax",
                "away_team": "Utrecht",
                "market": "Over 2.5",
                "odds": 1.72,
                "model_probability": 0.61,
                "value_edge": 10.3,
                "score": 61.0,
            },
            {
                "match_id": "M9",
                "home_team": "Benfica",
                "away_team": "Braga",
                "market": "1X",
                "odds": 1.32,
                "model_probability": 0.72,
                "value_edge": 6.5,
                "score": 72.0,
            },
            {
                "match_id": "M10",
                "home_team": "Napoli",
                "away_team": "Roma",
                "market": "Over 1.5",
                "odds": 1.42,
                "model_probability": 0.71,
                "value_edge": 7.0,
                "score": 71.0,
            },
        ]

    # ========================================================================
    # BASIC PORTFOLIO CREATION
    # ========================================================================

    def test_four_tickets_are_created_when_enough_candidates_exist(self):
        tickets = build_market_portfolio(self.candidates)

        self.assertEqual(len(tickets), 4)

        self.assertEqual(
            [ticket.name for ticket in tickets],
            [
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            ],
        )

    def test_build_smart_portfolio_uses_same_strategy(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            [ticket.name for ticket in tickets],
            [
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            ],
        )

    # ========================================================================
    # TICKET NAMES
    # ========================================================================

    def test_portfolio_has_expected_ticket_names(self):
        tickets = build_market_portfolio(self.candidates)

        ticket_names = {
            ticket.name
            for ticket in tickets
        }

        self.assertIn("IRONCLAD", ticket_names)
        self.assertIn("BALANCED", ticket_names)
        self.assertIn("VOLATILITY", ticket_names)
        self.assertIn("BENCHMARK", ticket_names)

    def test_ticket_order_matches_strategy(self):
        tickets = build_market_portfolio(self.candidates)

        self.assertEqual(
            [ticket.name for ticket in tickets],
            list(TICKET_ORDER),
        )

    # ========================================================================
    # STAKE ALLOCATION
    # ========================================================================

    def test_ticket_stakes_are_40_30_20_10(self):
        tickets = build_market_portfolio(self.candidates)

        stakes = {
            ticket.name: ticket.stake_percent
            for ticket in tickets
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

    def test_stakes_are_40_30_20_10_in_order(self):
        tickets = build_market_portfolio(self.candidates)

        self.assertEqual(
            [ticket.stake_percent for ticket in tickets],
            [40.0, 30.0, 20.0, 10.0],
        )

    def test_total_stake_is_100_percent(self):
        tickets = build_market_portfolio(self.candidates)

        total_stake = sum(
            ticket.stake_percent
            for ticket in tickets
        )

        self.assertEqual(total_stake, 100.0)

    # ========================================================================
    # TICKET CONFIGURATION
    # ========================================================================

    def test_ticket_specs_match_strategy(self):
        self.assertEqual(
            TICKET_SPECS["IRONCLAD"]["stake_percent"],
            40.0,
        )

        self.assertEqual(
            TICKET_SPECS["BALANCED"]["stake_percent"],
            30.0,
        )

        self.assertEqual(
            TICKET_SPECS["VOLATILITY"]["stake_percent"],
            20.0,
        )

        self.assertEqual(
            TICKET_SPECS["BENCHMARK"]["stake_percent"],
            10.0,
        )

    def test_ironclad_maximum_is_four_matches(self):
        self.assertEqual(
            TICKET_SPECS["IRONCLAD"]["max_matches"],
            4,
        )

    def test_balanced_maximum_is_five_matches(self):
        self.assertEqual(
            TICKET_SPECS["BALANCED"]["max_matches"],
            5,
        )

    def test_volatility_maximum_is_six_matches(self):
        self.assertEqual(
            TICKET_SPECS["VOLATILITY"]["max_matches"],
            6,
        )

    def test_benchmark_maximum_is_five_matches(self):
        self.assertEqual(
            TICKET_SPECS["BENCHMARK"]["max_matches"],
            5,
        )

    # ========================================================================
    # MINIMUM / MAXIMUM SELECTIONS
    # ========================================================================

    def test_each_created_ticket_has_at_least_three_matches(self):
        tickets = build_market_portfolio(self.candidates)

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_ironclad_has_no_more_than_four_matches(self):
        tickets = build_market_portfolio(self.candidates)

        ironclad = next(
            ticket
            for ticket in tickets
            if ticket.name == "IRONCLAD"
        )

        self.assertLessEqual(
            len(ironclad.selections),
            4,
        )

    def test_balanced_has_no_more_than_five_matches(self):
        tickets = build_market_portfolio(self.candidates)

        balanced = next(
            ticket
            for ticket in tickets
            if ticket.name == "BALANCED"
        )

        self.assertLessEqual(
            len(balanced.selections),
            5,
        )

    def test_volatility_has_no_more_than_six_matches(self):
        tickets = build_market_portfolio(self.candidates)

        volatility = next(
            ticket
            for ticket in tickets
            if ticket.name == "VOLATILITY"
        )

        self.assertLessEqual(
            len(volatility.selections),
            6,
        )

    def test_benchmark_has_no_more_than_five_matches(self):
        tickets = build_market_portfolio(self.candidates)

        benchmark = next(
            ticket
            for ticket in tickets
            if ticket.name == "BENCHMARK"
        )

        self.assertLessEqual(
            len(benchmark.selections),
            5,
        )

    # ========================================================================
    # MATCH DUPLICATION
    # ========================================================================

    def test_no_duplicate_matches_inside_one_ticket(self):
        tickets = build_market_portfolio(self.candidates)

        for ticket in tickets:
            match_ids = [
                selection.match_id
                for selection in ticket.selections
            ]

            self.assertEqual(
                len(match_ids),
                len(set(match_ids)),
            )

    def test_match_reuse_limit_is_respected(self):
        tickets = build_market_portfolio(self.candidates)

        usage = {}

        for ticket in tickets:
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

    def test_match_can_appear_in_at_most_two_tickets(self):
        tickets = build_market_portfolio(self.candidates)

        usage = {}

        for ticket in tickets:
            for selection in ticket.selections:
                usage[selection.match_id] = (
                    usage.get(selection.match_id, 0) + 1
                )

        self.assertTrue(
            all(
                count <= 2
                for count in usage.values()
            )
        )

    # ========================================================================
    # DUPLICATE CANDIDATES
    # ========================================================================

    def test_candidates_from_same_match_are_not_duplicated_inside_ticket(self):
        duplicate_candidates = [
            self.candidates[0],
            {
                **self.candidates[0],
                "market": "Over 1.5",
                "odds": 1.40,
                "value_edge": 6.0,
                "score": 70.0,
            },
            *self.candidates[1:],
        ]

        tickets = build_market_portfolio(
            duplicate_candidates
        )

        for ticket in tickets:
            match_ids = [
                selection.match_id
                for selection in ticket.selections
            ]

            self.assertEqual(
                len(match_ids),
                len(set(match_ids)),
            )

    # ========================================================================
    # INSUFFICIENT CANDIDATES
    # ========================================================================

    def test_no_portfolio_when_fewer_than_three_candidates(self):
        tickets = build_market_portfolio(
            self.candidates[:2]
        )

        self.assertEqual(
            tickets,
            [],
        )

    def test_empty_candidates_return_empty_portfolio(self):
        tickets = build_market_portfolio([])

        self.assertEqual(
            tickets,
            [],
        )

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def test_missing_value_edge_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "model_probability": 0.88,
                "score": 88.0,
            }
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    def test_missing_match_id_is_rejected(self):
        bad_candidates = [
            {
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "model_probability": 0.88,
                "value_edge": 8.2,
                "score": 88.0,
            }
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    def test_missing_market_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "odds": 1.35,
                "model_probability": 0.88,
                "value_edge": 8.2,
                "score": 88.0,
            }
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    def test_missing_odds_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "model_probability": 0.88,
                "value_edge": 8.2,
                "score": 88.0,
            }
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    def test_invalid_candidate_type_is_rejected(self):
        with self.assertRaises(TypeError):
            build_market_portfolio(
                ["not a dictionary"]
            )

    def test_invalid_candidates_container_is_rejected(self):
        with self.assertRaises(TypeError):
            build_market_portfolio(
                ("invalid",)
            )

    # ========================================================================
    # ODDS VALIDATION
    # ========================================================================

    def test_odds_must_be_greater_than_one(self):
        bad_candidates = [
            {
                **self.candidates[0],
                "odds": 1.0,
            },
            *self.candidates[1:],
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    def test_zero_odds_are_rejected(self):
        bad_candidates = [
            {
                **self.candidates[0],
                "odds": 0,
            },
            *self.candidates[1:],
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    # ========================================================================
    # VALUE EDGE VALIDATION
    # ========================================================================

    def test_negative_value_edge_is_rejected(self):
        bad_candidates = [
            {
                **self.candidates[0],
                "value_edge": -1.0,
            },
            *self.candidates[1:],
        ]

        with self.assertRaises(ValueError):
            build_market_portfolio(
                bad_candidates
            )

    # ========================================================================
    # PORTFOLIO IMMUTABILITY
    # ========================================================================

    def test_input_candidates_are_not_mutated(self):
        original = [
            dict(candidate)
            for candidate in self.candidates
        ]

        build_market_portfolio(
            self.candidates
        )

        self.assertEqual(
            self.candidates,
            original,
        )

    # ========================================================================
    # SELECTION STRUCTURE
    # ========================================================================

    def test_every_selection_has_match_id(self):
        tickets = build_market_portfolio(
            self.candidates
        )

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertTrue(
                    selection.match_id
                )

    def test_every_selection_has_market(self):
        tickets = build_market_portfolio(
            self.candidates
        )

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertTrue(
                    selection.market
                )

    def test_every_selection_has_valid_odds(self):
        tickets = build_market_portfolio(
            self.candidates
        )

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertGreater(
                    selection.odds,
                    1.0,
                )

    def test_every_selection_has_valid_confidence(self):
        tickets = build_market_portfolio(
            self.candidates
        )

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertGreaterEqual(
                    selection.confidence,
                    0.0,
                )

                self.assertLessEqual(
                    selection.confidence,
                    100.0,
                )

    # ========================================================================
    # DETERMINISM
    # ========================================================================

    def test_same_input_produces_same_ticket_names(self):
        first = build_market_portfolio(
            self.candidates
        )

        second = build_market_portfolio(
            self.candidates
        )

        self.assertEqual(
            [ticket.name for ticket in first],
            [ticket.name for ticket in second],
        )

    def test_same_input_produces_same_stakes(self):
        first = build_market_portfolio(
            self.candidates
        )

        second = build_market_portfolio(
            self.candidates
        )

        self.assertEqual(
            [ticket.stake_percent for ticket in first],
            [ticket.stake_percent for ticket in second],
        )


if __name__ == "__main__":
    unittest.main()
