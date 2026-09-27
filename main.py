from datetime import datetime

from data.fixture_loader import load_fixtures
from data.daily_fixtures import get_daily_fixtures
from data.historical_provider import HistoricalDataProvider
from pipeline.daily_time_guard import filter_upcoming_fixtures
from pipeline.daily_real_pipeline import build_daily_real_candidates


FIXTURE_FILE = "fixtures.csv"

# Change these when we connect the historical datasets.
HISTORICAL_FILES = {
    "Premier League": "data/historical/premier_league.csv",
}


def load_historical_data():
    """Load all configured historical league data."""
    history = []

    for league, path in HISTORICAL_FILES.items():
        provider = HistoricalDataProvider(
            csv_path=path,
            league=league,
        )

        history.extend(provider.get_matches())

    return history


def main():
    print("=" * 70)
    print("FOOTBALL PREDICTION SYSTEM")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. DOWNLOAD FIXTURES
    # ---------------------------------------------------------
    print("\n[1/5] Downloading latest fixtures...")

    matches = load_fixtures(
        destination_path=FIXTURE_FILE,
    )

    print(f"Downloaded fixtures: {len(matches)}")

    # ---------------------------------------------------------
    # 2. CURRENT TIME
    # ---------------------------------------------------------
    now = datetime.now().astimezone()

    print(f"\nCurrent time: {now.isoformat()}")

    # ---------------------------------------------------------
    # 3. DAILY FIXTURES
    # ---------------------------------------------------------
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

    if not upcoming_matches:
        print("\nNo upcoming fixtures found.")
        return

    print("\nUpcoming fixtures:")

    for match in upcoming_matches:
        print(
            f"- {match.home_team} vs {match.away_team}"
            f" | {match.league}"
            f" | {match.kickoff.isoformat()}"
            f" | odds={match.odds}"
        )

    # ---------------------------------------------------------
    # 4. HISTORICAL DATA
    # ---------------------------------------------------------
    print("\n[4/5] Loading historical data...")

    history = load_historical_data()

    print(f"Historical matches loaded: {len(history)}")

    if not history:
        print("\nNO BET")
        print("Reason: no historical data available.")
        return

    # ---------------------------------------------------------
    # 5. BUILD REAL CANDIDATES
    # ---------------------------------------------------------
    print("\n[5/5] Building real market candidates...")

    candidates = build_daily_real_candidates(
        fixtures=upcoming_matches,
        history=history,
    )

    print(
        f"Qualified/analysed candidates generated: "
        f"{len(candidates)}"
    )

    if not candidates:
        print("\nNO BET")
        print("Reason: no valid candidates were generated.")
        return

    print("\nTOP CANDIDATES")
    print("-" * 70)

    for candidate in candidates[:20]:
        print(
            f"{candidate['home_team']} vs "
            f"{candidate['away_team']}"
            f" | {candidate['market']}"
            f" | odds={candidate['selected_odds']:.2f}"
            f" | probability="
            f"{candidate['model_probability']:.3f}"
            f" | edge="
            f"{candidate['value_edge']:.2f}%"
            f" | score="
            f"{candidate['score']:.2f}"
        )


if __name__ == "__main__":
    main()
