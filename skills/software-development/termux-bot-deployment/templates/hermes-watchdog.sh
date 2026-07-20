#!/bin/bash
# ===========================================================================
# Watchdog pour le GATEWAY HERMES AGENT sur Termux (phone-as-server)
# ---------------------------------------------------------------------------
# Surveille le process "hermes gateway" et le relance s'il meurt (crash, OOM,
# fermeture de Termux en arriere-plan, etc.). Garde le telephone eveille via
# termux-wake-lock pour eviter la mise en veille du CPU qui tuerait le gateway.
#
# Lancement (arriere-plan, detache de la session du gateway) :
#   setsid nohup bash hermes-watchdog.sh >/dev/null 2>&1 &
#   (depuis un shell externe ; voir templates/termux-boot-hermes.sh pour
#    l'auto-demarrage au reboot via Termux:Boot)
#
# Arret du watchdog : pkill -f hermes-guard/watchdog.sh
# ===========================================================================

LOG_DIR="$(dirname "$0")"
LOG="$LOG_DIR/hermes-watchdog.log"
HERMES_BIN="/usr/local/lib/hermes-agent/venv/bin/hermes"
POLL=15   # secondes entre chaque verification

# --- garde le telephone eveille (Termux natif) -----------------------------
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock

echo "$(date '+%F %T') - Watchdog Hermes demarre (PID $$)" >> "$LOG"

notify() {
    local msg="$1"
    echo "$(date '+%F %T') - $msg" >> "$LOG"
    # Notif Android discrete si Termux:API est installe (sinon ignore)
    if command -v termux-notification >/dev/null 2>&1; then
        termux-notification --title "Hermes Watchdog" --content "$msg" \
            --priority low 2>/dev/null
    fi
}

is_running() {
    # Ne matche QUE le vrai gateway, pas ce script ni ses enfants hors gateway
    pgrep -f "hermes gateway" >/dev/null 2>&1
}

# Boucle de surveillance
while true; do
    if ! is_running; then
        notify "Gateway Hermes absent -> redemarrage"
        # --replace nettoie toute instance fantome/residuelle (evite le
        # "second dispatcher escapes the service" au redemarrage)
        nohup "$HERMES_BIN" gateway run --replace >> "$LOG" 2>&1 &
        sleep 5   # laisse le gateway s'initialiser avant le prochain check
    fi
    sleep "$POLL"
done
