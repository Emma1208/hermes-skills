---
name: hermes-whatsapp-setup
description: Set up Hermes to read/write/manage WhatsApp — personal account (Baileys bridge, QR) vs WhatsApp Business Cloud API (WABA). Covers capabilities, limits, single-phone QR workaround, and the mandatory permission gate before any config change.
---

# Hermes WhatsApp Setup

## When to use
The user wants Hermes to read, write, or manage WhatsApp. There are TWO unrelated methods — pick based on whether they want their *personal* account or a *separate business number*.

## ⛔ MANDATORY PERMISSION GATE (user-mandated, 2026-07-15)
**NEVER run `hermes whatsapp`, `hermes whatsapp-cloud`, or any `hermes gateway`/`hermes config` command that mutates state or starts pairing without the user's explicit "yes".**
The user explicitly said: *"touche pas au paramétrage de Hermes sans ma permission"*.
- ✅ Allowed without permission: `hermes whatsapp --help`, `hermes whatsapp-cloud --help`, reading source under `plugins/platforms/whatsapp/` and `gateway/platforms/`.
- ❌ Forbidden until explicit go-ahead: anything that writes creds, launches the bridge, or alters `.env`/gateway config.
- Always present the choice (A/B/C) and wait. Offer the plan; do not execute it.

## Method A — Personal account (Baileys bridge) → `hermes whatsapp`
- Sets up a **Baileys** bridge (`@whiskeysockets/baileys`) as a **Node.js subprocess**; pairs like WhatsApp Web.
- Pairs via **QR code** printed to the bridge log; session saved to `creds.json` (under the platform session path).
- **Can:** read all chats, send text/media, delete own sent messages (time-limited), manage groups (leave/create), block contacts.
- **Cannot:** change number, delete the account, change 2-step verification PIN, delete *other people's* messages.
- **Risk:** unofficial connection → Meta may temporarily ban the number (hours–days). Low if used lightly, but real.
- **Single-phone gotcha:** QR needs a 2nd screen. Options: (a) display the QR on another device (friend's phone, cyber café PC) and scan with your own phone — THIS IS THE ONLY WORKING METHOD. (b) **There is NO 8-digit pairing-code alternative** — `requestPairingCode` is NOT present in Hermes's bundled Baileys bridge. VERIFIED (2026-07-15) by reading the bridge source (no `requestPairingCode` symbol) and the official doc `github.com/NousResearch/hermes-agent → website/docs/user-guide/messaging/whatsapp.md` (Jun 10 2026), which states pairing is **QR-code only**. The "pairing code" mentioned in Hermes docs refers to a DIFFERENT thing: the code Hermes sends an unknown DM *sender* to authorize that user — NOT a device-link code. Never promise an 8-digit code to a single-phone user; offer the temporary-2nd-screen QR method instead.

## Method B — WhatsApp Business Cloud API (WABA) → `hermes whatsapp-cloud`
- Official Meta API. Spins up a **separate business number** — does **NOT** access the user's personal chats/contacts/groups.
- **Requirements:** Meta Business Manager (business.facebook.com), a dedicated phone number (can be virtual: Twilio/Vonage), a Facebook Developer app of type "Business" (developers.facebook.com), and a **public webhook URL** (problem for local-only hosts → needs ngrok or a hosted server).
- Meta bills after ~1000 free messages/month. No QR — pure API.
- **Use when:** avoiding ban risk or running a business number. **Does NOT satisfy "manage my personal account."**

## Quick decision guide
| Goal | Method |
|------|--------|
| Manage my existing personal WhatsApp (chats, contacts, groups) | **A only** |
| Avoid ban risk / run a business number | **B** |
| Want both personal + business | Both (different numbers) |

## Setup steps (ONLY after explicit permission)
1. Confirm method A or B with the user (offer A/B/C, wait).
2. **Verify Node:** `node --version` (Hermes needs a Node subprocess for the Baileys bridge).
3. Method A: run `hermes whatsapp`; surface the QR to the user for scanning. For a single-phone user, arrange a temporary 2nd screen (friend's phone logged into their Telegram to receive the QR image, or a cyber café PC). There is NO 8-digit code fallback — do not offer one.
4. Method B: collect Meta Business Manager + number + developer app + public webhook (ngrok if local); then `hermes whatsapp-cloud`.
5. After pairing, run `hermes gateway status` to confirm connected.

## Pitfalls
- **Local-only host has no public IP** → WABA webhook needs ngrok/tunnel or a hosted server.
- **Missing `creds.json`** → bridge prints QR and never reaches `status:connected`.
- Don't confuse the two: WABA ≠ personal account. Telling a user WABA will "manage my account" is wrong.
- Investigate read-only first; the user gets annoyed if you start mutating Hermes config unprompted.

## References
- `references/baileys-vs-cloud.md` — command map, capability matrix, and the exact source locations inspected.
