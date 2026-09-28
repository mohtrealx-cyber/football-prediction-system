from unittest import TestCase

from tickets.builder import Selection, TicketBuilder


class TicketAssemblerTests(TestCase):

    def _make_selection(
        self,
        match_id,
        confidence=90.0,
        value_edge=10.0,
        odds=1.50,
    ):
        return Selection(
            match_id=match_id,
            match=f"Home {match_id} vs Away {match_id}",
            market="HOME",
            odds=odds,
            confidence=confidence,
            value_edge=value_edge,
        )

    def _make_candidates(self, count=12):
        return [
            self._make_selection(
                match_id=f"MATCH_{index}",
                confidence=90.0 - index,
                value_edge=10.0 - (index * 0.2),
                odds=1.40 + (index * 0.05),
            )
            for index in range(count)
        ]

    def test_four_tickets_can_be_created(self):
        builder = TicketBuilder()

        selections = self._make_candidates(12)

        tickets = builder.build(selections)

        names = [
            ticket.name
            for ticket in tickets
        ]

        self.assertEqual(
            names,
            [
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            ],
        )

    def test_four_ticket_stakes_are_correct(self):
        builder = TicketBuilder()

        selections = self._make_candidates(12)

        tickets = builder.build(selections)

        stakes = [
            ticket.stake_percent
            for ticket in tickets
        ]

        self.assertEqual(
            stakes,
            [
                40.0,
                20.0,
                10.0,
                30.0,
            ],
        )

    def test_each_ticket_has_at_least_three_matches(self):
        builder = TicketBuilder()

        selections = self._make_candidates(12)

        tickets = builder.build(selections)

        for ticket in tickets:
            self.assertGreaterEqual(
                len(ticket.selections),
                3,
            )

    def test_ticket_one_uses_strongest_selections(self):
        builder = TicketBuilder()

        selections = [
            self._make_selection(
                "STRONG_1",
                confidence=98.0,
                value_edge=15.0,
            ),
            self._make_selection(
                "STRONG_2",
                confidence=97.0,
                value_edge=14.0,
            ),
            self._make_selection(
                "STRONG_3",
                confidence=96.0,
                value_edge=13.0,
            ),
            self._make_selection(
                "WEAKER_1",
                confidence=82.0,
                value_edge=7.0,
            ),
            self._make_selection(
                "WEAKER_2",
                confidence=81.0,
                value_edge=6.0,
            ),
            self._make_selection(
                "WEAKER_3",
                confidence=80.0,
                value_edge=5.0,
            ),
        ]

        tickets = builder.build(selections)

        ironclad = tickets[0]

        selected_ids = {
            selection.match_id
            for selection in ironclad.selections
        }

        self.assertIn(
            "STRONG_1",
            selected_ids,
        )

        self.assertIn(
            "STRONG_2",
            selected_ids,
        )

        self.assertIn(
            "STRONG_3",
            selected_ids,
        )

    def test_tickets_use_candidate_matches(self):
        builder = TicketBuilder()

        selections = self._make_candidates(12)

        tickets = builder.build(selections)

        original_ids = {
            selection.match_id
            for selection in selections
        }

        for ticket in tickets:
            for selection in ticket.selections:
                self.assertIn(
                    selection.match_id,
                    original_ids,
                )

    def test_missing_candidate_field_is_rejected(self):
        selection = self._make_selection(
            "MATCH_1"
        )

        builder = TicketBuilder()

        selection_without_market = Selection(
            match_id=selection.match_id,
            match=selection.match,
            market="",
            odds=selection.odds,
            confidence=selection.confidence,
            value_edge=selection.value_edge,
        )

        with self.assertRaises(ValueError):
            builder.build(
                [selection_without_market]
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
