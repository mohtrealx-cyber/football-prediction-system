from typing import Protocol

from data.models import Match


class DataProvider(Protocol):
    """Interface that every real football data source must follow."""

    def get_matches(self) -> list[Match]:
        """Return available football matches."""
        ...
