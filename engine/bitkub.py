
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.bitkub.com"


def get_symbols():
    """ดึงรายชื่อคู่ตลาดจาก Bitkub"""
    url = f"{BASE_URL}/api/v3/market/symbols"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    if data.get("error") != 0:
        raise RuntimeError(f"Symbols API error: {data}")

    return [
        item["symbol"]
        for item in data.get("result", [])
        if item.get("status") == "active"
    ]


def get_all_tickers():
    """ดึง Ticker ของตลาดทั้งหมด"""
    url = f"{BASE_URL}/api/v3/market/ticker"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    # ตรวจสอบรูปแบบข้อมูล
    if isinstance(data, dict):
        if data.get("error", 0) != 0:
            raise RuntimeError(f"Ticker API error: {data}")

        # บาง API อาจห่อข้อมูลไว้ใน result
        data = data.get("result", data)

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        raise TypeError(
            f"Unexpected ticker response: {type(data).__name__}"
        )

    return data


def main():
    symbols = get_symbols()
    tickers = get_all_tickers()

    active = set(symbols)

    market = [
        item for item in tickers
        if item.get("symbol") in active
    ]

    print("=== BITKUB TICKER SCAN ===")
    print("Time:", datetime.now(timezone.utc).isoformat())
    print("Active pairs:", len(symbols))
    print("Ticker pairs:", len(tickers))
    print("Matched active pairs:", len(market))

    print("\n=== SAMPLE TICKER ===")

    if market:
        print(market[0])
    else:
        print("No matching ticker data found.")

    print("\n=== TOP 10 MARKET MOVERS ===")

    ranked = sorted(
        market,
        key=lambda x: float(x.get("percent_change", 0)),
        reverse=True
    )

    for item in ranked[:10]:
        print(
            item.get("symbol"),
            "Price:", item.get("last"),
            "Change:", item.get("percent_change"), "%"
        )


if __name__ == "__main__":
    main()

def get_candlesticks(symbol="THB_BTC", timeframe="15"):
    """ดึงข้อมูลแท่งเทียนผ่าน TradingView History API"""

    url = f"{BASE_URL}/tradingview/history"

    now = int(datetime.now(timezone.utc).timestamp())

    params = {
        "symbol": symbol,
        "resolution": timeframe,
        "from": now - 86400,
        "to": now
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if data.get("s") != "ok":
        raise RuntimeError(f"Candlestick API error: {data}")

    return data
