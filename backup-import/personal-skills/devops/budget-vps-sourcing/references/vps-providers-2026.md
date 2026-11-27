# Budget VPS Providers — 2026 Snapshot (mid-year)

## Billing reality check
- Most "<$4/mo" deals = ANNUAL prepay. State the period. RackNerd/Hetzner promos especially.
- "True monthly" (no annual lock) providers: RamNode (hourly), Hetzner (monthly), VPSDime, bithost, HostBrr, Cloudzy, Regxa.

## Provider details (verified via web search 2026-07-15)
| Provider | Monthly | Min upfront | RAM | Pay methods | Region | Notes |
|----------|---------|-------------|-----|-------------|--------|-------|
| Hetzner CX11 | ~4.10€ | **$25 account credit** (verification, NOT server price) | 2 GB | Card/PayPal | EU (DE/FI) | Most reliable; $25 credit blocks low-balance cards |
| RackNerd | ~4.50$ monthly / ~0.92$ annual-eq | annual prepay (~$11/yr) | 1 GB | Card | US | Cheap promos annual-only |
| Oracle Free Tier | **$0** | card test ~1-10$ (refunded) | 1 GB ×2 VMs | Card | EU (Amsterdam/Frankfurt) | 0$ but OFTEN rejects RDC/African cards; 1/8 vCPU; must pick "Always Free" |
| RamNode | ~4$ | **$3 min cloud credit** | 1 GB | Card/PayPal/**Crypto** | NL/US | Hourly billing, no lock — best flexible |
| Host4Fun | 3$ annual / 5$ monthly | annual for 3$ | 1 GB | Card/PayPal (claims no bank) | 35+ loc | |
| VPSDime | 5$ | 1st month | 1 GB | Card/Prepaid/Apple/Google Pay | US | Takes virtual/prepaid cards |
| Cloudzy | 2.48$ | low | 1 GB | **Perfect Money**, crypto | — | Good if user has PM wallet |
| bithost.io | ~4-5$ | none | 1 GB | **Bitcoin, NO KYC** | — | Zero passport/card |
| HostBrr | 2-3€ | low | 1 GB | Crypto | EU | Minimal verification |
| Regxa | 4.50$ | low | 1 GB | Crypto (no KYC) | — | Offshore |

## African payment unlock (RDC/Kinshasa)
- **Orange Money / Airtel Money virtual Visa (VisaPay, RDC)** → pays international VPS like normal Visa. Ask the user if they have Orange/Airtel Money before assuming rejection.
- Crypto (USDT/BTC) → bithost / HostBrr / Cloudzy sidesteps the card entirely.
- Perfect Money → Cloudzy.

## Ping from Kinshasa
- EU (DE/NL/Amsterdam/Frankfurt): good, stable. US-East also acceptable. Prefer EU for latency to Telegram/WhatsApp endpoints.

## RAM for Hermes
- Gateway + Telegram: 512 MB–1 GB fine.
- + WhatsApp Baileys bridge: +300–500 MB. 1 GB works but tight; 2 GB (Hetzner) comfortable.
- Oracle 1 GB VM: fine for Hermes+Telegram; tight for Hermes+WhatsApp.

## User context (Emmanuel, Kinshasa/RDC)
- Repeatedly hits card-balance walls (no $25 for Hetzner) and likely card-rejection (Oracle).
- Lead with: Orange/Airtel virtual Visa, or crypto (bithost/HostBrr/Cloudzy), or RamNode's $3 min.
- Avoid obscure "VPS Congo" resellers for a 24/7-critical bot.
