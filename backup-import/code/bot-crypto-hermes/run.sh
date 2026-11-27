#!/data/data/com.termux/files/usr/bin/bash
set -e
cd ~/bot-crypto-hermes
[ -f .env ] && set -a && source .env && set +a
exec python3 main.py
