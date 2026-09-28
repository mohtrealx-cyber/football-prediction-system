import os
import time
import requests
from datetime import datetime, timezone
from data.fixture_downloader import download_fixtures
from data.fixture_loader import load_fixtures
from data.historical_loader import load_historical_matches
from pipeline.daily_report_output import build_daily_report_output

# ==============================================================================
# TELEGRAM CONFIGURATION
# ==============================================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

def send_telegram_alert(msg: str) -> None:
    if not (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        print("Telegram credentials missing; notification skipped.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunk_size = 4000
    msg_chunks = [msg[i:i + chunk_size] for i in range(0, len(msg), chunk_size)]

    for chunk in msg_chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown",
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code != 200:
                payload.pop("parse_mode", None)
                r2 = requests.post(url, json=payload, timeout=15)
                if r2.status_code != 200:
                    print(f"Telegram alert error: {r2.text}")
        except Exception as e:
            print(f"Telegram alert exception: {e}")
        time.sleep(1)


def main():
    print("=======================================================================")
    print("FOOTBALL PREDICTION SYSTEM")
    print("=======================================================================")

    print("\n[1/5] Downloading latest fixtures...")
    download_fixtures()
    fixtures = load_fixtures()
    print(f"Downloaded fixtures: {len(fixtures)}")

    as_of = datetime.now(timezone.utc)
    print(f"\nCurrent time: {as_of.isoformat()}")

    print("\n[2/5] Loading historical data...")
    LEAGUES_TO_LOAD = [
        ("data/historical/premier_league.csv", "Premier League"),
        ("data/historical/bundesliga.csv", "Bundesliga"),
        ("data/historical/la_liga.csv", "La Liga"),
        ("data/historical/serie_a.csv", "Serie A"),
        ("data/historical/ligue_1.csv", "Ligue 1"),
        ("data/historical/eredivisie.csv", "Eredivisie"),
        ("data/historical/primeira_liga.csv", "Primeira Liga"),
        ("data/historical/champions_league.csv", "UEFA Champions League"),
        ("data/historical/europa_league.csv", "UEFA Europa League"),
        ("data/historical/conference_league.csv", "UEFA Conference League"),
    ]

    history = []
    for csv_path, league_name in LEAGUES_TO_LOAD:
        try:
            matches = load_historical_matches(csv_path, league_name)
            history.extend(matches)
            print(f"  Loaded {len(matches)} matches: {league_name}")
        except Exception as e:
            print(f"  Skipped {league_name}: {e}")

    print(f"\nTotal historical matches loaded: {len(history)}")

    print("\n[3/5] Running complete prediction pipeline...")
    report_result = build_daily_report_output(
        fixtures=fixtures,
        history=history,
        as_of=as_of,
    )

    status = report_result.get("status", "NO_BET")
    print(f"Pipeline status: {status}")

    # ==========================================================================
    # COMPOSE & DISPATCH TELEGRAM ALERT
    # ==========================================================================
    message = f"⚽ **FOOTBALL PREDICTION SYSTEM REPORT** ⚽\n\n"
    message += f"Status: `{status}`\n"
    message += f"Fixtures Processed: `{report_result.get('fixtures_received', 0)}`\n\n"

    if status == "READY":
        message += "🎯 **OPTIMIZED PORTFOLIO TICKETS READY** 🎯\n"
        portfolio = report_result.get("portfolio", [])
        for ticket in portfolio:
            message += f"\n• **{ticket.get('name')}** ({ticket.get('stake_percent')}% Stake)\n"
            for sel in ticket.get("selections", []):
                message += f"  ↳ {sel.get('match')} ➔ {sel.get('market')} (Odds: {sel.get('selected_odds')})\n"
    else:
        message += "⚠️ **NO BET:** Insufficient qualifying selections today.\n"

    send_telegram_alert(message)


if __name__ == "__main__":
    main()
