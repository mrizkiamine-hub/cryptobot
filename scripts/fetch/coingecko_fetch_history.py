import json
import time
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"
SLEEP_SEC = 3.0  # anti rate-limit (simple)

# mapping simple (tu peux en ajouter)
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

def fetch_market_chart(coin_id: str, vs_currency: str, days: int, max_retries: int = 6):
    url = BASE_URL.format(id=coin_id)
    params = {"vs_currency": vs_currency, "days": days, "interval": "daily"}

    wait = 5  # seconds
    for attempt in range(1, max_retries + 1):
        r = requests.get(url, params=params, timeout=20)

        # Rate limit -> backoff
        if r.status_code == 429:
            print(f"[WARN] 429 rate limit for {coin_id} {vs_currency}. Retry {attempt}/{max_retries} in {wait}s...")
            time.sleep(wait)
            wait = min(wait * 2, 120)  # cap 2 minutes
            continue

        r.raise_for_status()
        return r.json()

    raise RuntimeError(f"Rate limit persists after {max_retries} retries for {coin_id} {vs_currency}")

def save_json(obj, filename: str) -> Path:
    path = DATA_DIR / filename
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print(f"[OK] saved -> {path}")
    return path

if __name__ == "__main__":
    # Exemple : 365 jours d’historique
    DAYS = 365
    SYMBOLS = ["SOL"]

    for sym in SYMBOLS:
        coin_id = COINGECKO_IDS[sym]

        data_usd = fetch_market_chart(coin_id, "usd", DAYS)
        save_json(data_usd, f"coingecko_{sym}_usd_{DAYS}d.json")
        time.sleep(SLEEP_SEC)

        data_eur = fetch_market_chart(coin_id, "eur", DAYS)
        save_json(data_eur, f"coingecko_{sym}_eur_{DAYS}d.json")
        time.sleep(SLEEP_SEC)
