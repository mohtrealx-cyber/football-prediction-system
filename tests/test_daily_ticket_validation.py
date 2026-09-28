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
                "selection": "1X",
            },
            {
                "match_id": "M2",
                "home_team": "Barcelona",
                "away_team": "Valencia",
                "market": "HOME",
                "odds": 1.50,
                "selected_odds": 1.50,
                "model_probability": 0.84,
                "value_edge": 7.1,
                "score": 84.0,
                "selection": "HOME",
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
                "selection": "DNB",
            },
            {
                "match_id": "M4",
                "home_team": "Milan",
                "away_team": "Lazio",
                "market": "OVER_1_5",
                "odds": 1.30,
                "selected_odds": 1.30,
                "model_probability": 0.78,
                "value_edge": 6.9,
                "score": 78.0,
                "selection": "OVER_1_5",
            },
            {
                "match_id": "M5",
                "home_team": "Dortmund",
                "away_team": "Mainz",
                "market": "HOME",
                "odds": 1.60,
                "selected_odds": 1.60,
                "model_probability": 0.74,
                "value_edge": 9.4,
                "score": 74.0,
                "selection": "HOME",
            },
            {
                "match_id": "M6",
                "home_team": "PSG",
                "away_team": "Lille",
                "market": "OVER_1_5",
                "odds": 1.28,
                "selected_odds": 1.28,
                "model_probability": 0.69,
                "value_edge": 4.2,
                "score": 69.0,
                "selection": "OVER_1_5",
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
                "selection": "1X",
            },
            {
                "match_id": "M8",
                "home_team": "Ajax",
                "away_team": "Utrecht",
                "market": "OVER_2_5",
                "odds": 1.72,
                "selected_odds": 1.72,
                "model_probability": 0.61,
                "value_edge": 10.3,
                "score": 61.0,
                "selection": "OVER_2_5",
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
                "selection": "1X",
            },
            {
                "match_id": "M10",
                "home_team": "Napoli",
                "away_team": "Roma",
                "market": "OVER_1_5",
                "odds": 1.42,
                "selected_odds": 1.42,
                "model_probability": 0.71,
                "value_edge": 7.0,
                "score": 71.0,
                "selection": "OVER_1_5",
            },
            {
                "match_id": "M11",
                "home_team": "Liverpool",
                "away_team": "Everton",
                "market": "1X",
                "odds": 1.31,
                "selected_odds": 1.31,
                "model_probability": 0.81,
                "value_edge": 7.5,
                "score": 81.0,
                "selection": "1X",
            },
            {
                "match_id": "M12",
                "home_team": "Real Madrid",
                "away_team": "Getafe",
                "market": "HOME",
                "odds": 1.45,
                "selected_odds": 1.45,
                "model_probability": 0.80,
                "value_edge": 8.0,
                "score": 80.0,
                "selection": "HOME",
            },
        ]

    # ------------------------------------------------------------------
    # BASIC PORTFOLIO STRUCTURE
    # ------------------------------------------------------------------

    def test_four_daily_tickets_are_created(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(len(tickets), 4)

    def test_ticket_names_are_correct(self):
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

    def test_ticket_stakes_are_40_30_20_10(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            [ticket.stake_percent for ticket in tickets],
            [40.0, 30.0, 20.0, 10.0],
        )

    def test_stakes_are_in_correct_order(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertGreater(
            tickets[0].stake_percent,
            tickets[1].stake_percent,
        )

        self.assertGreater(
            tickets[1].stake_percent,
            tickets[2].stake_percent,
        )

        self.assertGreater(
            tickets[2].stake_percent,
            tickets[3].stake_percent,
        )

    def test_total_stake_allocation_is_100_percent(self):
        tickets = build_smart_portfolio(self.candidates)

        total = sum(
            ticket.stake_percent
            for ticket in tickets
        )

        self.assertEqual(total, 100.0)

    def test_safe_has_largest_stake(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            tickets[0].name,
            "IRONCLAD",
        )

        self.assertEqual(
            tickets[0].stake_percent,
            40.0,
        )

    def test_value_has_smallest_stake(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            tickets[-1].name,
            "BENCHMARK",
        )

        self.assertEqual(
            tickets[-1].stake_percent,
            10.0,
        )

    # ------------------------------------------------------------------
    # TICKET SIZE VALIDATION
    # ------------------------------------------------------------------

    def test_each_ticket_has_at_least_three_matches(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_each_ticket_has_no_more_than_six_matches(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            self.assertLessEqual(
                len(ticket.selections),
                6,
            )

    def test_no_portfolio_when_too_few_candidates(self):
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
    # MATCH REUSE / DUPLICATION
    # ------------------------------------------------------------------

    def test_match_is_used_in_at_most_two_tickets(self):
        tickets = build_smart_portfolio(self.candidates)

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

    def test_no_match_is_duplicated_inside_a_ticket(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            match_ids = [
                selection.match_id
                for selection in ticket.selections
            ]

            self.assertEqual(
                len(match_ids),
                len(set(match_ids)),
            )

    def test_match_reuse_above_two_tickets_is_rejected(self):
        tickets = build_smart_portfolio(self.candidates)

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

    # ------------------------------------------------------------------
    # SELECTION VALIDATION
    # ------------------------------------------------------------------

    def test_every_selection_has_required_fields(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            for selection in ticket.selections:

                self.assertTrue(
                    hasattr(selection, "match_id")
                )

                self.assertTrue(
                    hasattr(selection, "match")
                )

                self.assertTrue(
                    hasattr(selection, "market")
                )

                self.assertTrue(
                    hasattr(selection, "odds")
                )

                self.assertTrue(
                    hasattr(selection, "confidence")
                )

                self.assertTrue(
                    hasattr(selection, "value_edge")
                )

                self.assertIsNotNone(
                    selection.match_id
                )

                self.assertIsNotNone(
                    selection.match
                )

                self.assertIsNotNone(
                    selection.market
                )

                self.assertIsNotNone(
                    selection.odds
                )

    def test_selected_odds_is_supported(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertGreater(
                    selection.odds,
                    0,
                )

    # ------------------------------------------------------------------
    # CANDIDATE VALIDATION
    # ------------------------------------------------------------------

    def test_candidates_must_be_a_list(self):
        with self.assertRaises(TypeError):
            build_smart_portfolio(
                None
            )

    def test_candidate_must_be_a_dictionary(self):
        with self.assertRaises(TypeError):
            build_smart_portfolio(
                [
                    "invalid candidate",
                ]
            )

    def test_missing_odds_is_rejected(self):
        bad_candidates = [
            dict(
                self.candidates[0],
                odds=None,
                selected_odds=None,
            )
        ]

        with self.assertRaises(
            (ValueError, TypeError)
        ):
            build_smart_portfolio(
                bad_candidates
            )

    def test_zero_odds_are_rejected(self):
        bad_candidates = [
            dict(
                self.candidates[0],
                odds=0,
                selected_odds=0,
            )
        ]

        with self.assertRaises(
            (ValueError, TypeError)
        ):
            build_smart_portfolio(
                bad_candidates
            )

    def test_negative_odds_are_rejected(self):
        bad_candidates = [
            dict(
                self.candidates[0],
                odds=-1.5,
                selected_odds=-1.5,
            )
        ]

        with self.assertRaises(
            (ValueError, TypeError)
        ):
            build_smart_portfolio(
                bad_candidates
            )

    def test_missing_value_edge_is_rejected(self):
        bad_candidate = dict(
            self.candidates[0]
        )

        bad_candidate.pop(
            "value_edge",
            None,
        )

        with self.assertRaises(
            (ValueError, TypeError)
        ):
            build_smart_portfolio(
                [bad_candidate]
            )

    # ------------------------------------------------------------------
    # CANDIDATE DUPLICATION
    # ------------------------------------------------------------------

    def test_candidates_from_same_match_are_not_duplicated(self):
        duplicate_candidates = [
            self.candidates[0],
            {
                **self.candidates[0],
                "market": "OVER_1_5",
                "selection": "OVER_1_5",
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
            )

    # ------------------------------------------------------------------
    # INPUT IMMUTABILITY
    # ------------------------------------------------------------------

    def test_input_candidates_are_not_modified(self):
        original = [
            dict(candidate)
            for candidate in self.candidates
        ]

        build_smart_portfolio(
            self.candidates
        )

        self.assertEqual(
            self.candidates,
            original,
        )


if __name__ == "__main__":
    unittest.main()
