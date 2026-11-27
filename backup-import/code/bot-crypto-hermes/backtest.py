#!/usr/bin/env python3
"""Backtest v5 : utilise le vrai scorer, R/R optimisé, capital 10k$."""
import json
import sys
from pathlib import Path

from scorer import score_symbol

SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","ADAUSDT","DOGEUSDT"]
CACHE_PATH = Path(__file__).with_name("backtest_cache.json")
CAPITAL = 10000.0
RISK_PER_TRADE = 0.01          # 1% du capital = 100$
MAX_POSITIONS = 2
TP_ATR_MULT = 2.0              # TP = 2x SL en ATR
SL_ATR_MULT = 1.0              # SL = 1x ATR
MIN_SCORE = 75                 # score minimum pour acheter
MAX_HOLD_BARS = 200            # ~200 jours max


def atr(bars, period=14):
    """Calcul ATR sur les barres."""
    if len(bars) < period + 1:
        return None
    trs = []
    for i in range(-period, 0):
        high = bars[i]["h"]
        low = bars[i]["l"]
        prev_close = bars[i-1]["c"] if i > -period else bars[i]["c"]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return sum(trs) / len(trs)


def simulate(strategy_name="v5 R/R=2.0"):
    if not CACHE_PATH.exists():
        raise SystemExit("backtest_cache.json manquant.")

    cache = json.loads(CACHE_PATH.read_text())
    data = cache.get("bars", {})
    if not data:
        raise SystemExit("backtest_cache.json invalide.")

    n = min(len(data[s]) for s in SYMBOLS)
    for s in SYMBOLS:
        data[s] = data[s][-n:]

    positions = {}   # sym -> {"qty", "entry", "idx", "sl", "tp", "pullback"}
    cash = CAPITAL
    trades = []
    equity_curve = []

    for i in range(n):
        btc_bars = data["BTCUSDT"][:i+1]
        btc_closes = [b["c"] for b in btc_bars]
        btc_ok = len(btc_closes) < 7 or (btc_closes[-1] - btc_closes[-7]) / btc_closes[-7] > -0.05

        # --- CLOSE positions ---
        to_close = []
        for sym, pos in list(positions.items()):
            bar = data[sym][i]
            current = bar["c"]
            pnl_pct = (current - pos["entry"]) / pos["entry"]
            bars_held = i - pos["idx"]

            reason = None
            if current <= pos["sl"]:
                reason = "SL"
                exit_price = pos["sl"]
            elif current >= pos["tp"]:
                reason = "TP"
                exit_price = pos["tp"]
            elif bars_held >= MAX_HOLD_BARS:
                reason = "HORIZON"
                exit_price = current

            if reason:
                pnl = (exit_price - pos["entry"]) * pos["qty"]
                cash += exit_price * pos["qty"]
                trades.append({
                    "symbol": sym,
                    "entry": round(pos["entry"], 2),
                    "exit": round(exit_price, 2),
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl_pct * 100, 2),
                    "reason": reason,
                    "bars_held": bars_held,
                    "score": pos.get("score", 0),
                })
                to_close.append(sym)

        for sym in to_close:
            del positions[sym]

        if not btc_ok:
            continue

        # --- SCORE & OPEN positions ---
        # Convert bars to klines format for scorer
        klines_for_scoring = {
            sym: [
                [0, data[sym][j]["o"], data[sym][j]["h"], data[sym][j]["l"], data[sym][j]["c"], data[sym][j]["v"]]
                for j in range(i + 1)
            ]
            for sym in SYMBOLS
        }

        ranked = []
        for sym in SYMBOLS:
            if sym in positions:
                continue
            bars_sym = data[sym][:i+1]
            closes = [b["c"] for b in bars_sym]
            if len(closes) < 50:
                continue

            # Calcul ATR pour SL/TP dynamiques
            atr_val = atr(bars_sym, 14)
            if atr_val is None or atr_val <= 0:
                continue

            # Score via le vrai scorer
            info = score_symbol(sym, klines_for_scoring[sym])
            if info["score"] < MIN_SCORE:
                continue

            price = closes[-1]
            ranked.append((sym, info["score"], price, atr_val))

        ranked.sort(key=lambda x: x[1], reverse=True)

        for sym, score, price, atr_val in ranked:
            if len(positions) >= MAX_POSITIONS:
                break

            # Position sizing: risquer 1% du capital
            risk_usd = cash * RISK_PER_TRADE
            sl_dist = atr_val * SL_ATR_MULT
            tp_dist = atr_val * TP_ATR_MULT

            sl_price = round(price - sl_dist, 2)
            tp_price = round(price + tp_dist, 2)

            if sl_price <= 0 or tp_price <= price:
                continue

            # Quantité pour risquer risk_usd
            qty = risk_usd / (price - sl_price) if price > sl_price else 0
            cost = qty * price

            if cost > cash:
                qty = (cash * 0.95) / price
                cost = qty * price

            qty = round(qty, 6)
            if qty <= 0:
                continue

            cash -= cost
            positions[sym] = {
                "qty": qty,
                "entry": price,
                "idx": i,
                "sl": sl_price,
                "tp": tp_price,
                "score": score,
            }
            trades.append({
                "symbol": sym,
                "side": "BUY",
                "price": round(price, 2),
                "score": score,
                "sl": sl_price,
                "tp": tp_price,
                "rr": round((tp_price - price) / (price - sl_price), 2) if price != sl_price else 0,
            })

        # Equity
        equity = cash + sum(positions[s]["qty"] * data[s][i]["c"] for s in positions)
        equity_curve.append(round(equity, 2))

    # --- REPORT ---
    closed_trades = [t for t in trades if "pnl" in t]
    wins = [t for t in closed_trades if t["pnl"] > 0]
    losses = [t for t in closed_trades if t["pnl"] <= 0]
    win_rate = (len(wins) / max(1, len(closed_trades))) * 100
    total_pnl = sum(t["pnl"] for t in closed_trades)
    total_pnl_pct = (total_pnl / CAPITAL) * 100

    # Max drawdown
    peak = equity_curve[0] if equity_curve else CAPITAL
    dd = 0
    for e in equity_curve:
        if e > peak:
            peak = e
        dd = max(dd, (peak - e) / peak * 100)

    # Profit factor
    gross_profit = sum(t["pnl"] for t in wins) if wins else 0
    gross_loss = abs(sum(t["pnl"] for t in losses)) if losses else 1
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss else 999

    print(f"=== BACKTEST {strategy_name} ===")
    print(f"Symbole(s) : {', '.join(SYMBOLS)}")
    print(f"Capital initial : {CAPITAL:.0f}$ | Risque/trade : {RISK_PER_TRADE*100:.0f}%")
    print(f"Score min : {MIN_SCORE} | Max positions : {MAX_POSITIONS}")
    print(f"SL = {SL_ATR_MULT}x ATR | TP = {TP_ATR_MULT}x ATR")
    print()
    print(f"Bars : {n}")
    print(f"Trades total : {len(trades)}")
    print(f"Trades fermés : {len(closed_trades)}")
    print(f"Wins : {len(wins)} | Losses : {len(losses)}")
    print(f"Win rate : {win_rate:.1f}%")
    print(f"PnL total : {total_pnl:.2f}$ ({total_pnl_pct:.2f}%)")
    print(f"Profit factor : {profit_factor}")
    print(f"Max drawdown : {dd:.1f}%")
    print(f"Equity finale : {round(equity_curve[-1], 2) if equity_curve else CAPITAL}$")
    print(f"Equity max/min : {round(max(equity_curve), 2)} / {round(min(equity_curve), 2)}")
    print()
    print("Derniers trades:")
    for t in (trades[-10:] if len(trades) > 10 else trades):
        print(t)

    # Rapport structuré
    res = {
        "strategy": strategy_name,
        "symbols": SYMBOLS,
        "capital": CAPITAL,
        "risk_per_trade": RISK_PER_TRADE,
        "min_score": MIN_SCORE,
        "sl_atr": SL_ATR_MULT,
        "tp_atr": TP_ATR_MULT,
        "bars": n,
        "total_trades": len(trades),
        "closed_trades": len(closed_trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(win_rate, 1),
        "pnl": round(total_pnl, 2),
        "pnl_pct": round(total_pnl_pct, 2),
        "profit_factor": profit_factor,
        "max_drawdown": round(dd, 1),
        "final_equity": round(equity_curve[-1], 2) if equity_curve else CAPITAL,
        "max_equity": round(max(equity_curve), 2),
        "min_equity": round(min(equity_curve), 2),
    }
    Path(__file__).with_name("backtest_report.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False)
    )
    print("\n✅ report saved")

    return res


if __name__ == "__main__":
    simulate()
