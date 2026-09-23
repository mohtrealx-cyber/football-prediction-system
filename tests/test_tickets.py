import unittest

from tickets.builder import Selection, TicketBuilder


class TicketBuilderTests(unittest.TestCase):

    def setUp(self):
        self.selections = [
            Selection("M1", "A vs B", "1X", 1.35, 88, 8.2),
            Selection("M2", "C vs D", "Home", 1.50, 84, 7.1),
            Selection("M3", "E vs F", "DNB", 1.40, 82, 5.8),
            Selection("M4", "G vs H", "Over 1.5", 1.30, 78, 6.9),
            Selection("M5", "I vs J", "Home", 1.60, 74, 9.4),
            Selection("M6", "K vs L", "Over 1.5", 1.28, 69, 4.2),
            Selection("M7", "M vs N", "1X", 1.37, 65, 7.8),
            Selection("M8", "O vs P", "Over 2.5", 1.72, 61, 10.3),
        ]

    def test_four_tickets_can_be_built(self):
        builder = TicketBuilder()

        tickets = builder.build(self.selections)

        self.assertEqual(
            [t.name for t in tickets],
            ["SAFE", "BALANCED", "AGGRESSIVE", "VALUE"],
        )

        builder.validate_tickets(tickets)

    def test_stakes_are_40_30_20_10(self):
        builder = TicketBuilder()

        tickets = builder.build(self.selections)

        self.assertEqual(
            [t.stake_percent for t in tickets],
            [40.0, 30.0, 20.0, 10.0],
        )

    def test_every_ticket_has_at_least_three_matches(self):
        builder = TicketBuilder()

        tickets = builder.build(self.selections)

        self.assertTrue(
            all(len(t.selections) >= 3 for t in tickets)
        )

    def test_no_forced_ticket_when_only_two_qualify(self):
        only_two = self.selections[:2]

        builder = TicketBuilder()

        tickets = builder.build(only_two)

        self.assertEqual(tickets, [])

    def test_no_duplicate_match_inside_ticket(self):
        duplicate = [
            Selection("M1", "A vs B", "1X", 1.35, 88, 8.2),
            Selection("M1", "A vs B", "Over 1.5", 1.40, 86, 7.0),
            *self.selections[1:7],
        ]

        builder = TicketBuilder()

        tickets = builder.build(duplicate)

        for ticket in tickets:
            match_ids = [
                s.match_id
                for s in ticket.selections
            ]

            self.assertEqual(
                len(match_ids),
                len(set(match_ids)),
            )


if __name__ == "__main__":
    unittest.main()
