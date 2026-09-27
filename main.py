from datetime import datetime

from data.fixture_loader import load_fixtures
from data.daily_fixtures import get_daily_fixtures
from data.historical_provider import HistoricalDataProvider
from pipeline.daily_result import build_daily_result


FIXTURE_FILE = "fixtures.csv"

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


def print_ticket(ticket):
    print()
    print("=" * 70)
    print(f"TICKET: {ticket.name}")
    print(f"STAKE: {ticket.stake_percent}%")
    print(f"COMBINED ODDS: {ticket.combined_odds:.2f}")
    print(f"AVERAGE CONFIDENCE: {ticket.average_confidence:.2f}%")
    print("-" * 70)

    for selection in ticket.selections:
        print(
            f"- {selection.match}"
            f" | {selection.market}"
            f" | odds={selection.odds:.2f}"
            f" | confidence={selection.confidence:.2f}%"
            f" | edge={selection.value_edge:.2f}%"
        )


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

    # ---------------------------------------------------------
    # 4. HISTORICAL DATA
    # ---------------------------------------------------------
    print("\n[2/5] Loading historical data...")

    history = load_historical_data()

    print(
        f"Historical matches loaded: "
        f"{len(history)}"
    )

    if not history:
        print("\nNO BET")
        print("Reason: no historical data available.")
        return

    # ---------------------------------------------------------
    # 5. COMPLETE DAILY PIPELINE
    # ---------------------------------------------------------
    print("\n[3/5] Running complete prediction pipeline...")

    result = build_daily_result(
        fixtures=daily_matches,
        history=history,
        as_of=now,
    )

    print(
        f"Fixtures received: "
        f"{result['fixtures_received']}"
    )

    print(
        f"Upcoming fixtures: "
        f"{result['upcoming_fixtures']}"
    )

    print(
        f"Pipeline status: "
        f"{result['status']}"
    )

    # ---------------------------------------------------------
    # NO BET
    # ---------------------------------------------------------
    if result["status"] == "NO_BET":
        print("\n" + "=" * 70)
        print("NO BET")
        print("=" * 70)
        print(
            "Reason: "
            "insufficient qualifying selections"
        )
        return

    # ---------------------------------------------------------
    # READY
    # ---------------------------------------------------------
    portfolio = result["portfolio"]

    print("\n[4/5] Portfolio generated.")

    # ---------------------------------------------------------
    # TICKETS
    # ---------------------------------------------------------
    print("\n[5/5] FINAL DAILY TICKETS")

    if not portfolio:
        print("\nNO BET")
        print("Reason: portfolio is empty.")
        return

    for ticket in portfolio:
        print_ticket(ticket)

    print()
    print("=" * 70)
    print("DAILY PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
