# WhatsApp Integration — Verified Facts (2026-07-15)

## Source investigation (no config mutation performed)
- `hermes whatsapp --help` → "Configure WhatsApp and pair via QR code". Interactive, TTY-required.
- `hermes whatsapp-cloud --help` → Meta Business Cloud API adapter (separate number, webhook needed).
- Bridge source: `plugins/platforms/whatsapp/adapter.py` references a `bridge.js` under `scripts/whatsapp-bridge` (resolved via `gateway/platforms/whatsapp_common.py:resolve_whatsapp_bridge_dir`). At inspection time the bridge dir was NOT installed (no `npm install` run, `requestPairingCode` absent anywhere in the tree).
- `grep -rln "requestPairingCode"` across the whole install → **no matches**. Confirms the 8-digit device-link code does NOT exist in Hermes.

## Official doc (github.com/NousResearch/hermes-agent, main branch)
File: `website/docs/user-guide/messaging/whatsapp.md` (last touched Jun 10 2026). Key points:
- "Hermes connects to WhatsApp through a built-in bridge based on **Baileys**. This works by emulating a WhatsApp Web session — **not** through the official WhatsApp Business API."
- Pairing step: wizard prints a **QR code** in the terminal; user scans via Settings → Linked Devices → Link a Device. **No 8-digit alternative mentioned.**
- "By default, unauthorized DMs still receive a pairing code reply." → this is the **user-authorization pairing code** (for allowing a DM sender), NOT a device-link code. Easy to confuse — flag it.
- Ban-risk warning is explicit in the doc (unofficial API).
- `hermes whatsapp` also installs bridge deps via `npm install` (needs Node 18+).

## Capability matrix (Baileys / personal number)
| Action | Possible |
|--------|----------|
| Read all incoming (contacts + groups) | YES — only when bridge points at the personal number |
| Send text / media | YES |
| Delete own sent messages | YES (time-limited, like the app) |
| Manage groups (leave/create) | YES |
| Block contacts | YES |
| Change number / delete account | NO |
| Change 2-step PIN | NO |
| Delete other people's messages | NO |
| Read other numbers (bot mode) | NO — bot mode only sees the bot number |
| Read self-chat only (self-chat mode) | YES — but limited to self-chat |

## Env vars (~/.hermes/.env)
WHATSAPP_ENABLED=true | WHATSAPP_MODE=bot|self-chat | WHATSAPP_ALLOWED_USERS=15551234567 (no +) or *
config.yaml: whatsapp.unauthorized_dm_behavior: ignore
