from markets.engine import get_supported_markets
from performance.engine import calculate_performance
from performance.streaks import calculate_streaks


SUPPORTED_TICKETS = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)


def calculate_ticket_market_performance(results: dict) -> dict:
    """Calculate performance separately for every ticket and market."""

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    supported_markets = get_supported_markets()
    required_markets = set(supported_markets)

    provided_tickets = set(results.keys())

    unknown_tickets = provided_tickets - set(SUPPORTED_TICKETS)
    if unknown_tickets:
        raise ValueError(
            f"unknown tickets: {sorted(unknown_tickets)}"
        )

    missing_tickets = set(SUPPORTED_TICKETS) - provided_tickets
    if missing_tickets:
        raise ValueError(
            f"missing tickets: {sorted(missing_tickets)}"
        )

    performance = {}

    for ticket_name in SUPPORTED_TICKETS:
        ticket_results = results[ticket_name]

        if not isinstance(ticket_results, dict):
            raise TypeError(
                f"results for ticket '{ticket_name}' must be a dictionary"
            )

        provided_markets = set(ticket_results.keys())

        unknown_markets = provided_markets - required_markets
        if unknown_markets:
            raise ValueError(
                f"unknown markets for ticket '{ticket_name}': "
                f"{sorted(unknown_markets)}"
            )

        missing_markets = required_markets - provided_markets
        if missing_markets:
            raise ValueError(
                f"missing markets for ticket '{ticket_name}': "
                f"{sorted(missing_markets)}"
            )

        performance[ticket_name] = {}

        for market_name in supported_markets:
            market_results = ticket_results[market_name]

            if not isinstance(market_results, list):
                raise TypeError(
                    f"results for ticket '{ticket_name}' "
                    f"and market '{market_name}' must be a list"
                )

            try:
                market_performance = calculate_performance(
                    market_results
                )
                streaks = calculate_streaks(
                    market_results
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"invalid results for ticket '{ticket_name}' "
                    f"and market '{market_name}'"
                ) from exc

            performance[ticket_name][market_name] = {
                **market_performance,
                "streaks": streaks,
            }

    return performance
