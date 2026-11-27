---
name: hermes-termux-recovery
description: Recover/restore a Hermes Termux install from the GitHub backup repo when migrating to a new phone, AND the clean fresh-install flow (proot-distro Debian workaround for Termux's Python 3.14).
triggers:
  - change de telephone / nouveau telephone / recover hermes / restore memory
  - references to repo Emma1208/hermes-termux-backup or restore.sh
  - any device-migration or full-memory-restore request from Emmanuel
  - missing custom skills after a restore (freelance-script-bot, hermes-gateway-telegram)
  - installer hermes termux / fresh install / nouvelle install termux
  - Python 3.14 incompatibility / proot-distro debian workaround
---

# Hermes Termux Recovery

Emmanuel runs Hermes on a personal Android phone via **Termux**. A cron job (id `8dc9a4896d21`, every 2h) pushes the full config/memory/sessions to the **private** GitHub repo `Emma1208/hermes-termux-backup`. To bring Hermes back on a new device, clone that repo and run `restore.sh`.

## Full recovery flow (new phone)
1. Install **Termux from F-Droid** (NOT Play Store — Play version is outdated and breaks).
2. In Termux: `pkg update && pkg install git python python-pip -y`
3. Clone with token (repo is private):
   `git clone https://<GITHUB_TOKEN>@github.com/Emma1208/hermes-termux-backup.git`
   then `cd hermes-termux-backup`
4. `bash restore.sh`

`restore.sh` does 6 steps: verify env → pip install -r requirements.txt → mkdir ~/.hermes tree → copy config (sanitized), USER.md, MEMORY.md, sessions, state, skills → create ~/.hermes/.env from template → git config.

## What gets restored vs what you MUST supply
- **Restored automatically**: `~/.hermes/memories/USER.md`, `MEMORY.md`, sessions, state (gateway_state.json, processes.json, discord_threads.json), sanitized config.yaml, channel_directory.json, **source skills + personal/custom skills**.
- **NOT restored (you must fill in)**: `~/.hermes/.env` is created from `.env.example` with EMPTY values. Hermes will NOT work until you add real keys: `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `TELEGRAM_BOT_TOKEN`, `COMPOSIO_API_KEY`, `BINANCE_API_KEY`, `GITHUB_TOKEN`. Also `config.yaml` has `REDACTED` placeholders to replace.

## PERSONAL SKILLS WERE LOST — the original bug (learned the hard way)
The original `restore.sh` + `auto_sync.sh` only handled `hermes-agent-source/skills` (the bundled Hermes library) and **NEVER backed up or restored `~/.hermes/skills/` (Emmanuel's custom skills)**. Result: on recovery, custom skills (`freelance-script-bot`, `hermes-gateway-telegram`) were simply gone — the backup repo had them nowhere.

**Fix applied 2026-07-09 (commit d8cbfc8 on Emma1208/hermes-termux-backup):**
- `auto_sync.sh`: added step "8b" that copies `~/.hermes/skills/*` (excluding `__pycache__`, `.pyc`, `.usage.json`) into `personal-skills/` in the repo.
- `restore.sh`: after copying source skills, copies `personal-skills/*` back into `~/.hermes/skills/` (custom skills layered ON TOP of source skills, not overwritten).
- Custom skills now live under `personal-skills/` in the repo so future auto-syncs + restores preserve them.

**Always re-verify after any restore that `personal-skills/` exists in the repo and that `restore.sh` restores it.** If a future restore reports "Skills (source)" but NOT "Personal skills (custom)", the bug regressed — re-apply the patch above (add step 8b to auto_sync.sh, add the personal-skills copy block to restore.sh).

## CRON JOBS WERE ALSO LOST — same class of bug (learned 2026-07-09)
The stock scripts do not back up `~/.hermes/cron/` either, and the cron *config* (scheduled jobs) lives only on the source device — it is NOT in the repo. So a restored device loses its crons. The auto-backup cron (`8dc9a4896d21`, every 2h, `no-agent`, `deliver local`, script `auto_sync.sh`) must be **recreated on the new device** with `cronjob create`.

**Fix applied 2026-07-09 (commit a8d1c84):** `auto_sync.sh` now also mirrors `~/.hermes/cron/` (skipping `*.lock`) into `cron/` in the repo, and a working `auto_sync.sh` adapted to the target device's paths lives in `~/.hermes/scripts/`. Condensed recipe + verified shape: `references/skill-cron-persistence.md`.

**Recreate the auto-backup cron** (script path MUST be a bare filename inside `~/.hermes/scripts/`, absolute paths are rejected):
`cronjob create --name 'Auto-Backup Hermes' --schedule 'every 2h' --script auto_sync.sh --no-agent --deliver local`
Set git identity once per clone: `git config user.name "Emmanuel Kakesa Mudimba" && git config user.email "emmanuelkakesa@outlook.com"` (else commits warn/fail).

## FRESH INSTALL on Termux (clean start, no backup)
When setting Hermes up from scratch on Termux (NOT restoring from the GitHub backup):
1. Termux from **F-Droid** only. `pkg update && pkg install git python python-pip curl -y`
2. **Install into proot-distro Debian, not native Termux** (see Python 3.14 pitfall below). `pkg install proot-distro -y && proot-distro install debian`, then `proot-distro login debian` (Debian 13/Trixie → Python 3.13.5, compatible). Run the Hermes `install.sh` **inside Debian**.
3. Inside Debian: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`, then `hermes setup` (or `hermes setup --portal` for one-OAuth model+tools).
4. `hermes gateway start` (inside Debian) to bring the Telegram bot up.
5. Convenience launchers created in **NATIVE Termux** (because Hermes lives in the proot):
   - `~/start-hermes.sh` → `#!/data/data/com.termux/files/usr/bin/bash` + `proot-distro login debian -- hermes gateway start`
   - `~/hermes-cli.sh` → same shebang + `proot-distro login debian -- hermes`
   - `chmod +x` both. To relaunch after reboot you MUST `proot-distro login debian` first — Hermes is not on the native Termux PATH.
6. If a prior broken install left a venv in Python 3.14, clean it INSIDE Debian: `rm -rf ~/.hermes/hermes-agent` then re-run the installer within `proot-distro login debian`.

## Pitfalls (learned the hard way)
- **Token in clone URL leaks it into shell history / git config.** Always rotate the token after using it in a URL, and prefer `git config --global credential.helper store` + a one-time push. The repo URL is `https://github.com/Emma1208/hermes-termux-backup.git` — no token needed if creds are stored.
- `restore.sh` uses `#!/data/data/com.termux/files/usr/bin/bash` shebang — run it as `bash restore.sh`, never assume `/bin/bash`.
- **NEVER touch the Hermes venv** `~/.hermes/hermes-agent/venv`. All maintenance/cron runs OUTSIDE that venv. Boot is fixed: `start-hermes` points at `~/.hermes/hermes-agent`.
- LAN-only resources (e.g. his Termux server `10.253.42.225:22`) are unreachable from external/sandboxed environments — don't waste effort trying to reach them; work from the backup repo instead.
- After restore, start the gateway: `hermes gateway start`. Telegram bot returns as soon as gateway is up.
- **Termux now ships Python 3.14 (pkg install python = 3.14.6), which BREAKS the Hermes install.** The installer aborts with `ERROR: Package 'hermes-agent' requires a different Python: 3.14.x not in '>=3.11,<3.14'`. Hermes requires Python **3.11–3.13 (strictly <3.14)**. Reliable fix: `pkg install proot-distro -y && proot-distro install debian`, then `proot-distro login debian` (Debian 13/Trixie provides Python 3.13.5, compatible), then run the Hermes `install.sh` **inside Debian**. Do NOT compile Python 3.13 from source on Termux — use the proot Debian route. Note `hermes` then lives only inside the proot; to run it later: `proot-distro login debian` then `hermes ...`.
- If a `ghp_*` token was pasted in chat, flag it and tell Emmanuel to revoke + regenerate at github.com/settings/tokens.

## When you only need the MEMORY (not a full phone migration)
On any machine, clone the repo and read `memories/USER.md` + `memories/MEMORY.md`, then fold their contents into the active `memory` tool (compacted to fit the 2,200-char budget). See `references/memory-bank.md` for the condensed content shape used.

## Verification
- `ls ~/.hermes/memories/` shows USER.md + MEMORY.md.
- `ls ~/.hermes/skills/freelance ~/.hermes/skills/devops` shows the custom skills (freelance-script-bot, hermes-gateway-telegram, hermes-termux-recovery).
- `cat ~/.hermes/.env | grep -c KEY` > 0 and values non-empty.
- `hermes gateway start` boots without "missing config" errors.
