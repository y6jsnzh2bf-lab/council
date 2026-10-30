
import json
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from engine.bitkub import get_symbols, get_candlesticks
from engine.indicators import analyze_candles
from engine.decision import make_decision

MAX_WORKERS = 363


def analyze_symbol(symbol):
    candles = get_candlesticks(
        symbol=symbol,
        timeframe="15",
        hours=36
    )

    analysis = analyze_candles(candles)

    if analysis is None:
        return {
            "symbol": symbol,
            "error": "Insufficient candle data",
            "candle_count": len(candles)
        }

    analysis["symbol"] = symbol
    analysis["candle_count"] = len(candles)

    decision = make_decision(analysis)
    analysis["decision"] = decision

    return analysis


def main():
    symbols = get_symbols()

    print("=== AI TRADING COUNCIL ===")
    print("Scan time:", datetime.now(timezone.utc).isoformat())
    print("Active pairs:", len(symbols))
    print("Workers:", MAX_WORKERS)

    results = []
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(analyze_symbol, symbol): symbol
            for symbol in symbols
        }

        for index, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]

            try:
                analysis = future.result()

                if analysis is None:
                    failed.append({
                        "symbol": symbol,
                        "error": "Insufficient candle data"
                    })
                    continue

                if "error" in analysis:
                    failed.append(analysis)
                    print(
                        f"[{index}/{len(symbols)}] {symbol}: "
                        f"{analysis['candle_count']} candles"
                    )
                    continue

                results.append(analysis)

                print(
                    f"[{index}/{len(symbols)}] {symbol}: "
                    f"Score {analysis['score']['total']}/"
                    f"{analysis['score']['max']}"
                )

            except Exception as error:
                failed.append({
                    "symbol": symbol,
                    "error": str(error)
                })

                print(f"[{index}/{len(symbols)}] {symbol}: FAILED")

    ranked = sorted(
        results,
        key=lambda x: x["score"]["total"],
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
        indicators = item["indicators"]

        print(
            item["symbol"],
            "Decision:", item["decision"]["decision"],
            "Confidence:", item["decision"]["confidence"],
            "Score:", item["score"]["total"],
            "Trend:", item["trend"],
            "RSI:", round(indicators["rsi14"], 2)
        )

    print("\n=== SCAN SUMMARY ===")
    print("Analyzed:", len(results))
    print("Failed:", len(failed))
    print("Saved: analysis.json")
    print("\n=== FAILED PAIRS DETAILS ===")

    for item in failed[:20]:
        print(item["symbol"], "->", item["error"])


if __name__ == "__main__":
    main()
