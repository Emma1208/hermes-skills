#!/usr/bin/env python3
"""Crypto Signal Bot - canonical prototype (zero external deps).

Data: Binance public klines (no API key needed for market data).
Indicators: RSI (Wilder) + EMA(20) + EMA(50).
Strategy: BUY the dip in an uptrend / SELL the rebound in a downtrend.
Delivery: Telegram (set token+chat_id, dry_run=False) or console.
Run: python3 crypto_signal_bot.py once   # single scan
     python3 crypto_signal_bot.py         # infinite loop
"""
import time, sys, json, urllib.request, urllib.parse

CONFIG = {
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"],
    "interval": "15m",
    "limit": 200,
    "rsi_period": 14,
    "ema_fast": 20,
    "ema_slow": 50,
    "rsi_oversold": 35,
    "rsi_overbought": 65,
    "tp_pct": 0.03,
    "sl_pct": 0.015,
    "loop_seconds": 60,
    "telegram_token": "",
    "telegram_chat_id": "",
    "dry_run": True,
}
BINANCE_KLINES = "https://api.binance.com/api/v3/klines"
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"


def fetch_klines(symbol, interval, limit, retries=3):
    params = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "limit": limit})
    url = f"{BINANCE_KLINES}?{params}"
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            closes = [float(r[4]) for r in data]
            highs = [float(r[2]) for r in data]
            lows = [float(r[3]) for r in data]
            return closes, highs, lows
        except Exception as e:
            last = e
            time.sleep(2)
    raise last


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


def signal_conditions(price, rsi_now, ema_f, ema_s):
    """CANONICAL signal logic. BUY dip in uptrend / SELL rebound in downtrend.
    Returns 'BUY', 'SELL', or None. Keep IDENTICAL in live bot AND backtest."""
    if rsi_now is None:
        return None
    if rsi_now < CONFIG["rsi_oversold"] and price < ema_s and ema_f >= ema_s:
        return "BUY"
    if rsi_now > CONFIG["rsi_overbought"] and price > ema_s and ema_f <= ema_s:
        return "SELL"
    return None


def analyze(symbol, cfg):
    closes, _h, _l = fetch_klines(symbol, cfg["interval"], cfg["limit"])
    if len(closes) < cfg["ema_slow"]:
        return None
    r = rsi(closes, cfg["rsi_period"])
    ef = ema(closes, cfg["ema_fast"])
    es = ema(closes, cfg["ema_slow"])
    price = closes[-1]
    rsi_now = r[-1]
    ema_f = ef[-1]
    ema_s = es[-1]
    side = signal_conditions(price, rsi_now, ema_f, ema_s)
    if not side:
        return None
    if side == "BUY":
        tp = price * (1 + cfg["tp_pct"])
        sl = price * (1 - cfg["sl_pct"])
        trend = "HAUSSIER"
    else:
        tp = price * (1 - cfg["tp_pct"])
        sl = price * (1 + cfg["sl_pct"])
        trend = "BAISSIER"
    return {"side": side, "symbol": symbol, "price": price, "tp": tp, "sl": sl,
            "rsi": round(rsi_now, 1), "trend": trend, "timeframe": cfg["interval"]}


def format_signal(s):
    emoji = "🟢" if s["side"] == "BUY" else "🔴"
    return (f"{emoji} SIGNAL {s['side']} | {s['symbol']}\n"
            f"⏱ TF: {s['timeframe']}  |  Tendance: {s['trend']}\n"
            f"💰 Entrée: {s['price']:.2f}\n"
            f"🎯 TP: {s['tp']:.2f}\n"
            f"🛑 SL: {s['sl']:.2f}\n"
            f"📉 RSI: {s['rsi']}\n"
            f"⚠️ Pas un conseil en investissement. DYOR.")


def send_telegram(msg, cfg):
    if cfg["dry_run"] or not cfg["telegram_token"] or not cfg["telegram_chat_id"]:
        print(msg)
        print("-" * 40)
        return
    url = TELEGRAM_URL.format(cfg["telegram_token"])
    post = urllib.parse.urlencode({"chat_id": cfg["telegram_chat_id"], "text": msg}).encode()
    req = urllib.request.Request(url, data=post, headers={"User-Agent": "Mozilla/5.0"})
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
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        scan_once(CONFIG)
        return
    while True:
        scan_once(CONFIG)
        print(f"... attente {CONFIG['loop_seconds']}s\n")
        time.sleep(CONFIG["loop_seconds"])


if __name__ == "__main__":
    main()
