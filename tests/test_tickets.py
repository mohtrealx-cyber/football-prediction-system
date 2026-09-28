from unittest import TestCase

from tickets.builder import Selection, TicketBuilder


class TicketBuilderTests(TestCase):

    def _selection(
        self,
        match_id,
        confidence=90.0,
        value_edge=10.0,
        selected_odds=1.50,
    ):
        return Selection(
            match_id=match_id,
            match=f"Home {match_id} vs Away {match_id}",
            market="HOME",
            selected_odds=selected_odds,
            confidence=confidence,
            value_edge=value_edge,
        )

    def _selections(self, count=12):
        return [
            self._selection(
                f"MATCH_{i}",
                confidence=95.0 - i,
                value_edge=15.0 - (i * 0.25),
                selected_odds=1.40 + (i * 0.03),
            )
            for i in range(count)
        ]

    def test_four_tickets_can_be_built(self):
        builder = TicketBuilder()

        tickets = builder.build(
            self._selections(12)
        )

        self.assertEqual(
            [ticket.name for ticket in tickets],
            [
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            ],
        )

    def test_stakes_are_40_30_20_10(self):
        builder = TicketBuilder()

        tickets = builder.build(
            self._selections(12)
        )

        self.assertEqual(
            [
                ticket.stake_percent
                for ticket in tickets
            ],
            [
                40.0,
                30.0,
                20.0,
                10.0,
            ],
        )

    def test_ticket_names_match_strategy(self):
        builder = TicketBuilder()

        tickets = builder.build(
            self._selections(12)
        )

        expected = [
            "IRONCLAD",
            "BALANCED",
            "VOLATILITY",
            "BENCHMARK",
        ]

        actual = [
            ticket.name
            for ticket in tickets
        ]

        self.assertEqual(
            actual,
            expected,
        )

    def test_total_stake_is_100_percent(self):
        builder = TicketBuilder()

        tickets = builder.build(
            self._selections(12)
        )

        total_stake = sum(
            ticket.stake_percent
            for ticket in tickets
        )

        self.assertEqual(
            total_stake,
            100.0,
        )

    def test_each_ticket_has_three_to_six_matches(self):
        builder = TicketBuilder()

        tickets = builder.build(
            self._selections(12)
        )

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

            self.assertLessEqual(
                len(ticket.selections),
                6,
            )

    def test_no_duplicate_matches_inside_ticket(self):
        builder = TicketBuilder()

        tickets = builder.build(
            self._selections(12)
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
    import unittest

    unittest.main()
