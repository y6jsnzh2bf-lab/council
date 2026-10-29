
def calculate_ema(values, period):
    if len(values) < period:
        return None

    multiplier = 2 / (period + 1)
    ema = sum(values[:period]) / period

    for value in values[period:]:
        ema = (value - ema) * multiplier + ema

    return ema


def calculate_rsi(values, period=14):
    if len(values) <= period:
        return None

    gains = []
    losses = []

    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_macd(values):
    ema12 = calculate_ema(values, 12)
    ema26 = calculate_ema(values, 26)

    if ema12 is None or ema26 is None:
        return None

    return ema12 - ema26


def calculate_atr(candles, period=14):
    if len(candles) <= period:
        return None

    true_ranges = []

    for i in range(1, len(candles)):
        high = float(candles[i]["high"])
        low = float(candles[i]["low"])
        previous_close = float(candles[i - 1]["close"])

        true_range = max(
            high - low,
            abs(high - previous_close),
            abs(low - previous_close)
        )

        true_ranges.append(true_range)

    atr = sum(true_ranges[:period]) / period

    for value in true_ranges[period:]:
        atr = (atr * (period - 1) + value) / period

    return atr


def analyze_candles(candles):
    if len(candles) < 50:
        return None

    closes = [float(candle["close"]) for candle in candles]

    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    rsi = calculate_rsi(closes, 14)
    macd = calculate_macd(closes)
    atr = calculate_atr(candles, 14)

    return {
        "price": closes[-1],
        "ema20": ema20,
        "ema50": ema50,
        "rsi14": rsi,
        "macd": macd,
        "atr14": atr,
        "trend": (
            "BULLISH" if ema20 > ema50
            else "BEARISH" if ema20 < ema50
            else "NEUTRAL"
        )
    }
