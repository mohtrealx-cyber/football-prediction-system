from tickets.builder import Selection, TicketBuilder

def main():
    fake_selections = [
        Selection("M1", "Arsenal vs Chelsea", "1X", 1.35, 88, 8.2),
        Selection("M2", "Barcelona vs Valencia", "Barcelona Win", 1.50, 84, 7.1),
        Selection("M3", "Inter vs Torino", "Inter DNB", 1.40, 82, 5.8),
        Selection("M4", "Milan vs Lazio", "Over 1.5", 1.30, 78, 6.9),
        Selection("M5", "Dortmund vs Mainz", "Dortmund Win", 1.60, 74, 9.4),
        Selection("M6", "PSG vs Lille", "Over 1.5", 1.28, 69, 4.2),
        Selection("M7", "Porto vs Braga", "1X", 1.37, 65, 7.8),
        Selection("M8", "Ajax vs Utrecht", "Over 2.5", 1.72, 61, 10.3),
    ]

    builder = TicketBuilder(min_matches=3, max_matches=6)
    tickets = builder.build(fake_selections)
    builder.validate_tickets(tickets)

    for ticket in tickets:
        print(f"\n{ticket.name} | stake={ticket.stake_percent}%")
        print(f"combined odds: {ticket.combined_odds}")
        print(f"average confidence: {ticket.average_confidence}%")
        for selection in ticket.selections:
            print(
                f"  - {selection.match} | {selection.market} | "
                f"odds {selection.odds} | confidence {selection.confidence}% | "
                f"value edge {selection.value_edge}%"
            )

if __name__ == "__main__":
    main()
