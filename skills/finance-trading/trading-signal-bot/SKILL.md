---
name: trading-signal-bot
description: Build automated trading-signal services (crypto/Forex) end-to-end — market data → indicator analysis → signal generation → Telegram delivery → backtesting BEFORE monetization. Covers the classic strategy-design pitfalls (contradictory trend filters that produce ZERO signals), a zero-dependency Python HTTP pattern (urllib instead of requests), and RDC legal/compliance notes. Use when the user wants a trading bot, signal service, "bot de trading", "signaux", copy-trading, or prop-firm automation.
---

# Automated Trading Signal Bot

End-to-end pattern for a recurring, "set-and-forget" signal business: a bot scans markets 24/7, detects opportunities, and pushes BUY/SELL signals (entry, TP, SL, RSI, trend) to Telegram subscribers.

## When to use
- User asks for a trading bot, signal service, copy-trading setup, or prop-firm automation.
- User is exploring automated online business ideas in the trading/finance space.

## Architecture (the pipeline)
```
[Market data API] → [Indicator engine] → [Signal filter] → [Telegram delivery] → [Subscribers]
```
- Data: Binance public klines (`/api/v3/klines`) — **no API key** needed for market data.
- Engine: pure-Python RSI (Wilder) + EMA(20) + EMA(50). No pandas/numpy required.
- Delivery: Telegram bot (`python-telegram-bot` not even needed — use `urllib`).
- Hosting: any VPS (Contabo/Render) running the script with `nohup` or a systemd timer.

## Golden rule: BACKTEST BEFORE YOU MONETIZE
Never sell signals on a strategy you have not replayed on real history. A naive RSI/EMA filter often loses money or fires almost never. Always run the backtest harness (scripts/backtest.py) over 30+ days of real data and report the win rate honestly. In our live test: BTC 33% WR, ETH 22% WR, SOL 75% WR over ~30d — proof the raw strategy was NOT viable as-is and needed parameter/regime filtering before any paid launch.

## CRITICAL PITFALL — contradictory trend filter (produces ZERO signals)
The most common bug: combining RSI-oversold with "price above EMA50" in one AND condition.
- RSI < 35 means price just dropped hard → price is **below** EMA50 and EMA20 is **below** EMA50.
- Requiring `price > EMA50` simultaneously makes the condition **mathematically impossible** → 0 signals ever.

CANONICAL fix ("buy the dip in an uptrend"):
```
BUY  = RSI oversold  AND price < EMA_slow AND EMA_fast >= EMA_slow
SELL = RSI overbought AND price > EMA_slow AND EMA_fast <= EMA_slow
```
The trend is defined by EMA structure (fast vs slow), NOT by price-vs-EMA at the trigger candle. Keep this function **identical** in the live bot and the backtest — divergence between them invalidates the backtest. See `signal_conditions()` in scripts/crypto_signal_bot.py.

## Zero-dependency HTTP pattern
`requests` is often unavailable in minimal/PRoot/termux-like environments (`pip install requests` fails). Use stdlib `urllib.request` + `urllib.parse` instead — zero external deps, works everywhere. Add a retry loop (3×, 2s backoff) because public APIs drop connections. See both scripts.

## Monetization & compliance (RDC / francophone Africa)
- Abonnement mensuel (Mobile Money / Flutterwave / Stripe). Start 10–35 $ (≈15k–50k FC).
- Always include "⚠️ Pas un conseil en investissement. DYOR." in every signal.
- NEVER promise a guaranteed return — legally risky and reputationally fatal.
- Build a free public Telegram channel first as social proof, then upsell the paid signal group.

## Build sequence
1. Pick market (crypto easier to start; Forex needs broker API — user is ex-Forex analyst, leverage that).
2. Define edge; implement `signal_conditions()` (canonical logic above).
3. Run `python3 backtest.py` over 30d real data → measure win rate; iterate params.
4. Only after a viable WR (>55% with sensible R:R), wire Telegram (BotFather token + chat_id, `dry_run=False`).
5. Deploy on VPS; add payment + legal disclaimer.

## Support files
- `scripts/crypto_signal_bot.py` — working zero-dep prototype (Binance + RSI/EMA + Telegram, dry-run console mode).
- `scripts/backtest.py` — replays the SAME `signal_conditions()` on real Binance history; prints win rate + cumulative PnL.
- `references/strategy-pitfalls.md` — the contradictory-filter bug, real backtest numbers, and tuning notes.
