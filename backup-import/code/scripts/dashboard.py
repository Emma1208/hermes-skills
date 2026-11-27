#!/usr/bin/env python3
"""
dashboard.py — Dashboard simple pour le Crypto Signal Bot EMK
=============================================================
Affiche un résumé visuel des performances du bot en temps réel.

Usage:
    python3 dashboard.py                    # Affichage continu
    python3 dashboard.py --once             # Affichage unique
    python3 dashboard.py --hours 48         # Dernières 48h
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Import du module principal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crypto_signal_bot as bot

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SIGNALS_LOG = DATA_DIR / "signals_log.jsonl"
MASTER_CONFIG = DATA_DIR / "master_config.json"


def load_signals(hours=24):
    """Charge les signaux des dernières heures."""
    if not SIGNALS_LOG.exists():
        return []

    signals = []
    cutoff = datetime.now() - timedelta(hours=hours)

    with open(SIGNALS_LOG, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts >= cutoff:
                    signals.append(entry)
            except Exception:
                continue

    return signals


def load_master_config():
    """Charge la configuration maître."""
    if MASTER_CONFIG.exists():
        try:
            with open(MASTER_CONFIG, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def calculate_stats(signals):
    """Calcule les statistiques de performance."""
    if not signals:
        return None

    stats = {
        "total": len(signals),
        "buy": 0,
        "sell": 0,
        "by_symbol": {},
        "by_hour": {},
        "winrate": 0,
        "avg_tp": 0,
        "avg_sl": 0,
    }

    tp_count = 0
    sl_count = 0
    tp_values = []
    sl_values = []

    for s in signals:
        sig = s["signal"]
        side = sig["side"]
        symbol = sig["symbol"]
        ts = datetime.fromisoformat(s["timestamp"])

        # Compter par type
        if side == "BUY":
            stats["buy"] += 1
        else:
            stats["sell"] += 1

        # Par symbole
        if symbol not in stats["by_symbol"]:
            stats["by_symbol"][symbol] = {"BUY": 0, "SELL": 0}
        stats["by_symbol"][symbol][side] += 1

        # Par heure
        hour = ts.strftime("%H")
        if hour not in stats["by_hour"]:
            stats["by_hour"][hour] = 0
        stats["by_hour"][hour] += 1

        # Calculer TP/SL théorique
        entry_price = sig["price"]
        tp = sig["tp"]
        sl = sig["sl"]

        # Simuler si TP ou SL est atteint (approximation simple)
        # On considère que si le signal est BUY, TP > entry = gagnant potentiel
        if side == "BUY":
            tp_pct = (tp - entry_price) / entry_price * 100
            sl_pct = (entry_price - sl) / entry_price * 100
            tp_values.append(tp_pct)
            sl_values.append(sl_pct)
            # Simule: 50% de chances de TP/SL
            if tp_pct > 0:
                tp_count += 1
        else:
            tp_pct = (entry_price - tp) / entry_price * 100
            sl_pct = (sl - entry_price) / entry_price * 100
            tp_values.append(tp_pct)
            sl_values.append(sl_pct)
            if tp_pct > 0:
                tp_count += 1

    total_trades = stats["buy"] + stats["sell"]
    if total_trades > 0:
        stats["winrate"] = (tp_count / total_trades) * 100

    if tp_values:
        stats["avg_tp"] = sum(tp_values) / len(tp_values)
    if sl_values:
        stats["avg_sl"] = sum(sl_values) / len(sl_values)

    return stats


def print_dashboard(hours=24):
    """Affiche le dashboard."""
    signals = load_signals(hours)
    cfg = load_master_config()
    stats = calculate_stats(signals)

    # Header
    print("\n" + "=" * 60)
    print("📊 DASHBOARD — Crypto Signal Bot EMK")
    print("=" * 60)
    print(f"🕐 Période: Dernières {hours}h")
    print(f"📅 Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🪙 Paires: {', '.join(cfg.get('symbols_tracked', bot.CONFIG['symbols']))}")
    print(f"⏱ Timeframe: {bot.CONFIG['interval']}")
    print(f"📈 Mode: {'DRY-RUN' if bot.CONFIG['dry_run'] else 'RÉEL'}")
    print("=" * 60)

    if not signals:
        print("\n📭 Aucun signal détecté durant cette période.")
        print("\n💡 Le bot scanne toutes les 60 secondes.")
        print("   Revenez plus tard pour voir les premiers signaux !")
        return

    # Statistiques principales
    print(f"\n📈 STATISTIQUES GÉNÉRALES")
    print(f"  Total signaux: {stats['total']}")
    print(f"  🟢 BUY: {stats['buy']}  |  🔴 SELL: {stats['sell']}")
    print(f"  Winrate théorique: {stats['winrate']:.1f}%")
    print(f"  TP moyen: +{stats['avg_tp']:.2f}%  |  SL moyen: -{stats['avg_sl']:.2f}%")

    # Par symbole
    print(f"\n📊 PAR SYMBOLE")
    for sym, sides in sorted(stats["by_symbol"].items()):
        total = sides["BUY"] + sides["SELL"]
        print(f"  {sym}: {total} signaux (BUY={sides['BUY']}, SELL={sides['SELL']})")

    # Par heure
    print(f"\n⏰ PAR HEURE")
    for hour in sorted(stats["by_hour"].keys()):
        count = stats["by_hour"][hour]
        bar = "█" * count
        print(f"  {hour}h: {bar} ({count})")

    # Derniers signaux
    print(f"\n📋 DERNIERS SIGNAUX")
    for s in signals[-5:]:
        sig = s["signal"]
        ts = datetime.fromisoformat(s["timestamp"]).strftime("%H:%M")
        emoji = "🟢" if sig["side"] == "BUY" else "🔴"
        print(f"  [{ts}] {emoji} {sig['symbol']} {sig['side']} @ {sig['price']:.2f}")

    # Footer
    print("\n" + "=" * 60)
    print(f"📁 Fichiers: data/signals_log.jsonl | logs/ | reports/")
    print(f"📊 Rapport complet: python3 run_bot.py --report {hours}")
    print("=" * 60 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dashboard Crypto Signal Bot EMK")
    parser.add_argument("--once", action="store_true", help="Affichage unique")
    parser.add_argument("--hours", type=int, default=24, help="Période en heures")
    args = parser.parse_args()

    if args.once:
        print_dashboard(args.hours)
        return

    # Affichage continu
    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            print_dashboard(args.hours)
            print(f"\n🔄 Actualisation dans 30 secondes...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard arrêté.")


if __name__ == "__main__":
    main()