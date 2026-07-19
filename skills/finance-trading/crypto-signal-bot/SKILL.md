---
name: crypto-signal-bot
description: Build, backtest, and optimize an automated crypto trading-signal bot (Telegram delivery) in pure Python stdlib — no requests/pandas. Use when the user wants to build a trading signal service, backtest a crypto strategy, or tune RSI/EMA parameters against real Binance data.
---

# Crypto Signal Bot (pure-stdlib)

Build an automated crypto signal generator + backtester + parameter optimizer using
ONLY the Python standard library (`urllib`, `json`, no `requests`/`pandas`). This avoids
the broken-Pillow / missing-`requests` problems common on Termux/musl and keeps the bot
deployable on any VPS with stock Python 3.

## When to use
- User asks to build a trading signal bot, crypto alerts service, or "business automatique" around signals.
- User wants to backtest a strategy or optimize RSI/EMA/TP-SL parameters on real data.
- User is an ex-Forex analyst / wants a subscription signal product (see Monetization below).

## Hard constraints & environment notes
- **No third-party deps.** Binance market data is PUBLIC — no API key needed. Use
  `urllib.request` + `urllib.parse`, NOT `requests` (often missing on Termux/musl).
- This user expects **all replies and generated document/content in French**. Code/comments
  may stay English, but user-facing messages, signal text, and reports must be French.
- Add a **retry loop** around every `urlopen` — Binance public endpoints drop connections
  intermittently (saw `read operation timed out`); 3 retries with 2s sleep fixes it.

## Workflow (proven sequence from a real build)
1. **Prototype the bot** — fetch klines, compute RSI(Wilder)+EMA, detect signal, format, send.
   Start in `dry_run` (console) mode; verify live before wiring Telegram.
2. **Backtest on REAL history** — replay strategy on `klines` and simulate TP/SL hit candle-by-candle.
   Report: #trades, win rate (WR), cumulative %, breakeven WR, best/worst trade.
3. **Optimize** — grid-search parameters; keep only configs with WR ≥ breakeven AND ≥20 trades
   (small samples are not statistically valid).
4. **Pick winning pairs** — test multiple symbols; a strategy that wins on SOL may lose on BTC.
   Launch on validated pairs only.
5. **Monetize (separate step)** — Telegram channel + subscription + Mobile Money/Flutterwave.
   NOT covered in code here; flag it as the next phase.

## ⚠️ CRITICAL STRATEGY PITFALL (easy to get backwards)
The naive "buy when RSI oversold AND price above EMA_slow" is **self-contradictory**:
when RSI is oversold, price is *below* EMA_slow. The original build had this bug → 0 signals,
a real wasted cycle. Correct logic = **buy the dip inside an uptrend**:
- BUY:  `rsi < rsi_oversold` AND `price < ema_slow` AND `ema_fast >= ema_slow`
- SELL: `rsi > rsi_overbought` AND `price > ema_slow` AND `ema_fast <= ema_slow`
Trend is judged by EMA structure (`ema_fast >= ema_slow`), NOT by `price > ema_slow`.

## Risk/Reward math
- Derive TP from SL: `tp = entry * (1 ± sl_pct * rr)` (BUY +, SELL −). Do NOT use a fixed tp_pct.
- **Breakeven win rate = `1 / (1 + rr)`**. With rr=3.0 you only need **25% WR** to be profitable.
- This means leverage is on *signal quality* (filter noise), not on hitting 50% WR.

## Backtest core loop (TP/SL hit simulation)
```
for each candle i where indicators valid:
    if signal: entry, sl, tp computed
    for j in i+1 .. i+MAX_HOLD:
        if BUY and highs[j] >= tp: outcome=TP; break
        if BUY and lows[j]  <= sl: outcome=SL; break
        (mirror for SELL)
    if none hit within MAX_HOLD: mark EXPIRE -> compare final close vs entry
```
`MAX_HOLD` ~ 96 candles for 15m (1 day), ~168 for 1h (1 week).

## Compliance (do not skip)
- Always include "⚠️ Pas un conseil en investissement. DYOR." in signal text.
- Never promise a guaranteed return — legally risky and reputationally fatal.

## Files in this skill
- `templates/crypto_signal_bot.py` — full working bot (dry_run + Telegram), validated live on Binance. Copy and edit CONFIG.
- `scripts/optimizer.py` — grid-search optimizer; prints only rentable configs (WR≥breakeven, ≥20 trades). Run: `python3 optimizer.py`.
- Backtest module: reconstruct from the "Backtest core loop" above (or copy from a prior session); it is small.
