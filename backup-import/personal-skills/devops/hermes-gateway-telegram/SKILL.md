---
name: hermes-gateway-telegram
description: Operate the Hermes Telegram gateway on Termux — exclusive bot token, polling conflict (HTTP 409) diagnosis/recovery, and safe restart procedure without touching the Hermes venv.
tags: [telegram, gateway, termux, 409, polling, conflict]
related_skills: [hermes-termux-recovery, freelance-script-bot]
triggers:
  - telegram gateway / hermes gateway start / bot ne répond pas
  - HTTP 409 / conflict / "terminated by other getUpdates"
  - token telegram / polling
---

# Hermes Gateway — Telegram (Termux)

Hermes reaches Emmanuel on Telegram via a **dedicated, EXCLUSIVE** bot token (starts `820389...`). Nothing else may poll that token. This skill fixes the classic failure: the gateway stops answering because two processes fight over the same update stream.

## Symptom: HTTP 409 Conflict
- Error: `409 Conflict: terminated by other getUpdates request` (or bot silently dead).
- Root cause: **another instance is already polling the same token** — a leftover/stale Hermes gateway, or a stray `python` bot process.

## Recovery procedure (Order matters)
1. **Find the offender** — do NOT just kill blindly:
   `pgrep -af python` then look for any hermes-gateway / bot process using the same token.
2. **Kill duplicates only**:
   `pkill -f "hermes.*gateway"` (or the specific PID from step 1). Leave unrelated bots (e.g. Minga/2MT) alone — they use DIFFERENT tokens.
3. **Confirm single instance** then restart:
   `hermes gateway start`
4. Verify the bot replies on Telegram (send "Regarde" test or any message).

## Critical guardrails
- **Never run the gateway inside the Hermes venv** `~/.hermes/hermes-agent/venv`. All maintenance/cron/bot processes run OUTSIDE it. Boot script `start-hermes` points at `~/.hermes/hermes-agent` — don't modify it.
- The Telegram token is **exclusive to Hermes** and lives in the `820389...` range. Client bots (Minga, 2MT, freelance) MUST use a DIFFERENT @BotFather token (e.g. `895028...`). A client bot launched with the `820389` token triggers HTTP 409 and kills this gateway. Put a startup guard in every client bot refusing any token starting `820389` (recipe in `freelance-script-bot` → `references/ptb-pitfalls.md`).
- If 409 recurs after a clean restart, check `state/processes.json` and any `termux-boot` entry for a second auto-start of the gateway.

## WhatsApp note
Separate channel: bot mode + `allowed_users=*` + `unauthorized_dm_behavior=ignore`. Edit config.yaml with `sed` (don't hand-edit the venv). A 409 there follows the same duplicate-process logic.

## Verification
- No `409` in gateway logs after `hermes gateway start`.
- Exactly ONE hermes-gateway process in `pgrep -af python`.
- Telegram message gets a reply within seconds.
