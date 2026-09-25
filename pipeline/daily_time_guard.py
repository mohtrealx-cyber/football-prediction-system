from __future__ import annotations

from datetime import datetime
from typing import Any

from data.models import Match


def _validate_as_of(as_of: Any) -> None:
    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError(
            "as_of must be timezone-aware"
        )


def _validate_fixture(fixture: Any) -> None:
    if not isinstance(fixture, Match):
        raise TypeError(
            "each fixture must be a Match"
        )

    if fixture.kickoff.tzinfo is None or fixture.kickoff.utcoffset() is None:
        raise ValueError(
            "fixture kickoff must be timezone-aware"
        )


def filter_upcoming_fixtures(
    fixtures: list[Match],
    as_of: datetime,
) -> list[Match]:
    """
    Return only scheduled fixtures that have not kicked off yet.

    A fixture is considered upcoming only when:

        fixture.status == "scheduled"
        AND
        fixture.kickoff > as_of

    The input list is never modified and its original order
    is preserved.
    """
    if not isinstance(fixtures, list):
        raise TypeError(
            "fixtures must be a list"
        )

    _validate_as_of(as_of)

    for fixture in fixtures:
        _validate_fixture(fixture)

    return [
        fixture
        for fixture in fixtures
        if fixture.status == "scheduled"
        and fixture.kickoff > as_of
    ]
