import math

from backtesting.settlement import settle_market
from data.historical_models import HistoricalMatch


def backtest_selection(
    match: HistoricalMatch,
    market: str,
    odds: float,
    stake: float,
) -> dict:
    """
    Backtest one historical betting selection.

    Args:
        match: Historical match containing the final score.
        market: Supported betting market.
        odds: Decimal odds for the selection.
        stake: Amount staked.

    Returns:
        Dictionary containing the settlement result,
        return amount, and profit/loss.
    """

    # Validate match.
    if not isinstance(match, HistoricalMatch):
        raise TypeError("match must be a HistoricalMatch")

    # Validate market through the settlement engine.
    # This also rejects unsupported markets.
    won = settle_market(match, market)

    # Validate odds.
    if isinstance(odds, bool):
        raise ValueError("odds must be a number")

    if not isinstance(odds, (int, float)):
        raise ValueError("odds must be a number")

    if not math.isfinite(odds):
        raise ValueError("odds must be finite")

    if odds <= 1:
        raise ValueError("odds must be greater than 1")

    # Validate stake.
    if isinstance(stake, bool):
        raise ValueError("stake must be a number")

    if not isinstance(stake, (int, float)):
        raise ValueError("stake must be a number")

    if not math.isfinite(stake):
        raise ValueError("stake must be finite")

    if stake <= 0:
        raise ValueError("stake must be greater than zero")

    # Calculate return and profit/loss.
    if won:
        return_amount = stake * odds
        profit_loss = return_amount - stake
    else:
        return_amount = 0.0
        profit_loss = -stake

    return {
        "match_id": match.match_id,
        "market": market,
        "odds": float(odds),
        "stake": float(stake),
        "won": won,
        "return_amount": float(return_amount),
        "profit_loss": float(profit_loss),
    }
