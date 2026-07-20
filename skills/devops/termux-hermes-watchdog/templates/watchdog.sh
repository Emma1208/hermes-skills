#!/bin/bash
# ===========================================================================
# Watchdog Hermes Agent (gateway) — Termux / phone-as-server
# Surveille "hermes gateway" et le relance s'il meurt (crash, OOM, fermeture
# Termux en arriere-plan). Garde le telephone eveille via termux-wake-lock.
#
# Lancement (une fois, detache de la session) :
#   setsid nohup bash /root/hermes-guard/watchdog.sh >/dev/null 2>&1 &
# Auto-demarrage : via Termux:Boot (~/.termux/boot/start-hermes-watchdog.sh)
# ===========================================================================

LOG_DIR="$(dirname "$0")"
LOG="$LOG_DIR/hermes-watchdog.log"
HERMES_BIN="/usr/local/lib/hermes-agent/venv/bin/hermes"
POLL=15   # secondes entre chaque verification

# Garde le telephone eveille (Termux natif)
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock

echo "$(date '+%F %T') - Watchdog Hermes demarre (PID $$)" >> "$LOG"

notify() {
    local msg="$1"
    echo "$(date '+%F %T') - $msg" >> "$LOG"
    command -v termux-notification >/dev/null 2>&1 && \
        termux-notification --title "Hermes Watchdog" --content "$msg" \
            --priority low 2>/dev/null
}

is_running() {
    # Matche uniquement le vrai gateway (pas ce script ni ses enfants)
    pgrep -f "hermes gateway" >/dev/null 2>&1
}

while true; do
    if ! is_running; then
        notify "Gateway Hermes absent -> redemarrage"
        # --replace nettoie toute instance fantome (evite "second dispatcher escapes")
        nohup "$HERMES_BIN" gateway run --replace >> "$LOG" 2>&1 &
        sleep 5   # laisse le gateway s'initialiser
    fi
    sleep "$POLL"
done
