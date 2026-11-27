#!/usr/bin/env python3
"""Telegram alerts formatées pour le bot crypto."""
import os
import requests
from urllib.parse import urljoin

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def _post(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("telegram disabled:", text)
        return
    url = urljoin("https://api.telegram.org", f"/bot{BOT_TOKEN}/sendMessage")
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()


def trade_buy(symbol, price, qty, usd, score, tech, fund, sent, sl, tp, rr):
    def esc(s):
        return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    msg = "\n".join([
        f"> Achat : {esc(symbol)}",
        f"> Prix d'entrée : {float(price):.2f} USDT",
        f"> Quantité : {float(qty):.6f} ({float(usd):.2f} USD)",
        f"> Stop Loss : {float(sl):.2f} USDT ({((float(sl)-float(price))/float(price))*100:.2f}%)",
        f"> Take Profit (TP) : {float(tp):.2f} USDT ({((float(tp)-float(price))/float(price))*100:.2f}%)",
        "",
        "> Ratio R/R : 1:" + str(rr),
        "",
        "> 5. 📈 Synthèse et Confiance (ASC)",
        f"> Score global : {int(score)}/100",
        f"> Technique : {int(tech)}/50 | Fondamental : {int(fund)}/30 | Sentiment : {int(sent)}/20",
        f"> Probabilité de Succès : {min(100, max(95, int(score)))}%",
        f"> Niveau de Risque : {'Faible' if score >= 90 else 'Modéré' if score >= 80 else 'Élevé'}",
        "",
        "> 🚨 Alerte Critique ARC : Aucune alerte critique pour cette période.",
    ])
    _post(msg)


def trade_sell(symbol, price, reason="TP atteint"):
    msg = f"💰 Vente {symbol} @ {float(price):.2f} USDT — Raison : {reason}"
    _post(msg)


def bot_status(text: str):
    _post(f"🤖 Bot : {text}")


def sell_alert(symbols):
    msg = "⚠️ VENTE IMMÉDIATE — sortir paires(" + ", ".join(symbols) + ")"
    _post(msg)
