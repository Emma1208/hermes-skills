#!/usr/bin/env python3
"""
run_bot.py — Bot maître pour le Crypto Signal Bot EMK
====================================================
Fonctionnalités:
- Commandes Telegram: /start, /status, /signals, /report, /help
- Mode dry-run par défaut (journalise les signaux sans trading)
- Collecte et rapport des performances
- Compatible avec crypto_signal_bot.py

Usage:
    python3 run_bot.py                    # Démarrage interactif (dry-run)
    python3 run_bot.py --once             # Scan unique
    python3 run_bot.py --report           # Génère un rapport

Configuration (.env):
    TELEGRAM_TOKEN=...
    TELEGRAM_CHAT_ID=...
    DRY_RUN=true
"""

import os
import sys
import json
import time
import signal
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Import du module principal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crypto_signal_bot as bot

# ── Configuration ──
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Créer les dossiers nécessaires
for d in [DATA_DIR, LOG_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

# Fichier de log des signaux
SIGNALS_LOG = DATA_DIR / "signals_log.jsonl"
# Fichier de configuration du bot maître
MASTER_CONFIG = DATA_DIR / "master_config.json"


def load_master_config():
    """Charge ou crée la configuration maître."""
    default = {
        "dry_run": True,
        "active": True,
        "start_time": None,
        "total_signals": 0,
        "total_scans": 0,
        "symbols_tracked": bot.CONFIG["symbols"],
        "last_signal_time": None,
        "telegram_enabled": False,
        "admin_ids": [],
        # Anti-spam: délai minimum (minutes) entre 2 signaux de la même paire
        "cooldown_minutes": 15,
        # Dernier timestamp de signal par paire
        "last_signal_by_symbol": {},
    }
    if MASTER_CONFIG.exists():
        try:
            with open(MASTER_CONFIG, "r") as f:
                cfg = json.load(f)
            # Fusion avec les valeurs par défaut
            for k, v in default.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception:
            return default
    return default


def save_master_config(cfg):
    """Sauvegarde la configuration maître."""
    with open(MASTER_CONFIG, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def log_signal(signal):
    """Enregistre un signal dans le fichier de log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "signal": signal,
    }
    with open(SIGNALS_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_signals_history(hours=24):
    """Récupère l'historique des signaux des dernières heures."""
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


def format_report(hours=24):
    """Génère un rapport texte des signaux."""
    signals = get_signals_history(hours)
    cfg = load_master_config()

    report = []
    report.append(f"📊 RAPPORT DES SIGNAUX — Dernières {hours}h")
    report.append(f"🕐 Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"🤖 Bot actif depuis: {cfg.get('start_time', 'N/A')}")
    report.append(f"📈 Total signaux: {len(signals)}")
    report.append(f"🔍 Total scans: {cfg.get('total_scans', 0)}")
    report.append("")

    if not signals:
        report.append("📭 Aucun signal détecté durant cette période.")
        return "\n".join(report)

    # Compter par symbole et type
    by_symbol = {}
    by_side = {"BUY": 0, "SELL": 0}
    for s in signals:
        sig = s["signal"]
        sym = sig["symbol"]
        side = sig["side"]
        by_symbol.setdefault(sym, {"BUY": 0, "SELL": 0})
        by_symbol[sym][side] += 1
        by_side[side] += 1

    report.append("📈 Répartition par type:")
    report.append(f"  🟢 BUY: {by_side['BUY']}")
    report.append(f"  🔴 SELL: {by_side['SELL']}")
    report.append("")

    report.append("📊 Par symbole:")
    for sym, sides in sorted(by_symbol.items()):
        report.append(f"  {sym}: BUY={sides['BUY']}, SELL={sides['SELL']}")
    report.append("")

    # Derniers signaux
    report.append("📋 Derniers signaux:")
    for s in signals[-10:]:
        sig = s["signal"]
        ts = datetime.fromisoformat(s["timestamp"]).strftime("%H:%M")
        emoji = "🟢" if sig["side"] == "BUY" else "🔴"
        report.append(f"  [{ts}] {emoji} {sig['symbol']} {sig['side']} @ {sig['price']:.2f}")

    return "\n".join(report)


def save_report(hours=24):
    """Sauvegarde un rapport dans le dossier reports/."""
    report = format_report(hours)
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = REPORTS_DIR / filename
    with open(filepath, "w") as f:
        f.write(report)
    return filepath


def scan_with_logging(cfg):
    """Effectue un scan et journalise les signaux."""
    master_cfg = load_master_config()
    master_cfg["total_scans"] += 1
    master_cfg["start_time"] = master_cfg.get("start_time") or datetime.now().isoformat()

    for sym in cfg["symbols"]:
        try:
            sig = bot.analyze(sym, cfg)
            if sig:
                # ── Anti-spam: vérifier le cooldown par paire ──
                now = datetime.now()
                last_ts = master_cfg.get("last_signal_by_symbol", {}).get(sym)
                cooldown = master_cfg.get("cooldown_minutes", 15)
                if last_ts:
                    last_time = datetime.fromisoformat(last_ts)
                    elapsed = (now - last_time).total_seconds() / 60
                    if elapsed < cooldown:
                        # Trop tôt pour renvoyer un signal sur cette paire
                        print(f"[scan] {sym}: signal ignoré (cooldown {cooldown}min, "
                              f"reste {cooldown - elapsed:.1f}min)")
                        continue

                # Journaliser le signal
                log_signal(sig)
                master_cfg["total_signals"] += 1
                master_cfg["last_signal_time"] = now.isoformat()
                master_cfg.setdefault("last_signal_by_symbol", {})[sym] = now.isoformat()

                # Afficher ou envoyer
                msg = bot.format_signal(sig)
                if cfg["dry_run"]:
                    print(f"\n{msg}\n{'='*50}")
                else:
                    bot.send_telegram(msg, cfg)

                # Log détaillé
                log_file = LOG_DIR / f"signals_{datetime.now().strftime('%Y%m%d')}.log"
                with open(log_file, "a") as f:
                    f.write(f"[{datetime.now().isoformat()}] {msg}\n")

            else:
                print(f"[scan] {sym}: aucun signal ({cfg['interval']})")
        except Exception as e:
            print(f"[ERREUR {sym}] {e}")
            log_file = LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now().isoformat()}] {sym}: {e}\n")

    save_master_config(master_cfg)


def cmd_start():
    """Affiche le message de démarrage."""
    cfg = load_master_config()
    print("=" * 60)
    print("🚀 Crypto Signal Bot EMK — Bot Maître")
    print("=" * 60)
    print(f"📊 Mode dry-run: {cfg.get('dry_run', True)}")
    print(f"🪙 Paires suivies: {', '.join(cfg['symbols_tracked'])}")
    print(f"⏱ Timeframe: {bot.CONFIG['interval']}")
    print(f"📈 Signaux détectés: {cfg.get('total_signals', 0)}")
    print(f"🔍 Scans effectués: {cfg.get('total_scans', 0)}")
    print(f"🕐 Démarré le: {cfg.get('start_time', 'N/A')}")
    print("=" * 60)
    print("\nCommandes disponibles:")
    print("  --once    : Scan unique")
    print("  --report  : Générer un rapport")
    print("  --help    : Afficher l'aide")
    print("\nDémarrage du monitoring en continu...\n")


def cmd_help():
    """Affiche l'aide."""
    print("""
╔══════════════════════════════════════════════════════╗
║  Crypto Signal Bot EMK — Aide                        ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Commandes:                                          ║
║    python3 run_bot.py                    Démarrage   ║
║    python3 run_bot.py --once             Scan unique ║
║    python3 run_bot.py --report [hours]   Rapport     ║
║    python3 run_bot.py --help             Cette aide  ║
║                                                      ║
║  Commandes Telegram (si activé):                     ║
║    /start    Menu principal                          ║
║    /status   État du bot                             ║
║    /signals  Derniers signaux                        ║
║    /report   Rapport de performance                  ║
║    /help     Aide                                    ║
║                                                      ║
║  Fichiers générés:                                   ║
║    data/signals_log.jsonl   Historique des signaux   ║
║    data/master_config.json  Configuration maître     ║
║    logs/                    Logs quotidiens          ║
║    reports/                 Rapports générés         ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(description="Crypto Signal Bot EMK — Bot Maître")
    parser.add_argument("--once", action="store_true", help="Scan unique")
    parser.add_argument("--report", nargs="?", const=24, type=int, help="Générer un rapport (heures)")
    parser.add_argument("--info", action="store_true", help="Afficher l'aide détaillée")
    args = parser.parse_args()

    if args.info:
        cmd_help()
        return

    if args.report is not None:
        filepath = save_report(args.report)
        print(f"✅ Rapport généré: {filepath}")
        print("\n" + format_report(args.report))
        return

    # Démarrage
    cmd_start()

    if args.once:
        scan_with_logging(bot.CONFIG)
        print("\n✅ Scan terminé. Rapport disponible avec --report")
        return

    # Boucle principale
    try:
        while True:
            scan_with_logging(bot.CONFIG)
            print(f"\n... prochain scan dans {bot.CONFIG['loop_seconds']}s")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] En attente...\n")
            time.sleep(bot.CONFIG["loop_seconds"])
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du bot.")
        cfg = load_master_config()
        print(f"📊 Résumé: {cfg['total_signals']} signaux, {cfg['total_scans']} scans")
        print(f"📁 Rapport: python3 run_bot.py --report")


if __name__ == "__main__":
    main()