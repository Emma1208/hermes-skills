#!/usr/bin/env python3
"""Binance Spot client minimal : prix, ordres, soldes."""
import os
import time
import hmac
import hashlib
from urllib.parse import urlencode
from requests import Session

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BASE_URL = os.getenv("BINANCE_API_URL", "https://api.binance.com")

session = Session()
session.headers.update({"X-MBX-APIKEY": API_KEY})


def sign(params: dict):
    params["timestamp"] = int(time.time() * 1000)
    query = urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params


def get(path, params=None):
    r = session.get(f"{BASE_URL}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def post(path, params=None):
    params = sign(params or {})
    r = session.post(f"{BASE_URL}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def get_price(symbol: str):
    return get("/api/v3/ticker/price", {"symbol": symbol})


def get_klines(symbol: str, interval: str = "1d", limit: int = 200):
    return get("/api/v3/klines", {"symbol": symbol, "interval": interval, "limit": limit})


def get_account():
    return post("/api/v3/account")


def create_market_buy(symbol: str, quote_order_qty: float):
    return post("/api/v3/order", {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": f"{quote_order_qty:.2f}",
        "newClientOrderId": f"hermes_{int(time.time())}",
    })


def create_market_sell(symbol: str, quantity: float):
    return post("/api/v3/order", {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": f"{quantity:.6f}",
        "newClientOrderId": f"hermes_{int(time.time())}",
    })
