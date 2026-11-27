#!/usr/bin/env python3
"""Exemple minimal Alpaca : compte, positions, prix, ordre papier."""
import os
import sys
from alpaca_trade_api import REST

API_KEY = os.getenv("APCA_API_KEY_ID", "TA_CLÉ")
API_SECRET = os.getenv("APCA_API_SECRET_KEY", "TA_CLÉ_SECRÈTE")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

api = REST(API_KEY, API_SECRET, BASE_URL)

# 1) Compte
account = api.get_account()
print("compte:", account.status)
print("solde:", account.cash)
print("equity:", account.equity)

# 2) Positions
positions = api.list_positions()
print("positions:", len(positions))
for p in positions:
    print("-", p.symbol, "qte:", p.qty, "P&L:", p.unrealized_pl)

# 3) Prix
symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC/USD"
bars = api.get_latest_bar(symbol)
print("dernier_bar:", bars)

# 4) Ordre papier (exemple)
if len(sys.argv) > 3:
    side = sys.argv[2]
    qty = sys.argv[3]
    order = api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        type="market",
        time_in_force="gtc",
    )
    print("ordre:", order.status, order.client_order_id)
