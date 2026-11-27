#!/usr/bin/env python3
"""Test read-only Binance connectivity and basic scoring."""
from binance_api import get_price, get_klines
from database import init

if __name__ == "__main__":
    init()
    sym = "BTCUSDT"
    price = get_price(sym)
    print("price:", price)
    klines = get_klines(sym, interval="1d", limit=5)
    print("klines:", len(klines))
    from scorer import technical_score
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    print("tech_score:", technical_score(sym, closes + [0]*50, volumes + [0]*20))
