#!/usr/bin/env python3
"""
Crypto Signal Bot - PROTOTYPE
================================
Récupère les cours crypto (Binance publique), calcule des indicateurs
(RSI + EMA + filtre de tendance), détecte des signaux et les envoie sur Telegram.

Mode dry-run (sans token Telegram) : affiche les signaux dans la console.

Dépendance : requests  ->  pip install requests
Lancement  : python3 crypto_signal_bot.py

Configuration : édite la section CONFIG ci-dessous.
"""

import time
import sys
import json
import os
import urllib.request
import urllib.parse

# Charge .env local (secret: token Telegram + chat_id) - NE PAS commiter .env
def _load_env(path=".env"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()

# ============================================================
# CONFIG  (édite ici)
# ============================================================
CONFIG = {
    "symbols": ["SOLUSDT", "DOGEUSDT", "LTCUSDT"],  # paires validees par backtest (SOL 83%, DOGE 63%, LTC 48%)
    "interval": "15m",          # timeframe : 1m,5m,15m,1h,4h,1d
    "limit": 200,               # nb de bougies pour le calcul
    "rsi_period": 14,
    "ema_fast": 20,
    "ema_slow": 100,
    "rsi_oversold": 30,         # <  -> zone d'achat potentielle
    "rsi_overbought": 60,       # >  -> zone de vente potentielle
    "tp_pct": 0.03,             # Take Profit = +3%  (derive du SL x rr ci-dessous)
    "sl_pct": 0.02,             # Stop Loss   = -2%
    "rr": 3.0,                  # Risk/Reward cible : TP = SL x rr  (3.0 = 3/1)
    "loop_seconds": 60,         # attente entre 2 scans
    # Telegram (charge depuis .env : TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    "telegram_token": os.environ.get("TELEGRAM_TOKEN", ""),     # @Cryptobotemkbot
    "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),  # groupe signaux
    "dry_run": os.environ.get("DRY_RUN", "true").lower() not in ("false", "0"),  # lit .env DRY_RUN
}

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"

# ============================================================
# INDICATEURS (Python pur, sans pandas)
# ============================================================

def fetch_klines(symbol, interval, limit, retries=3):
    """Récupère les bougies (open time, open, high, low, close, volume)."""
    params = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "limit": limit})
    url = f"{BINANCE_KLINES}?{params}"
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            closes = [float(row[4]) for row in data]
            highs  = [float(row[2]) for row in data]
            lows   = [float(row[3]) for row in data]
            return closes, highs, lows
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise last_err


def ema(values, period):
    """Exponential Moving Average."""
    if len(values) < period:
        return [None] * len(values)
    k = 2 / (period + 1)
    emas = [None] * (period - 1)
    emas.append(sum(values[:period]) / period)
    for v in values[period:]:
        emas.append(values_ema := emas[-1] + k * (v - emas[-1]))
    return emas


def rsi(closes, period):
    """Relative Strength Index (Wilder)."""
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


# ============================================================
# LOGIQUE DE SIGNAL
# ============================================================

def analyze(symbol, cfg):
    """Renvoie un dict signal ou None si pas de signal."""
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

    # Filtre de tendance : EMA rapide >= EMA lente = tendance haussiere (structure)
    uptrend = ema_f >= ema_s
    downtrend = ema_f <= ema_s

    signal = None
    if rsi_now is None:
        return None
    signal = None
    if rsi_now < cfg["rsi_oversold"] and uptrend and ema_f >= ema_s:
        # Repli dans une tendance haussiere : RSI survendu, prix sous EMA lente, EMA rapide >= lente
        sl = price * (1 - cfg["sl_pct"])
        tp = price * (1 + cfg["sl_pct"] * cfg["rr"])
        signal = {
            "side": "BUY", "symbol": symbol, "price": price,
            "tp": tp, "sl": sl, "rsi": round(rsi_now, 1),
            "trend": "HAUSSIER", "timeframe": cfg["interval"],
        }
    elif rsi_now > cfg["rsi_overbought"] and downtrend and ema_f <= ema_s:
        # Rebond dans une tendance baissiere : RSI surachete, prix au-dessus EMA lente, EMA rapide <= lente
        sl = price * (1 + cfg["sl_pct"])
        tp = price * (1 - cfg["sl_pct"] * cfg["rr"])
        signal = {
            "side": "SELL", "symbol": symbol, "price": price,
            "tp": tp, "sl": sl, "rsi": round(rsi_now, 1),
            "trend": "BAISSIER", "timeframe": cfg["interval"],
        }
    return signal


# ============================================================
# FORMATAGE + ENVOI
# ============================================================

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


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

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
    # Scan unique si argument "once", sinon boucle
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        scan_once(CONFIG)
        return
    while True:
        scan_once(CONFIG)
        print(f"... attente {CONFIG['loop_seconds']}s\n")
        time.sleep(CONFIG["loop_seconds"])


if __name__ == "__main__":
    main()
