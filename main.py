
import json
import time
from datetime import datetime, timezone

from engine.bitkub import get_symbols, get_candlesticks


def main():
    symbols = get_symbols()

    print("=== BITKUB CANDLE SCAN ===")
    print("Scan time:", datetime.now(timezone.utc).isoformat())
    print("Active pairs:", len(symbols))

    market_candles = {}
    failed = []

    for index, symbol in enumerate(symbols, start=1):
        try:
            candles = get_candlesticks(
                symbol=symbol,
                timeframe="15",
                hours=24
            )

            market_candles[symbol] = candles

            print(
                f"[{index}/{len(symbols)}] "
                f"{symbol}: {len(candles)} candles"
            )

        except Exception as error:
            failed.append({
                "symbol": symbol,
                "error": str(error)
            })

            print(f"[{index}/{len(symbols)}] {symbol}: FAILED")

        # เว้นระยะระหว่าง API requests
        time.sleep(0.2)

    output = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "timeframe": "15m",
        "pairs_requested": len(symbols),
        "pairs_successful": len(market_candles),
        "pairs_failed": len(failed),
        "market_candles": market_candles,
        "failed_pairs": failed
    }

    with open("market_candles.json", "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False)

    print("\n=== SCAN SUMMARY ===")
    print("Successful:", len(market_candles))
    print("Failed:", len(failed))
    print("Saved: market_candles.json")


if __name__ == "__main__":
    main()
