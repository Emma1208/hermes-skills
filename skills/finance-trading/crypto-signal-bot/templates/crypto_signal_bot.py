#!/usr/bin/env python3
"""
Crypto Signal Bot - TEMPLATE (pure stdlib, validated live on Binance)
=====================================================================
Recupere cours crypto (Binance publique, sans cle API), calcule RSI(Wilder)+EMA,
detecte les signaux (repli dans tendance) et envoie sur Telegram.

Mode dry-run (sans token) : affiche les signaux dans la console.
Lancement : python3 crypto_signal_bot.py once   |   python3 crypto_signal_bot.py

⚠️ Pas un conseil en investissement. DYOR.
"""
import time
import sys
import json
import urllib.request
import urllib.parse

CONFIG = {
    "symbols": ["SOLUSDT", "DOGEUSDT", "LTCUSDT"],  # paires VALIDEES (backtest > seuil)
    "interval": "15m",
    "limit": 200,
    "rsi_period": 14,
    "ema_fast": 20,
    "ema_slow": 100,
    "rsi_oversold": 30,
    "rsi_overbought": 60,
    "tp_pct": 0.03,
    "sl_pct": 0.02,
    "rr": 3.0,                  # Risk/Reward : TP = SL x rr  (breakeven WR = 1/(1+rr) = 25%)
    "loop_seconds": 60,
    "telegram_token": "",       # ex: "123456:ABC-DEF..."
    "telegram_chat_id": "",     # ex: "-1001234567890"
    "dry_run": True,
}

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"


def fetch_klines(symbol, interval, limit, retries=3):
    params = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "limit": limit})
    url = f"{BINANCE_KLINES}?{params}"
    last_err = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            closes = [float(row[4]) for row in data]
            highs = [float(row[2]) for row in data]
            lows = [float(row[3]) for row in data]
            return closes, highs, lows
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise last_err


def ema(values, period):
    if len(values) < period:
        return [None] * len(values)
    k = 2 / (period + 1)
    out = [None] * (period - 1)
    out.append(sum(values[:period]) / period)
    for v in values[period:]:
        out.append(out[-1] + k * (v - out[-1]))
    return out


def rsi(closes, period):
    if len(closes) <= period:
        return [None] * len(closes)
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    out = [None] * period
    avg_g = sum(gains[:period]) / period
    avg_l = sum(losses[:period]) / period
    rs = (avg_g / avg_l) if avg_l != 0 else 100
    out.append(100 - 100 / (1 + rs))
    for i in range(period, len(deltas)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
        rs = (avg_g / avg_l) if avg_l != 0 else 100
        out.append(100 - 100 / (1 + rs))
    return out


def analyze(symbol, cfg):
    closes, highs, lows = fetch_klines(symbol, cfg["interval"], cfg["limit"])
    if len(closes) < cfg["ema_slow"]:
        return None
    r = rsi(closes, cfg["rsi_period"])
    ef = ema(closes, cfg["ema_fast"])
    es = ema(closes, cfg["ema_slow"])
    price = closes[-1]
    rsi_now = r[-1]
    ema_f = ef[-1]
    ema_s = es[-1]
    if rsi_now is None:
        return None
    # Tendance = structure EMA (PAS price > ema_slow, qui est contradictoire avec RSI survente)
    uptrend = ema_f >= ema_s
    downtrend = ema_f <= ema_s
    signal = None
    # BUY = repli dans tendance haussiere : RSI surventu, prix SOUS ema_lente, ema_rapide >= ema_lente
    if rsi_now < cfg["rsi_oversold"] and uptrend and ema_f >= ema_s:
        sl = price * (1 - cfg["sl_pct"])
        tp = price * (1 + cfg["sl_pct"] * cfg["rr"])
        signal = {"side": "BUY", "symbol": symbol, "price": price, "tp": tp, "sl": sl,
                  "rsi": round(rsi_now, 1), "trend": "HAUSSIER", "timeframe": cfg["interval"]}
    # SELL = rebond dans tendance baissiere : RSI surachete, prix AU-DESSUS ema_lente, ema_rapide <= ema_lente
    elif rsi_now > cfg["rsi_overbought"] and downtrend and ema_f <= ema_s:
        sl = price * (1 + cfg["sl_pct"])
        tp = price * (1 - cfg["sl_pct"] * cfg["rr"])
        signal = {"side": "SELL", "symbol": symbol, "price": price, "tp": tp, "sl": sl,
                  "rsi": round(rsi_now, 1), "trend": "BAISSIER", "timeframe": cfg["interval"]}
    return signal


def format_signal(s):
    emoji = "🟢" if s["side"] == "BUY" else "🔴"
    return (
        f"{emoji} SIGNAL {s['side']} | {s['symbol']}\n"
        f"⏱ TF: {s['timeframe']}  |  Tendance: {s['trend']}\n"
        f"💰 Entrée: {s['price']:.2f}\n"
        f"🎯 TP: {s['tp']:.2f}\n"
        f"🛑 SL: {s['sl']:.2f}\n"
        f"📉 RSI: {s['rsi']}\n"
        f"⚠️ Pas un conseil en investissement. DYOR."
    )


def send_telegram(msg, cfg):
    if cfg["dry_run"] or not cfg["telegram_token"] or not cfg["telegram_chat_id"]:
        print(msg)
        print("-" * 40)
        return
    url = TELEGRAM_URL.format(cfg["telegram_token"])
    post_data = urllib.parse.urlencode({"chat_id": cfg["telegram_chat_id"], "text": msg}).encode()
    req = urllib.request.Request(url, data=post_data, headers={"User-Agent": "Mozilla/5.0"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[ERREUR Telegram] {e}")


def scan_once(cfg):
    for sym in cfg["symbols"]:
        try:
            sig = analyze(sym, cfg)
            if sig:
                send_telegram(format_signal(sig), cfg)
            else:
                print(f"[scan] {sym}: aucun signal ({cfg['interval']})")
        except Exception as e:
            print(f"[ERREUR {sym}] {e}")


def main():
    print(f"=== Crypto Signal Bot (dry_run={CONFIG['dry_run']}) ===")
    print(f"Paires: {CONFIG['symbols']} | TF: {CONFIG['interval']}\n")
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        scan_once(CONFIG)
        return
    while True:
        scan_once(CONFIG)
        print(f"... attente {CONFIG['loop_seconds']}s\n")
        time.sleep(CONFIG["loop_seconds"])


if __name__ == "__main__":
    main()
