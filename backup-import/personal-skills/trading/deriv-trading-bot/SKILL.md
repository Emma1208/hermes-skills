---
name: deriv-trading-bot
description: Build/validate Deriv (Binary.com) automated trading bots with an edge-first, backtest-before-automate methodology. Covers tick-level backtesting, capped-martingale risk manager, kill-switches, and the Deriv strategy edge reality (high WR != edge).
triggers:
  - deriv bot / hermes trading / automatiser trading deriv
  - backtest strategie deriv / calcul EV strategie
  - DIGITDIFF CALL PUT R_100 volatility index / digit contract
  - trading automatique Emmanuel / bot crypto Deriv / edge first
---

# Deriv Trading Bot (edge-first)

Emmanuel trades Deriv (volatility indices, digit contracts). Profile: cap 10k$ (50$ virtual bot to start), risk 1%/trade, leverage 5x max, swing 3-10j, SL/BE/trail. The GOLDEN RULE: **backtest on real ticks before automating. EV must be positive after house costs.** Coding the executor first is wasted effort if there is no edge.

## Principle: edge-first, not code-first
A high win rate is NOT an edge — the payout must beat the house margin. On Deriv the documented reality:
- DIGITDIFF: WR 90-95% but payout ~1.09 → EV ≈ 0 (house takes it).
- CALL/PUT martingale: payout ~1.92 → ruin risk on streaks unless capped.
- R_100 (Volatility 100): ~50% WR, even-odds → EV ≈ 0 without external edge.

## Proven backtest framework structure (4 decoupled modules)
- `data/feed.py` — synthetic tick generator (self-test) + `load_ticks_csv()` for real ticks
- `data/collector.py` — Deriv WebSocket v3 tick collector (`{"ping":1}` every 20s keep-alive, token in `_token.py`, NEVER commit token)
- `strategy/` — signal ONLY (CALL/PUT/DIGITDIFF), NO money management mixed in
- `risk/manager.py` — position sizing + kill-switches
- `backtest/engine.py` — tick-level simulator; outcome derived from REAL tick movement, not fake probabilities

Outcome logic (backtest/engine.py): CALL wins if next tick > entry tick; PUT wins if next < entry; DIGITDIFF wins if last digit of next tick != last digit of entry tick.

## Risk manager rules (always encode these)
- base stake = 0.5% of capital (not 1%, keeps martingale safe)
- martingale capped at 4 levels (x1→x2→x4→x8 → RESET; never keep doubling = ruin protection)
- kill if daily loss > 3%
- kill if 3 consecutive SL

## Real finding (backtest on 20k synthetic ticks, default payouts)
| Strategy | WR | EV/trade | Verdict |
|----------|-----|----------|---------|
| digit_diff (payout 1.09) | 89.6% | −0.0082 | NO EDGE |
| call_put (payout 1.92) | 46.2% | −0.0723 | NO EDGE |
| r100 (payout 1.0) | 25% | −0.8750 | NO EDGE |

Lesson: even 89% WR loses when payout is too low. **If EV ≤ 0, do NOT trade — find a real edge first** (volatility structure, liquid hours, patterns the house doesn't price).

## Ideal workflow
1. Collect real ticks (collector.py, token in `_token.py`)
2. Backtest on real ticks + walk-forward (train 4mo, test 1mo, never same data)
3. Paper trade 2 weeks (50$ virtual) — check slippage + execution
4. Go live 50$ only if EV > 0 over 100+ trades, then scale

See references/backtest-engine.md for the exact simulator logic and Deriv contract quirks. Framework tested on Python 3.11/3.13 (Termux proot Debian) — NOT 3.14.
