from performance.engine import calculate_performance

SUPPORTED_TICKETS = {
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
}


def calculate_portfolio_performance(results: dict) -> dict:
    """
    Calculate overall portfolio performance and preserve
    performance for each of the four ticket types.
    """

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    provided_tickets = set(results.keys())

    unknown_tickets = provided_tickets - SUPPORTED_TICKETS
    if unknown_tickets:
        raise ValueError(
            f"unknown ticket(s): {sorted(unknown_tickets)}"
        )

    missing_tickets = SUPPORTED_TICKETS - provided_tickets
    if missing_tickets:
        raise ValueError(
            f"missing ticket(s): {sorted(missing_tickets)}"
        )

    ticket_results = {}

    all_results = []

    for ticket_name in (
        "SAFE",
        "BALANCED",
        "AGGRESSIVE",
        "VALUE",
    ):
        results_for_ticket = results[ticket_name]

        if not isinstance(results_for_ticket, list):
            raise TypeError(
                f"{ticket_name} results must be a list"
            )

        try:
            performance = calculate_performance(results_for_ticket)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"invalid results for {ticket_name}"
            ) from exc

        ticket_results[ticket_name] = performance
        all_results.extend(results_for_ticket)

    overall = calculate_performance(all_results)

    return {
        "overall": overall,
        "tickets": ticket_results,
    }
