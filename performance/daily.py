from performance.engine import calculate_performance
from performance.streaks import calculate_streaks
from performance.ticket import calculate_ticket_performance


SUPPORTED_TICKETS = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)


def calculate_daily_performance(results: dict) -> dict:
    """Calculate the complete performance for one trading day."""

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

    ticket_results = {}

    all_results = []

    for ticket_name in SUPPORTED_TICKETS:
        ticket_data = results[ticket_name]

        if not isinstance(ticket_data, list):
            raise TypeError(
                f"results for ticket '{ticket_name}' must be a list"
            )

        ticket_results[ticket_name] = ticket_data
        all_results.extend(ticket_data)

    overall = calculate_performance(all_results)
    streaks = calculate_streaks(all_results)
    tickets = calculate_ticket_performance(ticket_results)

    return {
        **overall,
        "tickets": tickets,
        "streaks": streaks,
    }
