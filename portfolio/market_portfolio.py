from portfolio.engine import build_smart_portfolio


def build_market_portfolio(
    candidates,
):
    """
    Build the four-ticket portfolio from market candidates.

    The existing portfolio engine handles:
    - SAFE — 40%
    - BALANCED — 30%
    - AGGRESSIVE — 20%
    - VALUE — 10%
    - minimum ticket size
    - maximum ticket size
    - match reuse limits
    - ticket diversity
    """
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    return build_smart_portfolio(candidates)
