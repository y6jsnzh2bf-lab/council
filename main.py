
import json
from datetime import datetime, timezone

from engine.bitkub import get_symbols, get_all_tickers


def main():
    symbols = get_symbols()
    tickers = get_all_tickers()

    # Ticker API ส่งกลับมาเป็นรายการข้อมูล
    if not isinstance(tickers, list):
        raise TypeError(
            f"Unexpected ticker format: {type(tickers).__name__}"
        )

    active_symbols = set(symbols)
    market = [
        item for item in tickers
        if item.get("symbol") in active_symbols
    ]

    print("=== AI TRADING COUNCIL ===")
    print("Scan time:", datetime.now(timezone.utc).isoformat())
    print("Active pairs:", len(active_symbols))
    print("Pairs with ticker data:", len(market))

    print("\n=== TOP 10 BY 24H CHANGE ===")
    ranked = sorted(
        market,
        key=lambda x: float(x.get("percent_change", 0)),
        reverse=True
    )

    for item in ranked[:10]:
        print(
            item["symbol"],
            "Price:", item.get("last"),
            "24h:", item.get("percent_change"), "%"
        )

    with open("market.json", "w", encoding="utf-8") as file:
        json.dump(market, file, ensure_ascii=False, indent=2)

    print("\nSaved market.json")


if __name__ == "__main__":
    main()
