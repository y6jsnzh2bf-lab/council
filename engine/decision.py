
def make_decision(analysis):
    """
    Convert technical indicators into BUY / SELL / HOLD.
    This is an informational analysis, not an execution signal.
    """

    indicators = analysis["indicators"]
    score = analysis["score"]["total"]
    trend = analysis["trend"]

    rsi = indicators["rsi14"]
    macd = indicators["macd"]
    adx = indicators["adx14"]
    volume_ratio = indicators["volume"]["ratio"]
    bollinger = indicators["bollinger"]

    reasons = []
    risks = []

    bullish = 0
    bearish = 0

    # 1. Trend: EMA
    if indicators["ema20"] > indicators["ema50"]:
        bullish += 1
        reasons.append("EMA20 is above EMA50")
    else:
        bearish += 1
        reasons.append("EMA20 is below EMA50")

    # 2. RSI
    if 50 <= rsi <= 70:
        bullish += 1
        reasons.append("RSI shows positive momentum")
    elif rsi < 30:
        bullish += 1
        risks.append("RSI is oversold; reversal is not confirmed")
    elif rsi > 70:
        bearish += 1
        risks.append("RSI is overbought")
    else:
        bearish += 1
        reasons.append("RSI shows weak momentum")

    # 3. MACD
    if macd["histogram"] > 0:
        bullish += 1
        reasons.append("MACD histogram is positive")
    else:
        bearish += 1
        reasons.append("MACD histogram is negative")

    # 4. ADX: trend strength
    if adx >= 25:
        reasons.append("ADX confirms a strong trend")
    else:
        risks.append("ADX indicates a weak or unclear trend")

    # 5. Volume
    if volume_ratio >= 1.5:
        reasons.append("Trading volume is significantly above average")
    elif volume_ratio < 0.5:
        risks.append("Trading volume is unusually low")

    # 6. Bollinger Bands
    if indicators["bollinger"]["width_percent"] > 10:
        risks.append("High volatility detected")

    # Decision
    if (
        score >= 7
        and bullish >= 2
        and trend == "BULLISH"
        and macd["histogram"] > 0
        and adx >= 25
    ):
        decision = "BUY"

    elif (
        score <= 3
        and bearish >= 2
        and trend == "BEARISH"
        and macd["histogram"] < 0
        and adx >= 25
    ):
        decision = "SELL"

    else:
        decision = "HOLD"

    # Confidence is signal agreement, not probability of profit.
    agreement = bullish + bearish

    if agreement == 0:
        confidence = "LOW"
    else:
        strongest = max(bullish, bearish) / agreement

        if strongest >= 0.85 and adx >= 25:
            confidence = "HIGH"
        elif strongest >= 0.65:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

    return {
        "decision": decision,
        "confidence": confidence,
        "bullish_signals": bullish,
        "bearish_signals": bearish,
        "reasons": reasons,
        "risks": risks
