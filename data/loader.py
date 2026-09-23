from typing import Iterable, List

from .models import Match


def validate_matches(matches: Iterable[Match]) -> List[Match]:
    validated = []

    for match in matches:
        match.validate()
        validated.append(match)

    return validated
