import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "cryptobot"
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed" / "macro_daily.json"

ASSETS = ["BTC", "ETH", "SOL"]

def ms_to_date(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def build_map(obj: dict) -> dict:
    out = {}
    for ts, val in obj.get("prices", []):
        out.setdefault(ms_to_date(ts), {})["price"] = float(val)
    for ts, val in obj.get("market_caps", []):
        out.setdefault(ms_to_date(ts), {})["market_cap"] = float(val)
    return out

def main():
    docs = []

    for asset in ASSETS:
        usd_path = RAW / f"coingecko_{asset}_usd_365d.json"
        eur_path = RAW / f"coingecko_{asset}_eur_365d.json"

        if not usd_path.exists() or not eur_path.exists():
            print(f"[SKIP] missing {asset} files")
            continue

        usd = build_map(read_json(usd_path))
        eur = build_map(read_json(eur_path))

        for d in sorted(set(usd.keys()) | set(eur.keys())):
            docs.append({
                "asset": asset,
                "date": d,
                "price_usd": usd.get(d, {}).get("price"),
                "price_eur": eur.get(d, {}).get("price"),
                "market_cap_usd": usd.get(d, {}).get("market_cap"),
                "source": "COINGECKO"
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] wrote {len(docs)} docs -> {OUT}")

if __name__ == "__main__":
    main()
