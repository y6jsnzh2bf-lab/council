
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.bitkub.com"

def get_symbols():
    """ดึงรายชื่อคู่เหรียญจาก Bitkub"""
    url = f"{BASE_URL}/api/v3/market/symbols"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    if data.get("error") != 0:
        raise RuntimeError(f"Bitkub API error: {data}")

    symbols = data.get("result", [])

    return [
        item["symbol"]
        for item in symbols
        if item.get("status") == "active"
    ]


def get_all_tickers():
    """ดึงข้อมูลตลาดจาก Bitkub"""
    url = f"{BASE_URL}/api/v3/market/ticker"
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict) and data.get("error", 0) != 0:
        raise RuntimeError(f"Bitkub API error: {data}")

    return data


def main():
    symbols = get_symbols()
    tickers = get_all_tickers()

    print("BITKUB MARKET SCAN")
    print("Time:", datetime.now(timezone.utc).isoformat())
    print("Active pairs:", len(symbols))
    print("Ticker response type:", type(tickers).__name__)

    print("Sample symbols:", symbols[:10])
    print("Sample ticker data:", str(tickers)[:2000])


if __name__ == "__main__":
    main()
