
import json
import time
from datetime import datetime, timezone

from engine.bitkub import get_symbols, get_candlesticks
from engine.indicators import analyze_candles


def main():
    symbols = get_symbols()

    print("=== AI TRADING COUNCIL ===")
    print("Scan time:", datetime.now(timezone.utc).isoformat())
    print("Active pairs:", len(symbols))

    results = []
    failed = []

    for index, symbol in enumerate(symbols, start=1):
        try:
            candles = get_candlesticks(
                symbol=symbol,
                timeframe="15",
                hours=36
            )

            analysis = analyze_candles(candles)

            if analysis is not None:
                analysis["symbol"] = symbol
                results.append(analysis)

            print(f"[{index}/{len(symbols)}] {symbol}: OK")

        except Exception as error:
            failed.append({
                "symbol": symbol,
                "error": str(error)
            })
            print(f"[{index}/{len(symbols)}] {symbol}: FAILED")

        time.sleep(0.2)

    # จัดอันดับด้วย RSI และแนวโน้ม
    for item in results:
        score = 0

        if item["trend"] == "BULLISH":
            score += 2

        if 50 <= item["rsi14"] <= 70:
            score += 1

        if item["macd"] > 0:
            score += 1

        item["score"] = score

    ranked = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    output = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "pairs_scanned": len(symbols),
        "pairs_analyzed": len(results),
        "pairs_failed": len(failed),
        "ranked_market": ranked,
        "failed_pairs": failed
    }

    with open("analysis.json", "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print("\n=== TOP 10 TECHNICAL SCORES ===")

    for item in ranked[:10]:
        print(
            item["symbol"],
            "Score:", item["score"],
            "Trend:", item["trend"],
            "RSI:", round(item["rsi14"], 2)
        )

    print("\nAnalyzed:", len(results))
    print("Failed:", len(failed))
    print("Saved: analysis.json")


if __name__ == "__main__":
    main()
    main()
