from datetime import datetime

from data.fixture_loader import load_fixtures
from data.daily_fixtures import get_daily_fixtures
from data.historical_provider import HistoricalDataProvider
from pipeline.daily_result import build_daily_result


FIXTURE_FILE = "fixtures.csv"


# ============================================================
# HISTORICAL DATA SOURCES
# ============================================================
#
# Add historical CSV files here as they become available.
#
# The system is NOT limited to the Premier League.
# Each competition gets its own dataset and league label.
#
# IMPORTANT:
# Do not add a file here until that file actually exists.
#
HISTORICAL_FILES = {
    "Premier League": "data/historical/premier_league.csv",

    # Add these one at a time when their CSV files are ready:
    #
    # "Bundesliga": "data/historical/bundesliga.csv",
    # "La Liga": "data/historical/la_liga.csv",
    # "Serie A": "data/historical/serie_a.csv",
    # "Ligue 1": "data/historical/ligue_1.csv",
    # "Eredivisie": "data/historical/eredivisie.csv",
    # "Primeira Liga": "data/historical/primeira_liga.csv",
    #
    # UEFA competitions:
    #
    # "UEFA Champions League":
    #     "data/historical/champions_league.csv",
    #
    # "UEFA Europa League":
    #     "data/historical/europa_league.csv",
    #
    # "UEFA Conference League":
    #     "data/historical/conference_league.csv",
}


def load_historical_data():
    """
    Load all configured historical competition data.

    Every configured CSV is loaded through HistoricalDataProvider.
    The resulting HistoricalMatch objects are combined into one
    historical dataset for the prediction pipeline.
    """

    history = []

    for league, path in HISTORICAL_FILES.items():
        print(
            f"Loading historical data: "
            f"{league} -> {path}"
        )

        provider = HistoricalDataProvider(
            csv_path=path,
            league=league,
        )

        matches = provider.get_matches()

        print(
            f"  Loaded {len(matches)} matches"
        )

        history.extend(matches)

    return history


def print_ticket(ticket):
    print()
    print("=" * 70)
    print(f"TICKET: {ticket.name}")
    print(f"STAKE: {ticket.stake_percent}%")
    print(
        f"COMBINED ODDS: "
        f"{ticket.combined_odds:.2f}"
    )
    print(
        f"AVERAGE CONFIDENCE: "
        f"{ticket.average_confidence:.2f}%"
    )
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
    print(
        "\n[1/5] Downloading latest fixtures..."
    )

    matches = load_fixtures(
        destination_path=FIXTURE_FILE,
    )

    print(
        f"Downloaded fixtures: "
        f"{len(matches)}"
    )

    # ---------------------------------------------------------
    # 2. CURRENT TIME
    # ---------------------------------------------------------
    now = datetime.now().astimezone()

    print(
        f"\nCurrent time: "
        f"{now.isoformat()}"
    )

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
    print(
        "\n[2/5] Loading historical data..."
    )

    history = load_historical_data()

    print(
        f"\nHistorical matches loaded: "
        f"{len(history)}"
    )

    if not history:
        print("\nNO BET")
        print(
            "Reason: no historical data available."
        )
        return

    # ---------------------------------------------------------
    # 5. COMPLETE DAILY PIPELINE
    # ---------------------------------------------------------
    print(
        "\n[3/5] Running complete prediction pipeline..."
    )

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

    print(
        "\n[4/5] Portfolio generated."
    )

    # ---------------------------------------------------------
    # TICKETS
    # ---------------------------------------------------------
    print(
        "\n[5/5] FINAL DAILY TICKETS"
    )

    if not portfolio:
        print("\nNO BET")
        print(
            "Reason: portfolio is empty."
        )
        return

    for ticket in portfolio:
        print_ticket(ticket)

    print()
    print("=" * 70)
    print("DAILY PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
