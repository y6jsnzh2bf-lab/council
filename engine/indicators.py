
from math import sqrt


# ==========================================
# BASIC UTILITIES
# ==========================================

def sma(values, period):
    if len(values) < period:
        return None

    return sum(values[-period:]) / period


def calculate_ema_series(values, period):
    if len(values) < period:
        return []

    multiplier = 2 / (period + 1)

    ema = sum(values[:period]) / period
    result = [None] * (period - 1) + [ema]

    for value in values[period:]:
        ema = (value - ema) * multiplier + ema
        result.append(ema)

    return result


def calculate_ema(values, period):
    series = calculate_ema_series(values, period)
    return series[-1] if series else None


# ==========================================
# RSI
# ==========================================

def calculate_rsi(values, period=14):
    if len(values) <= period:
        return None

    changes = [
        values[i] - values[i - 1]
        for i in range(1, len(values))
    ]

    gains = [max(x, 0) for x in changes]
    losses = [max(-x, 0) for x in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(changes)):
        avg_gain = (
            avg_gain * (period - 1) + gains[i]
        ) / period

        avg_loss = (
            avg_loss * (period - 1) + losses[i]
        ) / period

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


# ==========================================
# MACD
# ==========================================

def calculate_macd(values):
    fast = calculate_ema_series(values, 12)
    slow = calculate_ema_series(values, 26)

    if not fast or not slow:
        return None

    macd_series = [
        fast[i] - slow[i]
        if fast[i] is not None and slow[i] is not None
        else None
        for i in range(len(values))
    ]

    valid_macd = [x for x in macd_series if x is not None]

    signal_series = calculate_ema_series(valid_macd, 9)

    if not signal_series:
        return None

    macd_line = macd_series[-1]
    signal_line = signal_series[-1]

    histogram = macd_line - signal_line

    return {
        "line": macd_line,
        "signal": signal_line,
        "histogram": histogram
    }


# ==========================================
# ATR
# ==========================================

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
        atr = (
            atr * (period - 1) + value
        ) / period

    return atr


# ==========================================
# VOLUME ANALYSIS
# ==========================================

def calculate_volume(candles, period=20):
    if len(candles) < period + 1:
        return None

    volumes = [
        float(candle["volume"])
        for candle in candles
    ]

    current = volumes[-1]
    average = sum(volumes[-period-1:-1]) / period

    ratio = current / average if average > 0 else None

    return {
        "current": current,
        "average": average,
        "ratio": ratio
    }


# ==========================================
# ADX
# ==========================================

def calculate_adx(candles, period=14):
    if len(candles) < period * 2 + 1:
        return None

    plus_dm = []
    minus_dm = []
    true_ranges = []

    for i in range(1, len(candles)):
        high = float(candles[i]["high"])
        low = float(candles[i]["low"])

        prev_high = float(candles[i - 1]["high"])
        prev_low = float(candles[i - 1]["low"])
        prev_close = float(candles[i - 1]["close"])

        up_move = high - prev_high
        down_move = prev_low - low

        plus_dm.append(
            up_move if up_move > down_move and up_move > 0 else 0
        )

        minus_dm.append(
            down_move if down_move > up_move and down_move > 0 else 0
        )

        true_ranges.append(max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        ))

    def wilder_smooth(values):
        result = [None] * len(values)

        current = sum(values[:period])
        result[period - 1] = current

        for i in range(period, len(values)):
            current = current - current / period + values[i]
            result[i] = current

        return result

    smoothed_tr = wilder_smooth(true_ranges)
    smoothed_plus = wilder_smooth(plus_dm)
    smoothed_minus = wilder_smooth(minus_dm)

    dx_values = []

    for i in range(len(true_ranges)):
        if smoothed_tr[i] is None or smoothed_tr[i] == 0:
            dx_values.append(None)
            continue

        plus_di = 100 * smoothed_plus[i] / smoothed_tr[i]
        minus_di = 100 * smoothed_minus[i] / smoothed_tr[i]

        total = plus_di + minus_di

        dx_values.append(
            100 * abs(plus_di - minus_di) / total
            if total > 0 else 0
        )

    valid_dx = [x for x in dx_values if x is not None]

    if len(valid_dx) < period:
        return None

    adx = sum(valid_dx[:period]) / period

    for value in valid_dx[period:]:
        adx = (adx * (period - 1) + value) / period

    return adx


# ==========================================
# BOLLINGER BANDS
# ==========================================

def calculate_bollinger(values, period=20, multiplier=2):
    if len(values) < period:
        return None

    window = values[-period:]
    middle = sum(window) / period

    variance = sum(
        (x - middle) ** 2 for x in window
    ) / period

    deviation = sqrt(variance)

    upper = middle + multiplier * deviation
    lower = middle - multiplier * deviation

    width = (
        (upper - lower) / middle * 100
        if middle != 0 else None
    )

    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
        "width_percent": width
    }


# ==========================================
# SUPPORT / RESISTANCE
# ==========================================

def calculate_support_resistance(candles, period=20):
    if len(candles) < period:
        return None

    window = candles[-period:]

    support = min(float(c["low"]) for c in window)
    resistance = max(float(c["high"]) for c in window)

    return {
        "support": support,
        "resistance": resistance
    }


# ==========================================
# TECHNICAL SCORE
# ==========================================

def calculate_score(
    price,
    ema20,
    ema50,
    rsi,
    macd,
    adx,
    volume,
    bollinger
):
    score = 0
    max_score = 10
    reasons = []

    # EMA trend: 0-2
    if ema20 is not None and ema50 is not None:
        if ema20 > ema50:
            score += 1
            reasons.append("EMA20 above EMA50")

        if price > ema20:
            score += 1
            reasons.append("Price above EMA20")

    # RSI: 0-2
    if rsi is not None:
        if 50 <= rsi <= 65:
            score += 2
            reasons.append("Positive RSI momentum")
        elif 65 < rsi < 70:
            score += 1
            reasons.append("Strong RSI momentum")

    # MACD: 0-2
    if macd is not None:
        if macd["line"] > macd["signal"]:
            score += 1
            reasons.append("MACD bullish")

        if macd["histogram"] > 0:
            score += 1
            reasons.append("MACD histogram positive")

    # ADX: 0-2
    if adx is not None:
        if adx >= 25:
            score += 1
            reasons.append("Strong trend")

        if adx >= 25 and macd is not None:
            if macd["line"] > macd["signal"]:
                score += 1

    # Volume: 0-1
    if volume is not None and volume["ratio"] is not None:
        if volume["ratio"] >= 1.5:
            score += 1
            reasons.append("Volume above average")

    # Bollinger: 0-1
    if bollinger is not None:
        if price > bollinger["middle"]:
            score += 1
            reasons.append("Price above Bollinger middle")

    return {
        "total": score,
        "max": max_score,
        "reasons": reasons
    }


# ==========================================
# COMPLETE ANALYSIS
# ==========================================

def analyze_candles(candles):
    if len(candles) < 100:
        return None

    closes = [
        float(candle["close"])
        for candle in candles
    ]

    price = closes[-1]

    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)

    rsi = calculate_rsi(closes, 14)
    macd = calculate_macd(closes)

    atr = calculate_atr(candles, 14)
    volume = calculate_volume(candles, 20)
    adx = calculate_adx(candles, 14)

    bollinger = calculate_bollinger(closes, 20)
    levels = calculate_support_resistance(candles, 20)

    atr_percent = (
        atr / price * 100
        if atr is not None and price > 0
        else None
    )

    if ema20 is None or ema50 is None:
        return None

    if ema20 > ema50:
        trend = "BULLISH"
    elif ema20 < ema50:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"

    score = calculate_score(
        price,
        ema20,
        ema50,
        rsi,
        macd,
        adx,
        volume,
        bollinger
    )

    return {
        "price": price,

        "trend": trend,

        "indicators": {
            "rsi14": rsi,
            "ema20": ema20,
            "ema50": ema50,
            "macd": macd,
            "atr14": atr,
            "atr_percent": atr_percent,
            "adx14": adx,
            "volume": volume,
            "bollinger": bollinger,
            "support_resistance": levels
        },

        "score": score
    }
