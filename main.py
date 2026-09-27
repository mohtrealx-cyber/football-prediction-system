from datetime import datetime
from pathlib import Path

from data.fixture_loader import load_fixtures
from data.daily_fixtures import get_daily_fixtures
from data.historical_provider import HistoricalDataProvider
from pipeline.daily_result import build_daily_result


FIXTURE_FILE = "fixtures.csv"


# ============================================================
# HISTORICAL DATA SOURCES
# ============================================================
#
# The system is NOT limited to the Premier League.
#
# Supported competitions include:
#   - Premier League
#   - Bundesliga
#   - La Liga
#   - Serie A
#   - Ligue 1
#   - Eredivisie
#   - Primeira Liga
#   - UEFA Champions League
#   - UEFA Europa League
#   - UEFA Conference League
#
# A competition is loaded only when its CSV file exists.
# This prevents the system from crashing while datasets are
# being added one at a time.
#
# All CSV files should use the same structure:
#
# Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR
#
# Optional odds columns supported by HistoricalDataProvider:
# B365H,B365D,B365A
#
# ============================================================

HISTORICAL_FILES = {
    # --------------------------------------------------------
    # ENGLAND
    # --------------------------------------------------------
    "Premier League": (
        "data/historical/premier_league.csv"
    ),

    # --------------------------------------------------------
    # GERMANY
    # --------------------------------------------------------
    "Bundesliga": (
        "data/historical/bundesliga.csv"
    ),

    # --------------------------------------------------------
    # SPAIN
    # --------------------------------------------------------
    "La Liga": (
        "data/historical/la_liga.csv"
    ),

    # --------------------------------------------------------
    # ITALY
    # --------------------------------------------------------
    "Serie A": (
        "data/historical/serie_a.csv"
    ),

    # --------------------------------------------------------
    # FRANCE
    # --------------------------------------------------------
    "Ligue 1": (
        "data/historical/ligue_1.csv"
    ),

    # --------------------------------------------------------
    # NETHERLANDS
    # --------------------------------------------------------
    "Eredivisie": (
        "data/historical/eredivisie.csv"
    ),

    # --------------------------------------------------------
    # PORTUGAL
    # --------------------------------------------------------
    "Primeira Liga": (
        "data/historical/primeira_liga.csv"
    ),

    # --------------------------------------------------------
    # UEFA CHAMPIONS LEAGUE
    # --------------------------------------------------------
    "UEFA Champions League": (
        "data/historical/champions_league.csv"
    ),

    # --------------------------------------------------------
    # UEFA EUROPA LEAGUE
    # --------------------------------------------------------
    "UEFA Europa League": (
        "data/historical/europa_league.csv"
    ),

    # --------------------------------------------------------
    # UEFA CONFERENCE LEAGUE
    # --------------------------------------------------------
    "UEFA Conference League": (
        "data/historical/conference_league.csv"
    ),
}


def load_historical_data():
    """
    Load all available historical competition data.

    Every configured CSV that actually exists is loaded through
    HistoricalDataProvider.

    Missing datasets are skipped instead of causing the entire
    prediction system to crash.

    Returns:
        list[HistoricalMatch]: Combined historical dataset.
    """

    history = []

    print("\nChecking historical datasets...")

    for league, path in HISTORICAL_FILES.items():
        file_path = Path(path)

        # ----------------------------------------------------
        # DATASET NOT CREATED YET
        # ----------------------------------------------------
        if not file_path.exists():
            print(
                f"  SKIPPED: {league} -> {path}"
                " [file not found]"
            )
            continue

        # ----------------------------------------------------
        # DATASET EXISTS
        # ----------------------------------------------------
        print(
            f"Loading historical data: "
            f"{league} -> {path}"
        )

        try:
            provider = HistoricalDataProvider(
                csv_path=path,
                league=league,
            )

            matches = provider.get_matches()

            print(
                f"  Loaded {len(matches)} matches"
            )

            history.extend(matches)

        except Exception as exc:
            raise RuntimeError(
                f"Failed to load historical data for "
                f"{league}: {exc}"
            ) from exc

    print(
        f"\nTotal historical matches loaded: "
        f"{len(history)}"
    )

    return history


def print_ticket(ticket):
    """
    Print one generated betting ticket.
    """

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

    # ========================================================
    # 1. DOWNLOAD FIXTURES
    # ========================================================

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

    # ========================================================
    # 2. CURRENT TIME
    # ========================================================

    now = datetime.now().astimezone()

    print(
        f"\nCurrent time: "
        f"{now.isoformat()}"
    )

    # ========================================================
    # 3. DAILY FIXTURES
    # ========================================================

    daily_matches = get_daily_fixtures(
        matches=matches,
        date=now,
    )

    print(
        f"Fixtures inside Nairobi daily window: "
        f"{len(daily_matches)}"
    )

    # ========================================================
    # 4. HISTORICAL DATA
    # ========================================================

    print(
        "\n[2/5] Loading historical data..."
    )

    history = load_historical_data()

    if not history:
        print("\n" + "=" * 70)
        print("NO BET")
        print("=" * 70)
        print(
            "Reason: no historical datasets are available."
        )
        return

    # ========================================================
    # 5. COMPLETE DAILY PIPELINE
    # ========================================================

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

    # ========================================================
    # NO BET
    # ========================================================

    if result["status"] == "NO_BET":
        print("\n" + "=" * 70)
        print("NO BET")
        print("=" * 70)

        print(
            "Reason: "
            "insufficient qualifying selections"
        )

        return

    # ========================================================
    # READY
    # ========================================================

    portfolio = result["portfolio"]

    print(
        "\n[4/5] Portfolio generated."
    )

    # ========================================================
    # FINAL TICKETS
    # ========================================================

    print(
        "\n[5/5] FINAL DAILY TICKETS"
    )

    if not portfolio:
        print("\n" + "=" * 70)
        print("NO BET")
        print("=" * 70)

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
