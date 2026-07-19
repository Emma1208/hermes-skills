# Telegram Integration & Monetization (RDC)

## Create the bot (2 min)
1. Message @BotFather on Telegram -> /newbot -> choose name + username (must end `bot`).
2. Copy the token `123456:ABC...`. Validate: `GET https://api.telegram.org/bot<TOK>/getMe`.
   A 200 with `ok:true` and the bot username confirms it works.

## Wire it into the bot
In crypto_signal_bot.py CONFIG:
  "telegram_token": "<TOK>",
  "telegram_chat_id": "<ID>",   # group ID (see below)
  "dry_run": False
Send test: set dry_run=False, call send_telegram("...", CONFIG). Check Telegram received it.

## Get the target chat_id
- `getUpdates` conflicts with webhooks -> call `deleteWebhook` first.
- Add bot to the GROUP and make it ADMIN, then post any message there.
- Run scripts/get_chat_id.py (listens ~40s). It prints `chat_id` + type.
- Group IDs look like `-1001234567890`. A DM chat is type `private` (NOT a group).
  If you only ever see a `private` id, the message came from you DMing the bot, not the group.

## Compliance
- Always append: "⚠️ Pas un conseil en investissement. DYOR."
- Never promise a fixed gain. Backtest proof builds trust; promises are illegal risk.

## Monetization path (not yet coded — next steps B2/B3)
- B2 Access control: only paying users receive signals. Options:
  * Private group with join-by-payment (Telegram paid groups limited in RDC).
  * Bot validates a paid code / expiry before forwarding signals to the user's DM.
- B3 Payment (RDC): Flutterwave (cards + Mobile Money) or direct Mobile Money
  (Airtel Money / Moov / M-Pesa RDC). Webhook on successful payment -> activate access.
  Flutterwave test secret + webhook endpoint needed; store secrets in env, never in code.
- Pricing seen in session: 15,000–50,000 FC (~10–35 USD)/month subscription.
