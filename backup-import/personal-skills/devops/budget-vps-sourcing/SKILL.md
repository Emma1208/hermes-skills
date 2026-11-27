---
name: budget-vps-sourcing
description: Find a cheap VPS (under ~$4-5/mo) for a user with payment constraints — African/international cards that get rejected, no big upfront sum, no passport/KYC. Built around hosting Hermes 24/7 but generalizes.
---

# Budget VPS Sourcing (constrained payment)

## When this applies
A user needs a server (run Hermes 24/7, host a bot, self-host) under a tight budget, especially with payment friction: cards rejected internationally, low card balance, no passport/KYC, wants monthly not annual.

## First rule: separate "true monthly" from "annual promo"
Most "<$4/mo" deals are **annual-only** (prepay the year; the monthly equivalent is higher). Always state the billing period. Don't present an annual promo price as "per month" — the user gets surprised at checkout.

## Provider snapshot (mid-2026)
| Provider | True monthly | Min upfront | RAM | Payment | Notes |
|----------|-------------|-------------|-----|---------|-------|
| Hetzner CX11 | ~4.10€/mo | **$25 account credit** (NOT server price) | 2 GB | Card/PayPal | Most reliable EU; the $25 is verification credit, blocks low-balance cards |
| RackNerd | ~4.50$/mo monthly / ~0.92$/mo annual | annual prepay | 1 GB | Card | Cheap promos are ANNUAL only |
| Oracle Cloud Free Tier | **$0** | card test (~1-10$, refunded) | 1 GB ×2 VMs | Card | 0$ but OFTEN rejects African/RDC cards; 1/8 vCPU; EU regions only |
| RamNode | ~4$/mo | **$3 min cloud credit** | 1 GB | Card/PayPal/**Crypto** | Hourly billing, no annual lock — best flexible |
| Host4Fun | 3$/mo annual / 5$/mo monthly | annual | 1 GB | Card/PayPal (claims "no bank") | |
| VPSDime | 5$/mo | 1st month | 1 GB | Card/Prepaid/ApplePay | Takes virtual/prepaid cards |
| Cloudzy | 2.48$/mo | low | 1 GB | **Perfect Money**, crypto | Good if user has a PM wallet |
| bithost.io | ~4-5$/mo | none | 1 GB | **Bitcoin, NO KYC** | Zero passport, zero card |
| HostBrr | 2-3€/mo | low | 1 GB | Crypto | EU, minimal verification |
| Regxa | 4.50$/mo | low | 1 GB | Crypto (no KYC) | Offshore |

## African payment unlock
- **Orange Money / Airtel Money virtual Visa card (VisaPay, RDC)** can pay international VPS like a normal Visa — unlocks Hetzner/RamNode/Host4Fun. ASK the user if they have Orange/Airtel Money before assuming card rejection.
- Crypto (USDT/BTC) via bithost/HostBrr/Cloudzy avoids the card entirely.
- Perfect Money via Cloudzy.

## RAM guidance for Hermes
- Hermes gateway (Telegram) alone: 512 MB–1 GB is fine.
- + WhatsApp Baileys bridge: +300–500 MB. On a 1 GB VM it's tight but works.
- Oracle Free Tier 1 GB suffices for Hermes+Telegram; for Hermes+WhatsApp prefer 2 GB (Hetzner) or split across the two free VMs.

## Recommended path by what the user has
- Has Visa/Mastercard (even prepaid/virtual) → **RamNode** ($3 min, hourly, monthly) or **VPSDime**.
- Card rejected / no card → **bithost** (Bitcoin) or **Cloudzy** (Perfect Money).
- Wants $0 and a card that might pass → try **Oracle Free Tier** (warn: often rejected for RDC).
- Has Orange/Airtel Money → virtual Visa → then RamNode/Hetzner.

## Pitfalls
- Hetzner's $25 is account credit, not the server cost; it funds ~5-6 months then bills from credit.
- Oracle Free Tier: must select **"Always Free"** explicitly; "Pay as you go" can incur charges. Shape = VM.Standard.E2.1.Micro.
- Avoid obscure "VPS Congo / local" resellers for a 24/7-critical bot — reliability unknown.
- The user (Emmanuel, Kinshasa/RDC) repeatedly hits card-balance and card-rejection walls — lead with the Orange/Airtel Money virtual Visa or crypto path rather than card-only providers.

## references/
- `references/vps-providers-2026.md` — fuller comparison, regional ping notes (Kinshasa → EU/US), signup quirks.
