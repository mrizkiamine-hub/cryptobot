import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Optional

import psycopg2
from psycopg2.extras import execute_values


BASE_DIR = Path(__file__).resolve().parents[2]   # ~/cryptobot
DATA_DIR = BASE_DIR / "data" / "processed"

TS_FMT = "%Y-%m-%d %H:%M:%S"

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "dst_db",
    "user": "daniel",
    "password": "datascientest",
}


def extract_symbol_interval(filename: str) -> Tuple[str, str]:
    parts = filename.split("_")
    return parts[1], parts[2]


def to_float(x: Optional[str]) -> Optional[float]:
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def to_int(x: Optional[str]) -> Optional[int]:
    try:
        return int(x) if x not in (None, "") else None
    except ValueError:
        return None


def parse_utc(ts_str: str) -> datetime:
    return datetime.strptime(ts_str, TS_FMT).replace(tzinfo=timezone.utc)


def load_csv_into_fact_market_price(csv_filename: str) -> int:
    csv_path = DATA_DIR / csv_filename
    if not csv_path.exists():
        raise FileNotFoundError("Missing file: {}".format(csv_path))

    symbol, interval = extract_symbol_interval(csv_filename)

    with psycopg2.connect(**PG_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM cryptobot.dim_market WHERE symbol = %s", (symbol,))
            res = cur.fetchone()
            if not res:
                raise ValueError("Market not found in dim_market: {}".format(symbol))
            market_id = res[0]

            cur.execute("SELECT 1 FROM cryptobot.dim_interval WHERE interval_code = %s", (interval,))
            if not cur.fetchone():
                raise ValueError("Interval not found in dim_interval: {}".format(interval))

            rows = []
            with csv_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append((
                        market_id,
                        interval,
                        parse_utc(r["open_time"]),
                        parse_utc(r["close_time"]),
                        float(r["open"]),
                        float(r["high"]),
                        float(r["low"]),
                        float(r["close"]),
                        float(r["volume_base"]),
                        to_float(r.get("quote_volume")),
                        to_int(r.get("trade_count")),
                    ))

            if not rows:
                return 0

            sql = """
                INSERT INTO cryptobot.fact_market_price (
                    market_id, interval_code,
                    open_time, close_time,
                    open, high, low, close,
                    volume_base, quote_volume, trade_count
                )
                VALUES %s
                ON CONFLICT (market_id, interval_code, open_time) DO NOTHING
            """

            execute_values(cur, sql, rows, page_size=2000)

    print("[OK] {} -> processed {} rows (duplicates ignored)".format(csv_filename, len(rows)))
    return len(rows)


if __name__ == "__main__":
    files = [
    "binance_BTCUSDT_1h_5_parsed.csv",
    "binance_ETHUSDT_1h_10_parsed.csv",
    "binance_ETHBTC_4h_5_parsed.csv",
    "binance_BTCUSDT_1h_500_parsed.csv",
]


    total = 0
    for f in files:
        total += load_csv_into_fact_market_price(f)

    print("\n=== Done: processed {} rows ===".format(total))
