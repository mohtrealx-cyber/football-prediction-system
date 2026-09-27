import math

from backtesting.engine import backtest_selection
from data.historical_models import HistoricalMatch


REQUIRED_SELECTION_FIELDS = {
    "match",
    "market",
    "odds",
}

MIN_SELECTIONS = 3


def backtest_ticket(
    selections: list,
    stake: float,
) -> dict:
    """
    Backtest a multi-selection accumulator ticket.

    A ticket wins only when every selection wins.

    Args:
        selections:
            List of selection dictionaries. Each selection must contain:
                - match
                - market
                - odds

        stake:
            Total amount staked on the ticket.

    Returns:
        Dictionary containing:
            - selection_count
            - selections
            - combined_odds
            - stake
            - won
            - return_amount
            - profit_loss
    """

    # ---------------------------------------------------------
    # Validate selections container.
    # ---------------------------------------------------------

    if not isinstance(selections, list):
        raise TypeError("selections must be a list")

    if len(selections) < MIN_SELECTIONS:
        raise ValueError(
            "A ticket must contain at least 3 selections"
        )

    # ---------------------------------------------------------
    # Validate stake.
    # ---------------------------------------------------------

    if isinstance(stake, bool):
        raise ValueError("stake must be a number")

    if not isinstance(stake, (int, float)):
        raise ValueError("stake must be a number")

    if not math.isfinite(stake):
        raise ValueError("stake must be finite")

    if stake <= 0:
        raise ValueError("stake must be greater than zero")

    stake = float(stake)

    # ---------------------------------------------------------
    # Track matches and ticket calculations.
    # ---------------------------------------------------------

    match_ids = set()

    settled_selections = []

    combined_odds = 1.0
    ticket_won = True

    # ---------------------------------------------------------
    # Process every selection.
    # ---------------------------------------------------------

    for selection in selections:

        if not isinstance(selection, dict):
            raise TypeError(
                "Every selection must be a dictionary"
            )

        missing_fields = (
            REQUIRED_SELECTION_FIELDS
            - selection.keys()
        )

        if missing_fields:
            raise ValueError(
                "Selection is missing required fields: "
                f"{sorted(missing_fields)}"
            )

        match = selection["match"]
        market = selection["market"]
        odds = selection["odds"]

        # -----------------------------------------------------
        # Validate match.
        # -----------------------------------------------------

        if not isinstance(match, HistoricalMatch):
            raise TypeError(
                "selection match must be a HistoricalMatch"
            )

        # -----------------------------------------------------
        # Prevent duplicate matches inside one ticket.
        # -----------------------------------------------------

        if match.match_id in match_ids:
            raise ValueError(
                "The same match cannot appear twice in one ticket"
            )

        match_ids.add(match.match_id)

        # -----------------------------------------------------
        # Validate odds before using them in multiplication.
        # -----------------------------------------------------

        if isinstance(odds, bool):
            raise ValueError("odds must be a number")

        if not isinstance(odds, (int, float)):
            raise ValueError("odds must be a number")

        if not math.isfinite(odds):
            raise ValueError("odds must be finite")

        if odds <= 1:
            raise ValueError(
                "odds must be greater than 1"
            )

        odds = float(odds)

        # -----------------------------------------------------
        # Backtest the individual selection.
        #
        # Stake is 1.0 here because the ticket engine handles
        # the actual ticket-level stake.
        # -----------------------------------------------------

        result = backtest_selection(
            match=match,
            market=market,
            odds=odds,
            stake=1.0,
        )

        settled_selections.append(result)

        # Use validated odds from the settlement result.
        combined_odds *= result["odds"]

        if not result["won"]:
            ticket_won = False

    # ---------------------------------------------------------
    # Calculate ticket return and profit/loss.
    # ---------------------------------------------------------

    if ticket_won:
        return_amount = stake * combined_odds
        profit_loss = return_amount - stake
    else:
        return_amount = 0.0
        profit_loss = -stake

    # ---------------------------------------------------------
    # Return normalized result.
    # ---------------------------------------------------------

    return {
        "selection_count": len(selections),
        "selections": settled_selections,
        "combined_odds": float(combined_odds),
        "stake": float(stake),
        "won": ticket_won,
        "return_amount": float(return_amount),
        "profit_loss": float(profit_loss),
    }
