import json
import time
from pathlib import Path
from datetime import datetime, timezone
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAX_LIMIT = 1000          # Binance max klines par call (souvent 1000)
SLEEP_SEC = 0.2           # petite pause anti rate-limit


def to_ms(dt_str_utc: str) -> int:
    # dt_str_utc format: "YYYY-MM-DD" ou "YYYY-MM-DD HH:MM:SS"
    fmt = "%Y-%m-%d" if len(dt_str_utc) == 10 else "%Y-%m-%d %H:%M:%S"
    dt = datetime.strptime(dt_str_utc, fmt).replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_klines(symbol: str, interval: str, start_ms: int, end_ms: int, limit: int = MAX_LIMIT):
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": limit
    }
    r = requests.get(BASE_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        raise RuntimeError(f"Binance API error: {data}")
    return data


def fetch_history(symbol: str, interval: str, start_utc: str, end_utc: str) -> list:
    start_ms = to_ms(start_utc)
    end_ms = to_ms(end_utc)

    all_rows = []
    cursor = start_ms

    while True:
        chunk = fetch_klines(symbol, interval, cursor, end_ms, limit=MAX_LIMIT)
        if not chunk:
            break

        all_rows.extend(chunk)

        last_open_time = chunk[-1][0]
        next_cursor = last_open_time + 1  # éviter de répéter la dernière bougie

        if next_cursor <= cursor:
            break

        cursor = next_cursor

        # stop si on a dépassé end_ms
        if cursor > end_ms:
            break

        time.sleep(SLEEP_SEC)

    # dédoublonnage simple (au cas où)
    seen = set()
    dedup = []
    for row in all_rows:
        ot = row[0]
        if ot not in seen:
            seen.add(ot)
            dedup.append(row)

    return dedup


def save_json(data: list, filename: str) -> Path:
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] saved {len(data)} rows -> {path}")
    return path


if __name__ == "__main__":
    # Exemple : 90 jours d'historique en 1h sur BTCUSDT (à adapter)
    symbol = "BTCUSDT"
    interval = "1h"
    start_utc = "2025-09-01"
    end_utc   = "2025-12-01"

    data = fetch_history(symbol, interval, start_utc, end_utc)
    save_json(data, f"binance_{symbol}_{interval}_{start_utc}_to_{end_utc}.json")
