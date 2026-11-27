#!/usr/bin/env python3
"""Scoring crypto : technique 50, fondamental 30, sentiment 20.

- Technique (0-50) : EMA cross, RSI, volume, tendance
- Fondamental (0-30) : Fear & Greed Index (web)
- Sentiment (0-20) : contexte marché
"""
import json
from pathlib import Path
from urllib.request import Request, urlopen

from database import add_score


def technical_score(symbol: str, closes, volumes) -> int:
    score = 0
    if len(closes) >= 200:
        ema50 = sum(closes[-50:]) / 50
        ema200 = sum(closes[-200:]) / 200
        if ema50 > ema200:
            score += 20
        elif ema50 < ema200 * 0.9:
            score -= 10
    if len(closes) >= 15:
        diffs = [closes[i] - closes[i-1] for i in range(-14, 0)]
        gains = sum(d for d in diffs if d > 0) / 14
        losses = sum(-d for d in diffs if d < 0) / 14
        rs = gains / losses if losses else 100
        rsi = 100 - 100 / (1 + rs)
        if 40 <= rsi <= 60:
            score += 15
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            score += 8
    if len(volumes) >= 20:
        avg_vol = sum(volumes[-20:]) / 20
        if volumes[-1] > avg_vol * 1.5:
            score += 15
        elif volumes[-1] > avg_vol:
            score += 8
    if len(closes) >= 5:
        pct_5d = (closes[-1] - closes[-5]) / closes[-5]
        if pct_5d > 0.01:
            score += 5
        elif pct_5d < -0.03:
            score -= 5
    return max(0, min(50, score))


_FNG_CACHE = {"value": 50, "ts": 0}


def _fetch_fear_greed() -> int:
    import time
    now = time.time()
    if now - _FNG_CACHE["ts"] < 3600:
        return _FNG_CACHE["value"]
    try:
        req = Request(
            "https://api.alternative.me/fng/?limit=1",
            headers={"User-Agent": "Hermes-Crypto-Bot/1.0"},
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            _FNG_CACHE["value"] = int(data["data"][0]["value"])
            _FNG_CACHE["ts"] = now
            return _FNG_CACHE["value"]
    except Exception:
        return 50


def fundamental_score(symbol: str) -> int:
    fng = _fetch_fear_greed()
    score = 0
    if fng <= 25:
        score += 25
    elif fng <= 45:
        score += 20
    elif fng <= 55:
        score += 15
    elif fng <= 75:
        score += 10
    else:
        score += 5
    if symbol == "BTCUSDT":
        score += 5
    return min(30, score)


def sentiment_score(symbol: str) -> int:
    score = 10
    try:
        fng = _fetch_fear_greed()
        if 25 <= fng <= 55:
            score += 5
    except Exception:
        pass
    if symbol in ("BTCUSDT", "ETHUSDT"):
        score += 3
    elif symbol in ("SOLUSDT", "BNBUSDT"):
        score += 2
    return min(20, max(5, score))


def score_symbol(symbol: str, klines):
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    tech = technical_score(symbol, closes, volumes)
    fund = fundamental_score(symbol)
    sent = sentiment_score(symbol)
    total = tech + fund + sent
    add_score(symbol, total, tech, fund, sent)
    return {"symbol": symbol, "score": total, "tech": tech, "fund": fund, "sent": sent}
