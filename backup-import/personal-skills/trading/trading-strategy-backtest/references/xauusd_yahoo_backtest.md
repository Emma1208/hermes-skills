# XAUUSD spot backtest via Yahoo Finance (2026-07-17 session)

## Data sourcing — CRITICAL
Yahoo Finance does NOT list raw spot forex symbols the way you'd expect:
- `XAUUSD`  -> 404 "Quote not found"
- `XAUUSD=X` -> 404 "possibly delisted; no price data found"
- `GC=F` (COMEX gold FUTURES, USD/oz) -> WORKS, ~124 daily candles for 6mo.
  Price tracks XAUUSD spot almost 1:1 (same unit, USD/oz). Use `GC=F` as the
  XAUUSD proxy. `GLD` (ETF) and `GOLD` (Barrick) are NOT the spot price.

```python
import yfinance as yf
df = yf.download("GC=F", period="6mo", interval="1d",
                 progress=False, auto_adjust=False)
close = df["Close"].squeeze()   # squeeze: yf returns MultiIndex columns
```

## pandas 3.0 gotcha
`DataFrame.last("6mo")` was REMOVED in pandas 3.0 -> AttributeError.
Slice by date instead:
```python
start = df.index[-1] - pd.DateOffset(months=6)
sub = df.loc[start:]
```

## Long/short backtest engine (daily, no leverage, no fees)
```python
def backtest(pos_target, prices):
    pos = pos_target.ffill().fillna(0.0)        # held until next signal
    ret = prices.pct_change().fillna(0.0)
    strat = pos.shift(1) * ret                  # fill at NEXT open
    eq = (1 + strat).cumprod()
    return dict(ret=eq.iloc[-1]-1,
                dd=((eq-eq.cummax())/eq.cummax()).min(),
                sharpe=np.sqrt(252)*strat.mean()/(strat.std()+1e-9))
```
pos_target is a Series of -1 / 0 / +1 (short / flat / long).

## Findings (XAUUSD, 6mo window 2026-01-20..2026-07-17 = bear, -16.6% B&H)
Single-window result is a TRAP:
- MACD trend-following (short during down-trend) nearly broke even (-1.6%)
  vs B&H -16.6% — looks like the "best" on this window.
- But over 5y multi-window (6mo/1y/2y/3y/5y): MACD LOSES every window (-20% avg)
  because gold's secular uptrend punishes persistent shorting.
- SMA10/30 trend-following: +15.9% avg, 4/5 windows positive.
- SMA + RSI-extreme filter (cut long if RSI>70, cut short if RSI<30):
  +14.4% avg, lower DD, best Sharpe (0.45), 4/5 windows positive.
=> Most ROBUST for XAUUSD: SMA trend-follow WITH extreme-RSI cut.

## Lesson
Always run MULTI-WINDOW (different start dates / lengths) before calling any
strategy "best". A strategy that wins on one regime (here, the bear 6mo window)
can be the worst over the full history. Confirm with train/test split.
