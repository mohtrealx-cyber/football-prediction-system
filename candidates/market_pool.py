from candidates.engine import build_candidate_pool


def build_market_candidate_pool(
    candidates,
    minimum_score=50.0,
):
    """
    Build the final candidate pool from market candidates.

    The existing candidate engine handles:
    - qualification filtering
    - minimum score filtering
    - one selection per match
    - ranking by score
    """
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    return build_candidate_pool(
        candidates,
        minimum_score=minimum_score,
    )
