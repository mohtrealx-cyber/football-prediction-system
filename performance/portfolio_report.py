from performance.engine import calculate_performance
from performance.ticket import calculate_ticket_performance
from performance.ticket_market import calculate_ticket_market_performance


SUPPORTED_TICKETS = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)


def build_portfolio_report(results: dict) -> dict:
    """Build a complete portfolio performance report."""

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    provided_tickets = set(results.keys())

    unknown_tickets = (
        provided_tickets - set(SUPPORTED_TICKETS)
    )
    if unknown_tickets:
        raise ValueError(
            f"unknown tickets: {sorted(unknown_tickets)}"
        )

    missing_tickets = (
        set(SUPPORTED_TICKETS) - provided_tickets
    )
    if missing_tickets:
        raise ValueError(
            f"missing tickets: {sorted(missing_tickets)}"
        )

    all_results = []

    for ticket_name in SUPPORTED_TICKETS:
        ticket_markets = results[ticket_name]

        if not isinstance(ticket_markets, dict):
            raise TypeError(
                f"results for ticket '{ticket_name}' "
                "must be a dictionary"
            )

        for market_results in ticket_markets.values():
            if not isinstance(market_results, list):
                raise TypeError(
                    f"market results for ticket '{ticket_name}' "
                    "must be lists"
                )

            all_results.extend(market_results)

    overall = calculate_performance(all_results)

    tickets_input = {}

    for ticket_name in SUPPORTED_TICKETS:
        ticket_results = []

        for market_results in results[ticket_name].values():
            ticket_results.extend(market_results)

        tickets_input[ticket_name] = ticket_results

    tickets = calculate_ticket_performance(
        tickets_input
    )

    ticket_markets = calculate_ticket_market_performance(
        results
    )

    return {
        "overall": overall,
        "tickets": tickets,
        "ticket_markets": ticket_markets,
    }
