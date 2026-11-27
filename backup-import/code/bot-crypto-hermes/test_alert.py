#!/usr/bin/env python3
"""Test envoi d'alerte Telegram formatée (pas de trading live)."""
from telegram_alerts import trade_buy, bot_status

if __name__ == "__main__":
    bot_status("lancement test alert format")
    trade_buy(
        symbol="ETHUSDT",
        price=3200.00,
        qty=0.000937,
        usd=3.00,
        score=82,
        tech=45,
        fund=25,
        sent=12,
        sl=3050.00,
        tp=3575.00,
        rr=2.5,
    )
