# Deploying the Crypto Signal Bot 24/7 on Android (Termux)

The user runs the bot on their own phone as a free server. This works but has
sharp edges. Captured from a real setup session.

## Install Termux correctly
- Install from **F-Droid**, NOT Google Play (Play Store build is deprecated/buggy).
  https://f-droid.org/packages/com.termux/
- Optional for auto-start at boot: install **Termux:Boot** from F-Droid.

## Keep the bot alive (watchdog + wake-lock)
SSH/VPS not available? Use a watchdog loop. `termux-wake-lock` stops Android from
killing the process / sleeping the CPU.

`watchdog.sh`:
```bash
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock
cd "$(dirname "$0")"
while true; do
  echo "$(date) - start"; python3 run_bot.py >> bot-watchdog.log 2>&1
  echo "$(date) - crashed (code $?), restart in 5s"; sleep 5
done
```
Launch in background so it survives closing the app:
```bash
termux-wake-lock
nohup bash watchdog.sh >/dev/null 2>&1 &
```
Auto-start at boot (Termux:Boot): copy `watchdog.sh` to `~/.termux/boot/`
(create the dir) — Termux:Boot runs anything there at boot.

## Keep the bot alive (watchdog + wake-lock)
SSH/VPS not available? Use a watchdog loop. `termux-wake-lock` stops Android from
killing the process / sleeping the CPU.

`watchdog.sh`:
```bash
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock
cd "$(dirname "$0")"
while true; do
  echo "$(date) - start"; python3 run_bot.py >> bot-watchdog.log 2>&1
  echo "$(date) - crashed (code $?), restart in 5s"; sleep 5
done
```
Launch in background so it survives closing the app:
```bash
termux-wake-lock
nohup bash watchdog.sh >/dev/null 2>&1 &
```
Auto-start at boot (Termux:Boot): copy `watchdog.sh` to `~/.termux/boot/`
(create the dir) — Termux:Boot runs anything there at boot.

## ⚠️ Battery
`termux-wake-lock` prevents sleep → drains battery. Keep the phone on charge.
The user's session repeatedly hit 15-19% — the run stalled. Always tell them
to plug in before launching the watchdog.

## ⚠️ Long secrets: do NOT type them by hand
Telegram tokens are 46 chars and overflow the phone screen → manual `printf`
retyping produces truncated/cut tokens and wasted turns. Instead:
- Use **`nano .env`** and PASTE the full token (long-press → paste). Then
  `CTRL+X` → `Y` → Enter to save. Far more reliable than `printf` on a small screen.
- Or generate the `.env` from a script on the dev machine and copy the whole file.
- NEVER hand the user an *abbreviated* secret (e.g. `883696...1`) and tell them to
  "copy this" — they will type the abbreviation and it won't work. Give the FULL
  value, or read it from the real source file and paste it. (This mistake cost
  ~10 turns in the real session — the user explicitly flagged it.)

## ⚠️ You (the agent) CANNOT SSH into the phone
The phone exposes SSH only on a **private LAN IP** (e.g. `10.x.x.x`, port 22).
The agent's environment is a remote machine NOT on that Wi-Fi, so:
- `ping`/`tcp` to `10.x.x.x` → 100% loss / "Connection refused".
- Therefore the agent must guide the user to type commands THEMSELVES in Termux.
  Do not attempt to connect; explain why and continue the step-by-step guidance.

## Common Termux pitfalls seen
- `git clone` of a PRIVATE repo prompts for username/password. Make the repo
  PUBLIC (if it has no secrets) or use a token URL. The bot repo here was made
  public because `.env`/secrets are git-ignored.
- Typo in clone URL (`Emna1208` vs `Emma1208`) → clone fails. Double-check spelling.
- `cd crypto-signal-bot-emk && nano .env` when ALREADY inside the folder →
  "No such file or directory" on the `cd`. Just run `nano .env` directly.
- `printf '...' > .env` OVERWRITES the file each time. Write all 3 lines in ONE
  command, or use `>>` to append, or use nano.
