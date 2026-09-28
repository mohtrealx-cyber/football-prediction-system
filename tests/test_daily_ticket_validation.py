import unittest

from portfolio.engine import build_smart_portfolio


class DailyTicketValidationTests(unittest.TestCase):

    def setUp(self):
        self.candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "selected_odds": 1.35,
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
                "selected_odds": 1.50,
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
                "selected_odds": 1.40,
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
                "selected_odds": 1.30,
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
                "selected_odds": 1.60,
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
                "selected_odds": 1.28,
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
                "selected_odds": 1.37,
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
                "selected_odds": 1.72,
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
                "selected_odds": 1.32,
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
                "selected_odds": 1.42,
                "model_probability": 0.71,
                "value_edge": 7.0,
                "score": 71.0,
            },
        ]

    # ------------------------------------------------------------------
    # TICKET NAMES
    # ------------------------------------------------------------------

    def test_ticket_names_are_correct(self):
        tickets = build_smart_portfolio(self.candidates)

        ticket_names = [
            ticket.name
            for ticket in tickets
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

    def test_all_four_ticket_types_exist(self):
        tickets = build_smart_portfolio(self.candidates)

        ticket_names = {
            ticket.name
            for ticket in tickets
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

    # ------------------------------------------------------------------
    # STAKE ALLOCATION
    # ------------------------------------------------------------------

    def test_ticket_stakes_are_40_30_20_10(self):
        tickets = build_smart_portfolio(self.candidates)

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

    def test_stake_percentages_sum_to_100(self):
        tickets = build_smart_portfolio(self.candidates)

        total_stake = sum(
            ticket.stake_percent
            for ticket in tickets
        )

        self.assertEqual(
            total_stake,
            100.0,
        )

    def test_ironclad_has_largest_stake(self):
        tickets = build_smart_portfolio(self.candidates)

        stakes = {
            ticket.name: ticket.stake_percent
            for ticket in tickets
        }

        self.assertEqual(
            stakes["IRONCLAD"],
            max(stakes.values()),
        )

    def test_benchmark_has_smallest_stake(self):
        tickets = build_smart_portfolio(self.candidates)

        stakes = {
            ticket.name: ticket.stake_percent
            for ticket in tickets
        }

        self.assertEqual(
            stakes["BENCHMARK"],
            min(stakes.values()),
        )

    def test_stake_order_is_40_30_20_10(self):
        tickets = build_smart_portfolio(self.candidates)

        stakes = [
            ticket.stake_percent
            for ticket in tickets
        ]

        self.assertEqual(
            stakes,
            [
                40.0,
                30.0,
                20.0,
                10.0,
            ],
        )

    # ------------------------------------------------------------------
    # MINIMUM / MAXIMUM SELECTION COUNTS
    # ------------------------------------------------------------------

    def test_every_ticket_has_at_least_three_matches(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            len(tickets),
            4,
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

    def test_no_ticket_has_more_than_six_matches(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            self.assertLessEqual(
                len(ticket.selections),
                6,
                msg=(
                    f"{ticket.name} has more than "
                    "6 selections"
                ),
            )

    # ------------------------------------------------------------------
    # MATCH REUSE
    # ------------------------------------------------------------------

    def test_match_can_appear_in_at_most_two_tickets(self):
        tickets = build_smart_portfolio(self.candidates)

        usage = {}

        for ticket in tickets:
            for selection in ticket.selections:
                match_id = selection.match_id

                usage[match_id] = (
                    usage.get(match_id, 0) + 1
                )

        for match_id, count in usage.items():
            self.assertLessEqual(
                count,
                2,
                msg=(
                    f"Match {match_id} appears in "
                    f"{count} tickets"
                ),
            )

    def test_same_match_is_not_duplicated_inside_ticket(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            match_ids = [
                selection.match_id
                for selection in ticket.selections
            ]

            self.assertEqual(
                len(match_ids),
                len(set(match_ids)),
                msg=(
                    f"{ticket.name} contains "
                    "the same match more than once"
                ),
            )

    # ------------------------------------------------------------------
    # EMPTY / INSUFFICIENT INPUT
    # ------------------------------------------------------------------

    def test_no_forced_ticket_when_too_few_candidates(self):
        tickets = build_smart_portfolio(
            self.candidates[:2]
        )

        self.assertEqual(
            tickets,
            [],
        )

    def test_empty_candidate_list_returns_empty_portfolio(self):
        tickets = build_smart_portfolio([])

        self.assertEqual(
            tickets,
            [],
        )

    # ------------------------------------------------------------------
    # REQUIRED CANDIDATE FIELDS
    # ------------------------------------------------------------------

    def test_missing_candidate_field_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "selected_odds": 1.35,
                "model_probability": 0.88,
                "score": 88.0,
                # value_edge intentionally missing
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(
                bad_candidates
            )

    def test_missing_selected_odds_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "model_probability": 0.88,
                "value_edge": 8.2,
                "score": 88.0,
                # selected_odds intentionally missing
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(
                bad_candidates
            )

    # ------------------------------------------------------------------
    # DUPLICATE CANDIDATES
    # ------------------------------------------------------------------

    def test_candidates_from_same_match_are_not_duplicated(self):
        duplicate_candidates = [
            self.candidates[0],
            {
                **self.candidates[0],
                "market": "Over 1.5",
                "odds": 1.40,
                "selected_odds": 1.40,
                "value_edge": 6.0,
                "score": 70.0,
            },
            *self.candidates[1:],
        ]

        tickets = build_smart_portfolio(
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
                msg=(
                    f"{ticket.name} contains "
                    "duplicate match IDs"
                ),
            )

    # ------------------------------------------------------------------
    # SELECTION DATA INTEGRITY
    # ------------------------------------------------------------------

    def test_all_selections_have_match_ids(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertTrue(
                    selection.match_id
                )

    def test_all_tickets_have_valid_stake_percent(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            self.assertGreater(
                ticket.stake_percent,
                0,
            )

            self.assertLessEqual(
                ticket.stake_percent,
                100,
            )

    def test_four_tickets_are_created_with_enough_candidates(self):
        tickets = build_smart_portfolio(
            self.candidates
        )

        self.assertEqual(
            len(tickets),
            4,
        )


if __name__ == "__main__":
    unittest.main()
