# Deriv backtest engine — condensed reference

## Outcome logic (derive from REAL tick movement, never fake probabilities)
- CALL  wins if `next_tick > entry_tick`
- PUT   wins if `next_tick < entry_tick`
- DIGITDIFF wins if `last_digit(next) != last_digit(entry)`
  - `last_digit(x) = int(abs(round(x,1))*10) % 10`

## PnL & equity
- `stake` from risk manager.
- `pnl = stake * (payout - 1)` if won, else `-stake`.
- `equity += pnl` each trade.

## Loop
- `for i in range(len(ticks)-1)`: `sig = strategy.signal(ticks, i)`; skip if `None`.
- After each trade: `risk.on_result(won)`; check `risk.killed(equity)` → break with reason.

## RiskManager
- attrs: capital0, base=capital*base_pct (0.005), stake, level, max_levels (4),
  daily_loss_pct (0.03), max_consec_sl (3), consec_sl, day_start_equity, peak.
- on_result(won):
  - win → stake=base, level=0, consec_sl=0
  - loss → consec_sl+=1; if level < max_levels-1: level+=1, stake=base*2**level
          else (cap reached): stake=base, level=0  # RESET, no ruin
- killed(equity): returns "daily_loss" if equity < day_start_equity*(1-daily_loss_pct);
  returns "consec_sl" if consec_sl >= max_consec_sl; else None.

## Metrics reported
WR, EV/trade, total_return_pct, final_equity, max_drawdown_pct (peak-to-trough),
profit_factor (gross_win/gross_loss), kill_reason, equity_curve.

## Deriv reality checks (verified 2026-07-11, 20k synthetic ticks)
- digit_diff payout 1.09 → WR 89.6% but EV -0.0082 (NO EDGE)
- call_put  payout 1.92 → WR 46.2% EV -0.0723 (NO EDGE)
- r100      payout 1.0  → WR 25%   EV -0.875  (NO EDGE)
High WR != edge when payout is too low. EV<=0 → do NOT trade.

## Deploy note
Runs on Python 3.11/3.13 (Termux proot Debian). NOT 3.14.
Tokens in `deriv_bot/_token.py` (gitignored); example in `_token.py.example`.
Deriv WebSocket v3: `wss://ws.binary-api.com/v3?app_id=1089`, keep-alive `{"ping":1}` every 20s.
