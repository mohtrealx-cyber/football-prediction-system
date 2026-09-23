import unittest

from portfolio.engine import build_smart_portfolio


class PortfolioEngineTests(unittest.TestCase):

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

    def test_four_tickets_are_created_when_enough_candidates_exist(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            [ticket.name for ticket in tickets],
            [
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            ],
        )

    def test_stake_allocation_is_40_30_20_10(self):
        tickets = build_smart_portfolio(self.candidates)

        self.assertEqual(
            [ticket.stake_percent for ticket in tickets],
            [40.0, 30.0, 20.0, 10.0],
        )

    def test_every_ticket_has_at_least_three_matches(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_no_ticket_has_more_than_six_matches(self):
        tickets = build_smart_portfolio(self.candidates)

        for ticket in tickets:
            self.assertLessEqual(
                len(ticket.selections),
                6,
            )

    def test_match_can_appear_in_at_most_two_tickets(self):
        tickets = build_smart_portfolio(self.candidates)

        usage = {}

        for ticket in tickets:
            for selection in ticket.selections:
                usage[selection.match_id] = (
                    usage.get(selection.match_id, 0) + 1
                )

        self.assertTrue(
            all(count <= 2 for count in usage.values())
        )

    def test_same_match_is_not_duplicated_inside_one_ticket(self):
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

    def test_no_forced_ticket_when_too_few_candidates(self):
        tickets = build_smart_portfolio(
            self.candidates[:2]
        )

        self.assertEqual(tickets, [])

    def test_missing_candidate_field_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "model_probability": 0.88,
                "score": 88.0,
                # value_edge missing
            }
        ]

        with self.assertRaises(ValueError):
            build_smart_portfolio(bad_candidates)

    def test_candidates_from_same_match_are_not_duplicated(self):
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


if __name__ == "__main__":
    unittest.main()
