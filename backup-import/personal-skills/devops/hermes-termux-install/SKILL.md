---
name: hermes-termux-install
description: Install Hermes Agent on Android Termux. Handles the Termux Python 3.14 incompatibility by running Hermes inside a Debian proot-distro (Python 3.13). Fresh-install path — distinct from hermes-termux-recovery (which is restore-from-backup).
triggers:
  - install Hermes on Termux or Android
  - Hermes Termux setup
  - Python version error during Hermes install on Termux
  - new phone Termux install, not a backup restore
---

# Install Hermes Agent on Termux

## Steps
1. Termux from **F-Droid only** (Play Store version is broken/outdated).
2. `pkg update && pkg install git python python-pip curl -y`
3. Run installer: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`

## CRITICAL PITFALL — Termux Python is 3.14 (incompatible)
Termux's default Python is **3.14.x** (seen 3.14.6). Hermes requires **>=3.11,<3.14**.
The installer fails with:
```
ERROR: Package 'hermes-agent' requires a different Python: 3.14.6 not in '>=3.11,<3.14'
```
and suggests `python -m pip install -e .[termux-all] -c constraints-termux.txt` —
**that does NOT fix it** (still 3.14 in the Termux venv).

## FIX — run Hermes inside Debian (proot-distro)
Debian in proot gives Python 3.13.5, which satisfies Hermes.
```bash
pkg install proot-distro -y && proot-distro install debian
proot-distro login debian
apt update && apt install -y git curl python3 python3-pip python3-venv clang rustc cargo make pkg-config libffi-dev libssl-dev ca-certificates ripgrep ffmpeg
rm -rf ~/.hermes/hermes-agent          # clear the broken 3.14 venv from the first try
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```
Verify inside Debian: `python3 --version` → 3.13.x, then `hermes --version` works.

## After install
- Hermes lives **inside Debian**, not bare Termux. To run: `proot-distro login debian`
  then `hermes ...`.
- Shortcut scripts (created in BARE Termux shell, NOT inside Debian):
  - `~/start-hermes.sh` → `proot-distro login debian -- hermes gateway start`
  - `~/hermes-cli.sh` → `proot-distro login debian -- hermes`
- Never touch `~/.hermes/hermes-agent/venv`. Termux shebang =
  `#!/data/data/com.termux/files/usr/bin/bash` (run `bash script.sh`, never `/bin/bash`).

## Verify
`proot-distro login debian` → `hermes --version` works, `python3 --version` shows 3.11–3.13.
