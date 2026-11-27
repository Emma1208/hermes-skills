# Termux 24/7 watchdog + launcher for the trading bot

Proven pattern (built & tested 2026-07-12) to keep the virtual/live bot alive on
Emmanuel's phone: Debian runs INSIDE Termux via proot-distro; the watchdog lives in
Termux and drives the bot inside Debian.

## Proven scripts (as delivered in deriv_bot.tar.gz)

### watchdog.sh  — keep-alive, runs the bot inside Debian
```bash
#!/data/data/com.termux/files/usr/bin/bash
# Restarts bot if it crashes OR goes silent (no heartbeat for STALE sec).
set -u
BOT_CMD="cd /root/deriv_bot && python3 run_virtual_bot.py"
LOG=~/deriv_bot/watchdog.log
STALE=300          # bot considered dead if no new heartbeat for 5 min
POLL=30            # check interval
MAX_RESTARTS=20    # stop after 20 restarts in a row (avoid crash loop)
restart_count=0
log(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }
while true; do
  log "WATCHDOG: starting bot (restart #$restart_count)"
  proot-distro login debian -- bash -c "$BOT_CMD" > ~/deriv_bot/bot.out 2>&1 &
  BOT_PID=$!
  last_mtime=0
  while true; do
    sleep "$POLL"
    if ! kill -0 "$BOT_PID" 2>/dev/null; then
      log "WATCHDOG: bot process exited. Restarting."
      restart_count=$((restart_count+1)); break
    fi
    if [ -f ~/deriv_bot/bot.out ]; then
      mtime=$(stat -c %Y ~/deriv_bot/bot.out 2>/dev/null || echo 0)
      now=$(date +%s)
      if [ "$mtime" -ne "$last_mtime" ]; then
        last_mtime=$mtime; restart_count=0
      elif [ $((now - mtime)) -gt "$STALE" ]; then
        log "WATCHDOG: bot silent ${STALE}s. Killing $BOT_PID."
        kill -9 "$BOT_PID" 2>/dev/null
        restart_count=$((restart_count+1)); break
      fi
    fi
  done
  if [ "$restart_count" -ge "$MAX_RESTARTS" ]; then
    log "WATCHDOG: too many restarts. Stopping."; exit 1
  fi
done
```

### start-bot-24-7.sh  — Termux entry point
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/deriv_bot
termux-wake-lock 2>/dev/null || true
nohup bash watchdog.sh >> watchdog.log 2>&1 &
echo "Bot 24/7 launched. Watchdog PID $!"
echo "  tail logs :  tail -f ~/deriv_bot/watchdog.log"
echo "  bot output:  tail -f ~/deriv_bot/bot.out"
echo "  stop all   :  pkill -f watchdog.sh ; pkill -f run_virtual_bot.py"
```

### stop-bot-24-7.sh
```bash
#!/data/data/com.termux/files/usr/bin/bash
pkill -f watchdog.sh 2>/dev/null
pkill -f run_virtual_bot.py 2>/dev/null
pkill -f "proot-distro login debian -- bash -c" 2>/dev/null
termux-wake-unlock 2>/dev/null || true
echo "Bot 24/7 stopped, wake-lock released."
```

## VirtualBot heartbeat requirement
VirtualBot.run() MUST print a status line EVERY loop, including when FLAT:
```
[HH:MM:SS] price=4101.1 eq=1000 pos=FLAT trades=0 wins=0 DD=0.0%
```
This is what makes the silent-death detector work. If the bot only prints on a
trade, a hung-but-alive process looks healthy and never restarts.

## How we proved the watchdog
Ran it against a mock bot that printed 3 heartbeats then `exit 1`. Log showed:
`starting (restart 0)` -> `exited, restart` -> `starting (restart 1)` -> re-launch.
This confirmed restart-on-crash before trusting it on the real bot.

## Shebang note
Termux shebang is `#!/data/data/com.termux/files/usr/bin/bash`. Use `bash script.sh`,
never assume `/bin/bash`.
