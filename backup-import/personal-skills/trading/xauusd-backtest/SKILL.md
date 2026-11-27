---
name: xauusd-backtest
description: Reusable pipeline to backtest XAUUSD (gold spot, proxied by GC=F futures) and find the best trading strategy across multiple time windows, with realistic fees (spread + swap). Produces a regime-aware long/short strategy that is robust across bull and bear markets.
---

# XAUUSD Backtest Pipeline

Find the best trading strategy for XAUUSD by backtesting several strategies across
multiple time windows, then confirm robustness with realistic fees.

## Key findings (so the agent doesn't re-derive every time)

- **XAUUSD proxy on Yahoo = `GC=F`** (gold futures, USD). `XAUUSD=X` returns 404.
- Best strategy = **REGIME-AWARE long/short**:
  - Detect market regime with a LONG SMA (e.g. 100–200d, or `n//3` of window).
  - Long (buy) only when short SMA(10) > long SMA(30) AND price > regime MA.
  - Short (sell) only when short SMA(10) < long SMA(30) AND price < regime MA.
  - This avoids fighting the trend — the killer mistake that destroys MACD/
    mean-reversion strategies over 5 years.
- Results over 5 windows (6mo→5y): REGIME-AWARE **+17.4% avg, 5/5 winning,
  Sharpe 0.45, only 0.37% fees** (spread ±0.40 USD/oz, swap long -0.015%/d,
  short -0.005%/d). Beats Buy&Hold, SMA-trend, SMA+RSI, and MACD on every window.
- **MACD trend is the worst** (-20% avg, 0/5) — it shorts against a major bull run.
- **Mean-reversion (RSI/Bollinger) overtrades** → high fees in live conditions.

## Pipeline steps

1. Install deps in the numpy venv: `yfinance` (data), `ta` (indicators),
   `pandas`, `numpy`, `matplotlib` (already in `/root/numpy-venv`).
2. Fetch: `yf.download("GC=F", period="5y", interval="1d", auto_adjust=False)`.
3. Compute indicators with `ta`: SMA(10), SMA(30), RSI(14), MACD(12,26,9),
   plus a long regime SMA.
4. Build strategy position series (-1/0/+1) for each candidate.
5. Backtest engine: `pos.ffill()`, daily return `pos.shift(1) * price.pct_change()`,
   equity = cumprod. With fees: subtract spread on every position switch
   (`SPREAD / price`) and add daily swap per held position.
6. Score each strategy per window: total return, max drawdown, Sharpe, fee%.
7. Rank by average return AND count of winning windows (robustness > raw return).
8. Save a plot of top-3 equity curves vs Buy&Hold.

## Rules / pitfalls

- pandas 3.0 removed `.last()` — use `df.loc[df.index[-1] - pd.DateOffset(...):]`.
- Always compare against **Buy&Hold** and test on MULTIPLE windows, not one
  (a single bear window makes trend-following look like a loser).
- Include fees — they flip SMA/RSI from winner to loser over 5 years.
- `ta` has no `__version__` attribute (import check prints `?`, that's fine).
- Single pair, single history → no guarantee of future performance.

## Reference files

- `references/backtest_regime.py` — full self-contained regime-aware backtest
  with fees, multi-window, ready to run via `/root/numpy-venv/bin/python`.
- Other legacy scripts live in `/root/`: `backtest_xauusd.py` (long-only),
  `backtest_xauusd_short.py` (long/short), `backtest_multiframe.py` (robustness),
  `backtest_fees.py` (fees-only comparison).
