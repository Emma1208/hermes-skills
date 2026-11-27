#!/data/data/com.termux/files/usr/bin/bash
# GENERIC watchdog template for any long-running bot on Termux+proot-Debian.
# Usage: set BOT_CMD (must run INSIDE debian if the bot needs the Debian env),
# then:  nohup bash watchdog_template.sh >> watchdog.log 2>&1 &
# Requires: proot-distro (if bot runs in Debian), termux-wake-lock (optional).
set -u
BOT_CMD="cd /root/deriv_bot && python3 run_virtual_bot.py"   # <-- EDIT THIS
LOG=~/watchdog.log
OUT=~/bot.out
STALE=300
POLL=30
MAX_RESTARTS=20
restart_count=0
log(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }
while true; do
  log "WATCHDOG: starting bot (restart #$restart_count)"
  proot-distro login debian -- bash -c "$BOT_CMD" > "$OUT" 2>&1 &
  BOT_PID=$!
  last_mtime=0
  while true; do
    sleep "$POLL"
    if ! kill -0 "$BOT_PID" 2>/dev/null; then
      log "WATCHDOG: bot exited. Restarting."; restart_count=$((restart_count+1)); break
    fi
    if [ -f "$OUT" ]; then
      mtime=$(stat -c %Y "$OUT" 2>/dev/null || echo 0); now=$(date +%s)
      if [ "$mtime" -ne "$last_mtime" ]; then last_mtime=$mtime; restart_count=0
      elif [ $((now - mtime)) -gt "$STALE" ]; then
        log "WATCHDOG: bot silent ${STALE}s. Killing $BOT_PID."; kill -9 "$BOT_PID" 2>/dev/null
        restart_count=$((restart_count+1)); break
      fi
    fi
  done
  [ "$restart_count" -ge "$MAX_RESTARTS" ] && { log "WATCHDOG: too many restarts. Stop."; exit 1; }
done
