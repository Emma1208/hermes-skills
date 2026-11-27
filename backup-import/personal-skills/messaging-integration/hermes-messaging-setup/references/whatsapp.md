# WhatsApp on Hermes — verified detail

Source: official Hermes docs (github.com/NousResearch/hermes-agent, main @ 2026-06-10),
plus local source inspection (`plugins/platforms/whatsapp/adapter.py`,
`gateway/platforms/whatsapp_common.py`).

## Pairing methods
- **Account linking = QR code ONLY.** `hermes whatsapp` runs the Baileys bridge
  wizard, prints a QR in the terminal, waits for scan. No 8-digit-code path
  exists in any version.
- The bridge script lives at `scripts/whatsapp-bridge/bridge.js` (may need
  `npm install` first — Baileys dep not bundled).
- **"Pairing code" in Hermes ≠ account link.** It is the DM-user authorization
  flow: unknown DMs get a code to prove they're allowed to talk to the bot
  (`unauthorized_dm_behavior: pair`). Do NOT promise this as a phone-link method.

## Two modes (`WHATSAPP_MODE`)
- `bot` — dedicated number people message directly. Recommended, lower ban risk.
- `self-chat` — user messages themselves to talk to the agent. Quick, single user.

## WhatsApp Business Cloud API (WABA) — `hermes whatsapp-cloud`
- Official Meta path: NO ban risk, but needs a Meta Business account + public
  webhook URL (tunnel/ngrok or a live server).
- Creates a SEPARATE business number. It does NOT manage the user's personal
  WhatsApp account, chats, contacts, or groups.
- Meta bills after ~1000 msgs/month. Not a substitute for managing a personal acct.

## Env config (`~/.hermes/.env`)
```
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot            # or "self-chat"
WHATSAPP_ALLOWED_USERS=15551234567   # comma-separated, country code, no +
# WHATSAPP_ALLOWED_USERS=*           # allow everyone
# WHATSAPP_ALLOW_ALL_USERS=true      # same as *
```
`~/.hermes/config.yaml` extras:
```
whatsapp:
  unauthorized_dm_behavior: ignore   # stay silent to strangers
  reply_prefix: ""                   # disable "⚕ Hermes Agent" header
```

## Session persistence
- Saved under `~/.hermes/platforms/whatsapp/session` (encryption keys + creds).
- Survives restarts; re-pair only on phone reset / WhatsApp protocol update /
  manual unlink. `chmod 700` that dir.

## Single-phone user workaround
QR must appear on a screen that ISN'T the user's phone:
1. Open web.telegram.org on a friend's phone (or cyber PC), log into the user's
   Telegram via QR-from-own-phone.
2. Agent runs `hermes whatsapp`, gets QR, sends it to the user over Telegram.
3. User opens that image on the friend's screen; on own phone:
   WhatsApp → Settings → Linked Devices → Link a Device → scan.

## Ban-risk caveats (unofficial API)
- Use a dedicated number, not personal.
- Conversational use only; no bulk/spam, no unsolicited outbound.
- WhatsApp Web protocol updates can break the bridge; pull latest Hermes + re-pair.

## Commands
- `hermes whatsapp` — pair (QR)
- `hermes gateway setup` — guided
- `hermes gateway` — foreground run
- `hermes gateway install` / `start` / `status` / `list`
- `hermes gateway setup` picks WhatsApp interactively.
