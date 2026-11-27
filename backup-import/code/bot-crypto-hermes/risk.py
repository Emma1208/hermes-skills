#!/usr/bin/env python3
"""Gestion du risque et DCA."""
from math import floor

CAPITAL_USD = float(__import__("os").getenv("BOT_CAPITAL", "10000"))
RISK_PER_TRADE = float(__import__("os").getenv("BOT_RISK", "0.01"))
MAX_POSITIONS = 2
INITIAL_ORDER_USD = min(CAPITAL_USD * RISK_PER_TRADE, 100.0)
DCA_LEVELS = [INITIAL_ORDER_USD * 1.3, INITIAL_ORDER_USD * 1.69, INITIAL_ORDER_USD * 2.2]
BTC_MAX_DROP_24H = 0.05


def sizing(price_usd: float) -> float:
    qty = INITIAL_ORDER_USD / price_usd
    # Binance contraintes : > 0.0001 BTC/USDT approx
    return max(round(qty, 6), 0.0001)


def dca_amounts():
    arr = [INITIAL_ORDER_USD] + DCA_LEVELS
    return arr
