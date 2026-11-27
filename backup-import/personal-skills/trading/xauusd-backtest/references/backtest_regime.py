#!/usr/bin/env python3
"""
Backtest XAUUSD — Stratégie RÉGIME-AWARE.
Détecte bull/bear via une longue SMA, puis :
  - regime haussier : autorise LONG (SMA10/30), interdit SHORT
  - regime baissier : autorise SHORT (SMA10/30), interdit LONG
Compare contre S1, S6, MACD, Buy&Hold sur 5 fenêtres.
Venv: /root/numpy-venv/bin/python
"""
import numpy as np
import pandas as pd
import yfinance as yf
import ta

def indicators(close):
    sma_s = ta.trend.SMAIndicator(close, window=10).sma_indicator()
    sma_l = ta.trend.SMAIndicator(close, window=30).sma_indicator()
    rsi   = ta.momentum.RSIIndicator(close, window=14).rsi()
    macd  = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    return sma_s, sma_l, rsi, macd.macd(), macd.macd_signal()

def backtest(pos_target, prices):
    pos = pos_target.ffill().fillna(0.0)
    ret = prices.pct_change().fillna(0.0)
    strat = pos.shift(1) * ret
    eq = (1 + strat).cumprod()
    return dict(ret=eq.iloc[-1]-1,
                dd=((eq-eq.cummax())/eq.cummax()).min(),
                sharpe=np.sqrt(252)*strat.mean()/(strat.std()+1e-9))

# ---------- Récupération ----------
print("==> XAUUSD 5 ans...")
df = yf.download("GC=F", period="5y", interval="1d", progress=False, auto_adjust=False)
df = df[["Close"]].copy(); df.columns = ["Close"]; df = df.dropna()
print(f"    {len(df)} bougies {df.index[0].date()} -> {df.index[-1].date()}")

offsets = [pd.DateOffset(months=6), pd.DateOffset(years=1), pd.DateOffset(years=2),
           pd.DateOffset(years=3), pd.DateOffset(years=5)]
labels  = ["6 mois", "1 an", "2 ans", "3 ans", "5 ans"]

names = ["S1 SMA trend", "S6 SMA+RSI", "S3 MACD", "REGIME-AWARE"]
summary = {n: [] for n in names}

for off, lab in zip(offsets, labels):
    sub = df.loc[df.index[-1]-off:]
    close = sub["Close"]
    sma_s, sma_l, rsi, macd_l, macd_s = indicators(close)

    # S1 : long/short SMA10/30
    s1 = pd.Series(index=close.index, dtype=float)
    s1[sma_s > sma_l] = 1.0; s1[sma_s < sma_l] = -1.0

    # S6 : SMA10/30 + coupe RSI extrêmes
    s6 = s1.copy()
    s6[rsi > 70] = 0.0; s6[rsi < 30] = 0.0

    # S3 : MACD
    s3 = pd.Series(index=close.index, dtype=float)
    s3[macd_l > macd_s] = 1.0; s3[macd_l < macd_s] = -1.0

    # REGIME-AWARE : longue SMA = max(30, n//3)
    n = len(close)
    long_w = max(30, n // 3)
    regime_ma = ta.trend.SMAIndicator(close, window=long_w).sma_indicator()
    bull = close > regime_ma
    reg = pd.Series(0.0, index=close.index)
    reg[(sma_s > sma_l) & bull] = 1.0     # long seulement en hausse
    reg[(sma_s < sma_l) & ~bull] = -1.0    # short seulement en baisse
    reg = reg.ffill().fillna(0.0)

    bh = (close.iloc[-1]/close.iloc[0]) - 1
    strats = {"S1 SMA trend": s1, "S6 SMA+RSI": s6, "S3 MACD": s3, "REGIME-AWARE": reg}
    row = [f"{lab:<7} BH {bh*100:>6.1f}%"]
    for nn in names:
        r = backtest(strats[nn], close)
        summary[nn].append((r["ret"], r["dd"], r["sharpe"]))
        row.append(f"{nn.split()[0]:<4} {r['ret']*100:>6.1f}%")
    print(" | ".join(row))

print("\n==> RÉSUMÉ robustesse (moyenne 5 fenêtres)\n")
print(f"{'Stratégie':<16}{'Rend moy':>10}{'DD moy':>10}{'Sharpe':>9}{'Gagn/Rot':>10}")
print("-"*55)
res = []
for nn in names:
    rets=[x[0] for x in summary[nn]]; dds=[x[1] for x in summary[nn]]; shs=[x[2] for x in summary[nn]]
    win=sum(1 for x in rets if x>0)
    res.append((nn, np.mean(rets), np.mean(dds), np.mean(shs), win, len(rets)))
res.sort(key=lambda x:x[1], reverse=True)
for nn,mr,md,ms,win,tot in res:
    print(f"{nn:<16}{mr*100:>9.1f}%{md*100:>9.1f}%{ms:>9.2f}{win:>5}/{tot:<4}")
print("-"*55)
best=res[0]
print(f"\n==> PLUS ROBUSTE : {best[0]}  (moy {best[1]*100:.1f}%, {best[4]}/{best[5]} gagnantes)")
