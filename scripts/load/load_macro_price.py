import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

import psycopg2
from psycopg2.extras import execute_values

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"


PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "dst_db",
    "user": "daniel",
    "password": "datascientest",
}

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "MATIC": "polygon",
    "ATOM": "cosmos",
    "TRX": "tron",
    "USDC": "usd-coin",
    "DAI": "dai",
}

def ms_to_date(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.date().isoformat()

def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def build_daily_map(data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Retourne un dict:
      date -> {"price": x, "market_cap": y}
    basé sur les listes 'prices' et 'market_caps'
    """
    out: Dict[str, Dict[str, float]] = {}
    for ts, val in data.get("prices", []):
        d = ms_to_date(ts)
        out.setdefault(d, {})["price"] = float(val)
    for ts, val in data.get("market_caps", []):
        d = ms_to_date(ts)
        out.setdefault(d, {})["market_cap"] = float(val)
    return out

def get_asset_id(cur, symbol: str) -> int:
    cur.execute("SELECT id FROM cryptobot.dim_asset WHERE symbol = %s", (symbol,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Asset not found in dim_asset: {symbol}")
    return int(row[0])

def upsert_fact_macro(symbol: str, days: int) -> int:
    usd_path = DATA_DIR / f"coingecko_{symbol}_usd_{days}d.json"
    eur_path = DATA_DIR / f"coingecko_{symbol}_eur_{days}d.json"

    if not usd_path.exists() or not eur_path.exists():
        raise FileNotFoundError(f"Missing JSON for {symbol}: {usd_path.name} / {eur_path.name}")

    usd = build_daily_map(load_json(usd_path))
    eur = build_daily_map(load_json(eur_path))

    all_dates = sorted(set(usd.keys()) | set(eur.keys()))

    with psycopg2.connect(**PG_CONFIG) as conn:
        with conn.cursor() as cur:
            asset_id = get_asset_id(cur, symbol)

            rows: List[Tuple] = []
            for d in all_dates:
                price_usd = usd.get(d, {}).get("price")
                price_eur = eur.get(d, {}).get("price")
                market_cap = usd.get(d, {}).get("market_cap")  # market cap en USD
                rows.append((asset_id, d, price_usd, price_eur, market_cap))

            sql = """
                INSERT INTO cryptobot.fact_macro_price (asset_id, date, price_usd, price_eur, market_cap)
                VALUES %s
                ON CONFLICT (asset_id, date) DO UPDATE
                SET price_usd = EXCLUDED.price_usd,
                    price_eur = EXCLUDED.price_eur,
                    market_cap = EXCLUDED.market_cap
            """

            execute_values(cur, sql, rows, page_size=2000)

    print(f"[OK] macro loaded: {symbol} -> {len(all_dates)} jours")
    return len(all_dates)

if __name__ == "__main__":
    DAYS = 365
    SYMBOLS = ["BTC", "ETH", "SOL"]  # <-- doit matcher le fetch

    total = 0
    for s in SYMBOLS:
        total += upsert_fact_macro(s, DAYS)

    print(f"\n=== Done: {total} lignes upsertées dans fact_macro_price ===")
