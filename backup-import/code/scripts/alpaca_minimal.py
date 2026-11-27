#!/usr/bin/env python3
"""Wrapper minimal Alpaca (paper trading) sans SDK, variables officielles."""
import os
import sys
import json
import requests
from urllib.parse import urljoin

API_KEY = os.getenv("APCA_API_KEY_ID", "")
API_SECRET = os.getenv("APCA_API_SECRET_KEY", "")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

session = requests.Session()
session.headers.update({
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET,
})


def account():
    r = session.get(urljoin(BASE_URL, "v2/account"), timeout=20)
    r.raise_for_status()
    return r.json()


def positions():
    r = session.get(urljoin(BASE_URL, "v2/positions"), timeout=20)
    r.raise_for_status()
    return r.json()


def latest_price(symbol: str):
    # Documentation endpoint pour le dernier trade :
    # https://docs.alpaca.markets/reference/stock_latest_trade
    url = urljoin(BASE_URL, f"v2/stocks/{symbol}/trades/latest")
    r = session.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def submit_order(symbol: str, qty: int, side: str, order_type: str = "market", time_in_force: str = "gtc"):
    payload = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": order_type,
        "time_in_force": time_in_force,
    }
    r = session.post(urljoin(BASE_URL, "v2/orders"), json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "account"
    if action == "account":
        print(json.dumps(account(), indent=2, ensure_ascii=False))
    elif action == "positions":
        print(json.dumps(positions(), indent=2, ensure_ascii=False))
    elif action == "price":
        sym = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
        print(json.dumps(latest_price(sym), indent=2, ensure_ascii=False))
    elif action == "buy":
        sym, qty = sys.argv[2], int(sys.argv[3])
        print(json.dumps(submit_order(sym, qty, "buy"), indent=2, ensure_ascii=False))
    elif action == "sell":
        sym, qty = sys.argv[2], int(sys.argv[3])
        print(json.dumps(submit_order(sym, qty, "sell"), indent=2, ensure_ascii=False))
    else:
        print("usage: account|positions|price <SYMBOL>|buy|sell <SYMBOL> <QTY>")
        sys.exit(1)


if __name__ == "__main__":
    main()
