import unittest

from tickets.assembler import build_four_tickets


class TicketAssemblerTests(unittest.TestCase):

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
            },
            {
                "match_id": "M2",
                "home_team": "Barcelona",
                "away_team": "Valencia",
                "market": "Home Win",
                "odds": 1.50,
                "model_probability": 0.84,
                "value_edge": 7.1,
            },
            {
                "match_id": "M3",
                "home_team": "Inter",
                "away_team": "Torino",
                "market": "DNB",
                "odds": 1.40,
                "model_probability": 0.82,
                "value_edge": 5.8,
            },
            {
                "match_id": "M4",
                "home_team": "Milan",
                "away_team": "Lazio",
                "market": "Over 1.5",
                "odds": 1.30,
                "model_probability": 0.78,
                "value_edge": 6.9,
            },
            {
                "match_id": "M5",
                "home_team": "Dortmund",
                "away_team": "Mainz",
                "market": "Home Win",
                "odds": 1.60,
                "model_probability": 0.74,
                "value_edge": 9.4,
            },
            {
                "match_id": "M6",
                "home_team": "PSG",
                "away_team": "Lille",
                "market": "Over 1.5",
                "odds": 1.28,
                "model_probability": 0.69,
                "value_edge": 4.2,
            },
            {
                "match_id": "M7",
                "home_team": "Porto",
                "away_team": "Braga",
                "market": "1X",
                "odds": 1.37,
                "model_probability": 0.65,
                "value_edge": 7.8,
            },
            {
                "match_id": "M8",
                "home_team": "Ajax",
                "away_team": "Utrecht",
                "market": "Over 2.5",
                "odds": 1.72,
                "model_probability": 0.61,
                "value_edge": 10.3,
            },
        ]

    def test_four_tickets_can_be_created(self):
        tickets = build_four_tickets(self.candidates)

        self.assertEqual(
            [ticket.name for ticket in tickets],
            [
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            ],
        )

    def test_four_ticket_stakes_are_correct(self):
        tickets = build_four_tickets(self.candidates)

        self.assertEqual(
            [ticket.stake_percent for ticket in tickets],
            [40.0, 30.0, 20.0, 10.0],
        )

    def test_each_ticket_has_at_least_three_matches(self):
        tickets = build_four_tickets(self.candidates)

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_ticket_one_uses_strongest_selections(self):
        tickets = build_four_tickets(self.candidates)

        safe_ticket = tickets[0]

        confidences = [
            selection.confidence
            for selection in safe_ticket.selections
        ]

        self.assertTrue(
            all(confidence >= 80.0 for confidence in confidences)
        )

    def test_missing_candidate_field_is_rejected(self):
        bad_candidates = [
            {
                "match_id": "M1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "market": "1X",
                "odds": 1.35,
                "model_probability": 0.88,
                # value_edge intentionally missing
            }
        ]

        with self.assertRaises(ValueError):
            build_four_tickets(bad_candidates)

    def test_tickets_use_candidate_matches(self):
        tickets = build_four_tickets(self.candidates)

        all_ticket_match_ids = []

        for ticket in tickets:
            for selection in ticket.selections:
                all_ticket_match_ids.append(selection.match_id)

        self.assertTrue(
            set(all_ticket_match_ids).issubset(
                {candidate["match_id"] for candidate in self.candidates}
            )
        )


if __name__ == "__main__":
    unittest.main()
