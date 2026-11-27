#!/usr/bin/env python3
"""Bot crypto : scan, score, achat, DCA, alertes Telegram."""
import os
import time
import json
from pathlib import Path

from binance_api import get_klines, get_price, get_account, create_market_buy
from database import init, add_trade, log
from scorer import score_symbol
from risk import sizing, dca_amounts, CAPITAL_USD, RISK_PER_TRADE
try:
    from telegram_alerts import bot_status, trade_buy, sell_alert
    TELEGRAM_ENABLED = True
except Exception as e:
    TELEGRAM_ENABLED = False
    bot_status = lambda *a, **k: None
    trade_buy = lambda *a, **k: None
    sell_alert = lambda *a, **k: None

BOT_PAPER = os.getenv("BOT_PAPER", "false").lower() == "true"
SYMBOLS = [s.strip() for s in os.getenv("BOT_SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT,DOGEUSDT").split(",") if s.strip()]
MIN_SCORE = int(os.getenv("BOT_MIN_SCORE", "70"))
MAX_POSITIONS = int(os.getenv("BOT_MAX_POSITIONS", "2"))
STATE_PATH = Path(__file__).with_name("state.json")


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"positions": {}, "dca_index": {}, "last_btc_price": None}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state))


def fetch_btc_24h_change():
    try:
        k = get_klines("BTCUSDT", interval="1d", limit=2)
        if len(k) >= 2:
            prev = float(k[-2][4])
            last = float(k[-1][4])
            if prev > 0:
                return (last - prev) / prev
    except Exception as e:
        log("ERROR", f"btc fetch fail: {e}")
    return 0.0


def scan_once():
    state = load_state()
    btc_drop = fetch_btc_24h_change()
    if btc_drop < -0.05:
        log("WARN", f"BTC 24h drop {btc_drop:.2%}, achat suspendu")
        bot_status(f"⚠️ BTC chute de {btc_drop:.2%} en 24h : achat suspendu.")
        return

    best = None
    for sym in SYMBOLS:
        try:
            klines = get_klines(sym, interval="1d", limit=200)
            info = score_symbol(sym, klines)
        except Exception as e:
            log("ERROR", f"score fail {sym}: {e}")
            continue
        if info["score"] >= MIN_SCORE and (best is None or info["score"] > best["score"]):
            best = (sym, info)

    if not best:
        log("INFO", "Aucun score >= 75")
        return

    sym, info = best
    if len(state.get("positions", {})) >= MAX_POSITIONS:
        log("INFO", "Max positions atteint")
        return

    price = float(get_price(sym)["price"])
    qty = sizing(price)
    dca_idx = state.get("dca_index", {}).get(sym, 0)
    amount = dca_amounts()[dca_idx]

    # SL / TP basé sur ATR
    atr_val = 0.0
    try:
        from backtest import atr
        klines = get_klines(sym, interval="1d", limit=20)
        bars = [{"h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in klines]
        atr_val = atr(bars, 14) or price * 0.02
    except Exception:
        atr_val = price * 0.02  # fallback 2%
    sl = round(price - atr_val, 8)
    tp = round(price + atr_val * 2.0, 8)
    rr = 2.0

    try:
        if BOT_PAPER:
            order = {"clientOrderId": f"paper_{int(time.time())}", "fills": [{"qty": str(qty), "price": str(price)}]}
        else:
            order = create_market_buy(sym, amount)
        add_trade(sym, "BUY", qty, price, 0.0, order.get("clientOrderId", ""))
        state.setdefault("positions", {})[sym] = {
            "entry_price": price,
            "qty": qty,
            "dca_index": dca_idx,
        }
        state.setdefault("dca_index", {})[sym] = min(dca_idx + 1, len(dca_amounts()) - 1)
        save_state(state)
        trade_buy(
            symbol=sym,
            price=price,
            qty=qty,
            usd=amount,
            score=info["score"],
            tech=info["tech"],
            fund=info["fund"],
            sent=info["sent"],
            sl=sl,
            tp=tp,
            rr=rr,
        )
        log("INFO", f"buy {sym} @ {price}")
    except Exception as e:
        log("ERROR", f"buy fail {sym}: {e}")
        bot_status(f"❌ Erreur achat {sym}: {e}")


if __name__ == "__main__":
    init()
    if TELEGRAM_ENABLED:
        bot_status("🤖 Bot crypto démarré")
    while True:
        try:
            scan_once()
        except Exception as e:
            log("ERROR", f"loop error: {e}")
        time.sleep(3600)
