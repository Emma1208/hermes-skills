---
name: hermes-messaging-setup
description: Connect a messaging platform (WhatsApp, etc.) to Hermes Agent — pairing methods, mode selection, env config, ban-risk caveats. Embeds the HARD rule that Hermes settings must never be changed without the user's explicit permission.
---

# Hermes Messaging Platform Setup

Covers linking a messaging platform to Hermes Agent's gateway. WhatsApp is the
most common request; the full knowledge bank lives in `references/whatsapp.md`.

## HARD RULE — permission guardrail (do not skip)
The user has explicitly forbidden changing Hermes settings without consent:
> « Attention touche pas au paramétrage de Hermes sans ma permission »

Before running ANY command that modifies Hermes config or state —
`hermes whatsapp`, `hermes gateway setup`, editing `.env`/`config.yaml`,
`hermes gateway install`, etc.:
1. Say what the command will do and whether it is read-only or write.
2. Offer the options and get explicit approval ("oui" / yes).
3. Only then execute.
Read-only inspection is fine without asking: `--help`, grepping source files,
`hermes status`, `hermes gateway status`, `hermes gateway list`.

## General flow
- `hermes gateway setup` → guided platform selection.
- `hermes whatsapp` → WhatsApp pairing wizard (QR code only).
- Config lives in `~/.hermes/.env` and `~/.hermes/config.yaml`.
- Start gateway: `hermes gateway` (foreground) or `hermes gateway install`.

## Verified facts (official Hermes docs, main @ 2026-06-10)
- WhatsApp pairing is **QR-code only** via the Baileys bridge. There is **no
  8-digit account-link code** in ANY Hermes version.
- Hermes' "pairing code" = **DM user authorization** (who may talk to the bot),
  NOT account linking. Do not conflate the two.
- WhatsApp Business Cloud API (WABA) = a SEPARATE business number; it does NOT
  manage the user's personal account/chats.
- Single-phone user: QR must be shown on a temporary screen (friend's phone via
  web.telegram.org, or a cyber PC), then scanned with the user's own phone
  (WhatsApp → Linked Devices → Link a Device).
- Ban risk (unofficial API): recommend a dedicated number, conversational use.

See `references/whatsapp.md` for env vars, modes, session paths, and the
pairwise comparison the user worked through.

## Pitfalls
- Never promise an "8-digit code" path for linking — it does not exist.
- Never claim WABA manages their personal account — it doesn't.
- Never edit `.env`/`config.yaml` or run setup commands without explicit approval.
- Don't silently assume the user has a second screen; ask about their setup.
