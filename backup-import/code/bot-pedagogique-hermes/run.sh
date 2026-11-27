#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || { echo 'Manque .env'; exit 1; }
exec python bot_telegram.py
