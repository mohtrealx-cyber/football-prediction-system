from datetime import datetime

from data.fixture_loader import load_fixtures
from data.daily_fixtures import get_daily_fixtures
from pipeline.daily_time_guard import filter_upcoming_fixtures


FIXTURE_FILE = "fixtures.csv"


def main():
    print("=" * 70)
    print("FOOTBALL PREDICTION SYSTEM")
    print("=" * 70)

    print("\nDownloading latest fixtures...")

    matches = load_fixtures(
        destination_path=FIXTURE_FILE,
    )

    print(f"Downloaded fixtures: {len(matches)}")

    now = datetime.now().astimezone()

    print(f"\nCurrent time: {now.isoformat()}")

    daily_matches = get_daily_fixtures(
        matches=matches,
        date=now,
    )

    print(
        f"Fixtures inside Nairobi daily window: "
        f"{len(daily_matches)}"
    )

    upcoming_matches = filter_upcoming_fixtures(
        daily_matches,
        now,
    )

    print(
        f"Upcoming fixtures remaining: "
        f"{len(upcoming_matches)}"
    )

    print("\nUpcoming fixtures:")

    if not upcoming_matches:
        print("No upcoming fixtures found.")
        return

    for match in upcoming_matches:
        print(
            f"- {match.home_team} vs {match.away_team}"
            f" | {match.league}"
            f" | {match.kickoff.isoformat()}"
            f" | odds={match.odds}"
        )


if __name__ == "__main__":
    main()
