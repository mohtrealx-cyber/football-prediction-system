from performance.engine import calculate_performance
from performance.streaks import calculate_streaks


SUPPORTED_TICKETS = {
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
}


def calculate_ticket_performance(results: dict) -> dict:
    """
    Calculate performance separately for each ticket.

    Each ticket receives:
    - the existing performance metrics
    - streak statistics
    """

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    provided_tickets = set(results.keys())

    unknown_tickets = provided_tickets - SUPPORTED_TICKETS
    if unknown_tickets:
        raise ValueError(
            f"unknown tickets: {sorted(unknown_tickets)}"
        )

    missing_tickets = SUPPORTED_TICKETS - provided_tickets
    if missing_tickets:
        raise ValueError(
            f"missing tickets: {sorted(missing_tickets)}"
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
                f"results for ticket '{ticket_name}' must be a list"
            )

        try:
            performance = calculate_performance(ticket_results)
            streaks = calculate_streaks(ticket_results)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"invalid results for ticket '{ticket_name}'"
            ) from exc

        # Preserve all existing performance metrics and add
        # ticket-level streak statistics.
        performance_by_ticket[ticket_name] = {
            **performance,
            "streaks": streaks,
        }

    return performance_by_ticket
