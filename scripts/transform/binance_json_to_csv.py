import json
from pathlib import Path
from datetime import datetime

# === Paths ===
BASE_DIR = Path(__file__).resolve().parents[2]   # ~/cryptobot
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def parse_binance_file(input_filename: str, output_filename: str) -> Path:
    in_path = RAW_DIR / input_filename
    out_path = PROCESSED_DIR / output_filename

    data = json.loads(in_path.read_text(encoding="utf-8"))

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"Unexpected format in {input_filename}")

    with out_path.open("w", encoding="utf-8") as f:
        f.write(
            "open_time,close_time,open,high,low,close,"
            "volume_base,quote_volume,trade_count\n"
        )

        for kline in data:
            open_time = datetime.utcfromtimestamp(kline[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            close_time = datetime.utcfromtimestamp(kline[6] / 1000).strftime("%Y-%m-%d %H:%M:%S")

            line = (
                f"{open_time},{close_time},"
                f"{kline[1]},{kline[2]},{kline[3]},{kline[4]},"
                f"{kline[5]},{kline[7]},{kline[8]}\n"
            )
            f.write(line)

    print(f"[OK] {input_filename} -> {out_path.name} ({len(data)} lignes)")
    return out_path


if __name__ == "__main__":
    parse_binance_file("binance_BTCUSDT_1h_5.json",  "binance_BTCUSDT_1h_5_parsed.csv")
    parse_binance_file("binance_ETHUSDT_1h_10.json", "binance_ETHUSDT_1h_10_parsed.csv")
    parse_binance_file("binance_ETHBTC_4h_5.json",   "binance_ETHBTC_4h_5_parsed.csv")
    parse_binance_file(
        "binance_BTCUSDT_1h_2025-09-01_to_2025-12-01.json",
        "binance_BTCUSDT_1h_2025-09-01_to_2025-12-01_parsed.csv"
    )
