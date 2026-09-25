from performance.engine import calculate_performance


SUPPORTED_TICKETS = {
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
}


def calculate_ticket_performance(results: dict) -> dict:
    """
    Calculate performance separately for the four ticket types.

    Expected input:

        {
            "SAFE": [...],
            "BALANCED": [...],
            "AGGRESSIVE": [...],
            "VALUE": [...]
        }

    Each ticket contains its historical ticket results.

    Returns one performance summary per ticket.
    """

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    provided_tickets = set(results.keys())

    unknown_tickets = provided_tickets - SUPPORTED_TICKETS

    if unknown_tickets:
        raise ValueError(
            f"Unsupported ticket(s): {sorted(unknown_tickets)}"
        )

    missing_tickets = SUPPORTED_TICKETS - provided_tickets

    if missing_tickets:
        raise ValueError(
            f"Missing ticket(s): {sorted(missing_tickets)}"
        )

    performance_by_ticket = {}

    for ticket_name in (
        "SAFE",
        "BALANCED",
        "AGGRESSIVE",
        "VALUE",
    ):
        ticket_results = results[ticket_name]

        if not isinstance(ticket_results, list):
            raise TypeError(
                f"Results for {ticket_name} must be a list"
            )

        try:
            performance = calculate_performance(ticket_results)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid results for ticket {ticket_name}: {exc}"
            ) from exc

        performance_by_ticket[ticket_name] = performance

    return performance_by_ticket
