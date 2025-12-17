import json
from pathlib import Path
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_binance_ohlcv(symbol: str, interval: str = "1h", limit: int = 500):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if not isinstance(data, list):
        raise RuntimeError(f"Erreur API Binance : {data}")

    print(f"[OK] {symbol} {interval} – {len(data)} bougies")
    print("Première bougie :", data[0])

    return data


def save_json(data, filename: str):
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Fichier sauvegardé : {path}\n")


if __name__ == "__main__":
    btc = fetch_binance_ohlcv("BTCUSDT", "1h", 5)
    save_json(btc, "binance_BTCUSDT_1h_5.json")

    eth = fetch_binance_ohlcv("ETHUSDT", "1h", 10)
    save_json(eth, "binance_ETHUSDT_1h_10.json")

    ethbtc = fetch_binance_ohlcv("ETHBTC", "4h", 5)
    save_json(ethbtc, "binance_ETHBTC_4h_5.json")
