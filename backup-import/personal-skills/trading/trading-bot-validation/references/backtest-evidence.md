# Backtest Evidence (real runs, 2026-07-12)

## Deriv binaries — synthetic 20k ticks (geometric random walk)
Framework: deriv_bot/run_backtest.py. EV derived from real tick movement (CALL=next>entry, PUT=next<entry, DIGITDIFF=last-digit differs). Risk: 0.5% base, martingale capped 4 levels, kill daily_loss 3% / 3 consec SL.

| Strategy | WR | EV/trade | Total | PF | Kill |
|----------|-----|----------|-------|-----|------|
| digit_diff (payout 1.09) | 89.6% | -0.0082 | -3.08% | 0.85 | daily_loss |
| call_put (payout 1.92) | 46.2% | -0.0723 | -0.94% | 0.84 | consec_sl |
| r100 (payout 1.0) | 25% | -0.8750 | -3.50% | 0.00 | daily_loss |

All NO EDGE. DIGITDIFF proves the trap: 89% WR but negative EV (payout too low).

## Trend follower — REAL Binance BTCUSDT 4h candles
Framework: deriv_bot/run_trend_backtest.py + sweep_trend.py. SMA(50)+MACD(12,26,9) entry, ATR(14) SL 1.5-2x + trailing 2-3x, 1% risk/trade. Tested 12 param combos.

Bearish window (88347 -> 63991, -27%):
  Best: SMA50 SL2.0 TRAIL3.0 -> -0.9% (PF 0.95). Worst: -15.5%.

Bullish window (42016 -> 60246, +43%, 2024-02..05):
  Best: SMA50 SL1.5 TRAIL3.0 -> +0.0% (PF 1.00). Worst: -8.3%.

Conclusion: naive trend follower has NO edge on BTC 4h. Even +43% market ends flat.
To get edge: add regime filter (SMA200 bullish), test Daily/Weekly, or other markets (EURUSD).

## Range-breakout — REAL Binance candles (BTC + gold + EUR)
Framework: deriv_bot/run_breakout_backtest.py, run_breakout_filtered.py, run_forex.py, run_weekly.py.
Donchian PER10/20/50 + optional MM200 filter, ATR(14) SL 1.5-2x + trail 3x, 1% risk/trade.

BTCUSDT 4h (recent bear 88347->63991): PER10 no-filter -> +5.2% (PF 1.24); MM200 PER10 -> +3.3% (PF 1.26).
BTCUSDT 4h walk-forward OOS: 2023 UP +0.7% (PF1.02), 2022 bear -5.3% (PF0.85), 2023 daily -2.3% (PF0.87), 2021 bull +1.4% (PF1.11). -> INTERMITTENT, not robust.
BTCUSDT 1w (465wk, 4086->63910): all configs positive, PER50 no-filter +3.8% (PF 2.81) but only 6 trades in 9y = too slow.
PAXGUSDT 1d (gold, 1919->4100, 1000 candles): **MM200 PER10 +17.3% (PF 2.25, DD 3.6%); PER20 +16.4% (PF 2.34); PER50 +14.6% (PF 2.82). ALL MM200 configs positive.** <- FIRST REAL EDGE.
XAUTUSDT 1d: only 109 candles, 0 trades (insufficient data).
EURUSDT 1d: flat, best none PER20 +0.5% (PF 1.02).

## First viable live candidate
Gold (PAXG) range-breakout + MM200, Daily. Caveat: ~1000 daily candles since 2021 => few trades (19-31). Confirm with more data, then paper-trade 2wk, then 50$ real ONLY if edge holds.

## Lessons (updated)
- Never present Deriv binaries as a tradable edge; show EV math.
- One window (bull or bear) is not proof; sweep params + test opposing regimes.
- Honest "NO EDGE" output is the correct, valuable result — not a failure.
- MM200 trend filter is market-dependent: HURT BTC breakout, HELPED gold breakout. Test, don't assume.
- Gold's structural uptrend is where the Donchian+MM200 edge actually lives for this user.
