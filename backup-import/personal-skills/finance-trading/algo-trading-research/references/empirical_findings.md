# Empirical findings — trading strategy backtests (2026-07 session)

All tests run on REAL Binance klines (public API, no account). Strategy = modular
Python framework (range_breakout.py / trend_follower.py + candle_engine.py with ATR
SL 1.5-2x + trailing stop 2-3x ATR, 1% risk/trade). Verdict = profit factor (PF);
PF > 1.2 OOS considered a real edge.

## Deriv (house game — NO EDGE possible)
Backtested on 20k synthetic ticks (structure mirrors Deriv):
| strategy   | WR     | EV/trade | verdict   |
|------------|--------|----------|-----------|
| digit_diff | 89.6%  | -0.0082  | NO EDGE   |
| call_put   | 46.2%  | -0.0723  | NO EDGE   |
| r100       | 25%    | -0.8750  | NO EDGE   |
Conclusion: payouts pre-set so EV ≤ 0 by construction. Do not trade for edge.

## BTC 4h range breakout (in-sample vs out-of-sample)
In-sample: PER10/SL2/TR3 = +8.0% PF 1.32 (recent down mkt); PER20/SL2/TR3 = +1.9% PF 1.21 (2024 bull).
Walk-forward OOS:
| window              | PER10/SL2/TR3 | PF   |
|---------------------|---------------|------|
| 2023 4h (up)        | +0.7%         | 1.02 |
| 2022 bear 4h (down) | -5.3%         | 0.85 |
| 2023 daily (up)     | -2.3%         | 0.87 |
| 2021 bull daily     | +1.4%         | 1.11 |
Verdict: unstable, NOT reliable for real money.

## BTC weekly (1w) range breakout — all configs positive but slow
465 weeks (4086 -> 63910). Best none PER50 = +3.8% PF 2.81; none PER10 = +3.5% PF 1.46;
MM200 PER20 = +3.0% PF 2.49. Only 6-17 trades in 9y -> minimal capital growth.

## BTC 4h naive trend follower (SMA50 + MACD) — too simple
Full window (88347->63991 down): +0.0% WR 38.5% PF 0.79. 2024 bull (42016->60246 +43%):
+0.0% PF 1.00. Even in a strong bull it breaks even -> no edge.

## GOLD / PAXG (Binance tokenized gold) daily + MM200 filter — STRONGEST EDGE
| config            | gain   | PF   | DD   | trades |
|-------------------|--------|------|------|--------|
| MM200 PER10       | +17.3% | 2.25 | 3.6% | 31     |
| MM200 PER20       | +16.4% | 2.34 | 4.3% | 26     |
| MM200 PER50       | +14.6% | 2.82 | 2.0% | 19     |
| none PER50        | +14.2% | 2.61 | 1.8% | 21     |
All MM200 configs positive. Recommended candidate for virtual bot.

## EURUSD daily breakout — flat
EURUSDT 1d (1.06 -> 1.14). Best none PER20 = +0.5% PF 1.02. No edge.

## XAUUSDT / XAUTUSDT notes
- XAUUSDT: NOT listed on Binance spot (HTTP 400 Bad Request).
- XAUTUSDT (Tether Gold): only 109 daily candles -> 0 trades, unusable.
- PAXGUSDT: ~1000 daily candles since 2021, sufficient, best edge.

## Virtual bot built
deriv_bot/execution/virtual_bot.py — simulated live bot on PAXGUSDT 1d, MM200+PER10,
prints equity/DD/wins. Tested in --demo mode (FLAT, no breakout on last candle — expected).
