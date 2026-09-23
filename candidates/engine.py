from typing import Dict, List


def build_candidate_pool(
    analyses: List[Dict],
    minimum_score: float = 50.0,
) -> List[Dict]:
    """
    Build a pool of qualified selections.

    Rules:
    - Must be qualified
    - Must meet the minimum score
    - One selection per match
    - Highest score first
    """

    if minimum_score < 0 or minimum_score > 100:
        raise ValueError(
            "minimum_score must be between 0 and 100"
        )

    candidates = []
    used_matches = set()

    for analysis in analyses:
        if "match_id" not in analysis:
            raise ValueError(
                "analysis is missing match_id"
            )

        if "qualified" not in analysis:
            raise ValueError(
                "analysis is missing qualified"
            )

        if "score" not in analysis:
            raise ValueError(
                "analysis is missing score"
            )

        if not analysis["qualified"]:
            continue

        if analysis["score"] < minimum_score:
            continue

        match_id = analysis["match_id"]

        if match_id in used_matches:
            continue

        candidates.append(analysis)
        used_matches.add(match_id)

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return candidates
