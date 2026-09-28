import unittest

from portfolio.engine import build_smart_portfolio


class DailyTicketValidationTests(unittest.TestCase):
    """
    Validate the daily four-ticket portfolio structure.

    Portfolio allocation:

        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%
    """

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

    # ========================================================
    # TICKET NAMES
    # ========================================================

    def test_ticket_names_are_correct(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        self.assertEqual(
            [ticket.name for ticket in tickets],
            [
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            ],
        )

    # ========================================================
    # STAKE ALLOCATION
    # ========================================================

    def test_ticket_stakes_are_40_30_20_10(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        self.assertEqual(
            {
                ticket.name: ticket.stake_percent
                for ticket in tickets
            },
            {
                "SAFE": 40.0,
                "BALANCED": 30.0,
                "AGGRESSIVE": 20.0,
                "VALUE": 10.0,
            },
        )

    def test_total_stake_allocation_is_100_percent(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        total_stake = sum(
            ticket.stake_percent
            for ticket in tickets
        )

        self.assertEqual(
            total_stake,
            100.0,
        )

    # ========================================================
    # FOUR TICKETS
    # ========================================================

    def test_four_daily_tickets_are_created(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        self.assertEqual(
            len(tickets),
            4,
        )

    # ========================================================
    # MINIMUM SELECTIONS
    # ========================================================

    def test_each_ticket_has_at_least_three_matches(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
                msg=(
                    f"{ticket.name} has fewer than "
                    "3 selections"
                ),
            )

    # ========================================================
    # MAXIMUM SELECTIONS
    # ========================================================

    def test_each_ticket_has_no_more_than_six_matches(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        for ticket in tickets:
            self.assertLessEqual(
                len(ticket.selections),
                6,
                msg=(
                    f"{ticket.name} has more than "
                    "6 selections"
                ),
            )

    # ========================================================
    # NO DUPLICATE MATCH INSIDE TICKET
    # ========================================================

    def test_no_match_is_duplicated_inside_a_ticket(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        for ticket in tickets:
            match_ids = [
                selection.match_id
                for selection in ticket.selections
            ]

            self.assertEqual(
                len(match_ids),
                len(set(match_ids)),
                msg=(
                    f"Duplicate match found in "
                    f"{ticket.name}"
                ),
            )

    # ========================================================
    # MATCH REUSE LIMIT
    # ========================================================

    def test_match_is_used_in_at_most_two_tickets(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        usage = {}

        for ticket in tickets:
            for selection in ticket.selections:
                usage[selection.match_id] = (
                    usage.get(selection.match_id, 0)
                    + 1
                )

        for match_id, count in usage.items():
            self.assertLessEqual(
                count,
                2,
                msg=(
                    f"{match_id} appears in "
                    f"{count} tickets"
                ),
            )

    # ========================================================
    # VALID STAKE ORDER
    # ========================================================

    def test_stakes_are_in_correct_order(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        self.assertEqual(
            [ticket.stake_percent for ticket in tickets],
            [
                40.0,
                30.0,
                20.0,
                10.0,
            ],
        )

    # ========================================================
    # SAFE IS THE LARGEST ALLOCATION
    # ========================================================

    def test_safe_has_largest_stake(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        safe = next(
            ticket
            for ticket in tickets
            if ticket.name == "SAFE"
        )

        for ticket in tickets:
            self.assertGreaterEqual(
                safe.stake_percent,
                ticket.stake_percent,
            )

    # ========================================================
    # VALUE IS THE SMALLEST ALLOCATION
    # ========================================================

    def test_value_has_smallest_stake(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        value = next(
            ticket
            for ticket in tickets
            if ticket.name == "VALUE"
        )

        for ticket in tickets:
            self.assertLessEqual(
                value.stake_percent,
                ticket.stake_percent,
            )

    # ========================================================
    # EVERY SELECTION HAS REQUIRED DATA
    # ========================================================

    def test_every_selection_has_required_fields(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        for ticket in tickets:
            for selection in ticket.selections:

                self.assertTrue(
                    selection.match_id
                )

                self.assertTrue(
                    selection.home_team
                )

                self.assertTrue(
                    selection.away_team
                )

                self.assertTrue(
                    selection.market
                )

                self.assertGreater(
                    selection.odds,
                    0,
                )

                self.assertGreaterEqual(
                    selection.model_probability,
                    0,
                )

                self.assertGreaterEqual(
                    selection.value_edge,
                    0,
                )

                self.assertGreaterEqual(
                    selection.score,
                    0,
                )

    # ========================================================
    # PORTFOLIO MUST NOT BE FORCED
    # ========================================================

    def test_no_portfolio_when_too_few_candidates(self):
        tickets = build_smart_portfolio(
            self.candidates[:2]
        )

        self.assertEqual(
            tickets,
            [],
        )

    # ========================================================
    # MISSING VALUE EDGE MUST FAIL
    # ========================================================

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
                # value_edge intentionally missing
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(
                bad_candidates
            )

    # ========================================================
    # MISSING ODDS MUST FAIL
    # ========================================================

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
                # odds intentionally missing
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(
                bad_candidates
            )

    # ========================================================
    # SELECTED_ODDS COMPATIBILITY
    # ========================================================

    def test_selected_odds_is_supported(self):
        candidates = [
            {
                **candidate,
                "selected_odds": candidate["odds"],
            }
            for candidate in self.candidates
        ]

        for candidate in candidates:
            candidate.pop("odds", None)

        tickets = build_smart_portfolio(
            candidates
        )

        self.assertEqual(
            len(tickets),
            4,
        )

    # ========================================================
    # ODDS MUST BE POSITIVE
    # ========================================================

    def test_zero_odds_are_rejected(self):
        bad_candidates = [
            {
                **self.candidates[0],
                "odds": 0,
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(
                bad_candidates
            )

    def test_negative_odds_are_rejected(self):
        bad_candidates = [
            {
                **self.candidates[0],
                "odds": -1.5,
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(
                bad_candidates
            )

    # ========================================================
    # EMPTY INPUT
    # ========================================================

    def test_empty_candidate_list_returns_empty_portfolio(self):
        tickets = build_smart_portfolio([])

        self.assertEqual(
            tickets,
            [],
        )

    # ========================================================
    # CANDIDATE TYPE VALIDATION
    # ========================================================

    def test_candidates_must_be_a_list(self):
        with self.assertRaises(ValueError):
            build_smart_portfolio(
                None
            )

    def test_candidate_must_be_a_dictionary(self):
        with self.assertRaises(ValueError):
            build_smart_portfolio(
                [
                    "invalid candidate"
                ]
            )


if __name__ == "__main__":
    unittest.main()
