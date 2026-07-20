#!/bin/bash
# Watchdog for a Termux-hosted Python bot.
# Relaunches the bot on crash + keeps the phone awake.
# Usage:  termux-wake-lock && nohup bash watchdog.sh > bot.log 2>&1 &

# Keep the phone awake (Termux native command)
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock

cd "$(dirname "$0")"

LOG="bot-watchdog.log"
echo "$(date) - Watchdog demarre (PID $$)" | tee -a "$LOG"

while true; do
    echo "$(date) - Demarrage du bot..." | tee -a "$LOG"
    python3 run_bot.py >> "$LOG" 2>&1
    CODE=$?
    echo "$(date) - Bot arrete (code $CODE). Redemarrage dans 5s..." | tee -a "$LOG"
    sleep 5
done
