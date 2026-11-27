import os, logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import yfinance as yf
import requests

TOKEN="8548148372:AAGeuEZb-oLezZJua4wzoGMR-SIQBrQXgz8"
ANALYST_CHAT_ID = "8131589581"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_data(symbol):
    try:
        m = {"XAUUSD":"GC=F","XAGUSD":"SI=F","EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X","USDJPY":"USDJPY=X","SPX":"^GSPC","NDX":"^NDX","DJIA":"^DJI","VIX":"^VIX","BTCUSD":"BTC-USD","ETHUSD":"ETH-USD"}
        tk = m.get(symbol.upper(), symbol.upper())
        t = yf.Ticker(tk)
        h = t.history(period="30d", interval="1d")
        if h.empty: return None
        p = float(h['Close'].iloc[-1])
        prev = float(h['Close'].iloc[-2]) if len(h)>1 else p
        chg = ((p-prev)/prev)*100 if prev else 0
        hist = [float(x) for x in h['Close'].tolist()[-20:]]
        return {"symbol":symbol.upper(),"price":round(p,4),"change_pct":round(chg,2),"source":"Yahoo Finance","history":hist}
    except Exception as e:
        logger.error(f"data {symbol}: {e}"); return None

def calc_rsi(prices, period=14):
    if len(prices) < period+1: return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        d = prices[i]-prices[i-1]; gains.append(max(d,0)); losses.append(max(-d,0))
    ag, al = sum(gains[:period])/period, sum(losses[:period])/period
    for i in range(period, len(gains)):
        ag = (ag*(period-1)+gains[i])/period; al = (al*(period-1)+losses[i])/period
    rs = ag/al if al else 100
    return round(100-(100/(1+rs)),2)

def calc_sma(prices, period):
    return round(sum(prices[-period:])/period,4) if len(prices)>=period else None

def analyze(symbol):
    data = get_data(symbol)
    if not data: return {"error":f"Actif {symbol} indisponible. BTC,ETH,XRP,XAUUSD,EURUSD,AAPL,TSLA"}
    hist = data.get("history",[])
    rsi = calc_rsi(hist) if len(hist)>14 else 50
    sma20 = calc_sma(hist,20) if len(hist)>=20 else None
    p, chg = data["price"], data.get("change_pct",0)
    if rsi>70: sig="SURACHAT → BAISSE PROBABLE"
    elif rsi<30: sig="SURVENTE → HAUSSE PROBABLE"
    elif chg>2: sig="ACHAT FORT"
    elif chg>0.5: sig="ACHAT"
    elif chg<-2: sig="VENTE FORTE"
    elif chg<-0.5: sig="VENTE"
    else: sig="NEUTRE"
    support = min(hist[-10:])*0.995 if len(hist)>=10 else p*0.97
    resistance = max(hist[-10:])*1.005 if len(hist)>=10 else p*1.03
    return {"symbol":data["symbol"],"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),"price":p,"change_pct":chg,"rsi":rsi,"sma20":sma20,"support":round(support,4),"resistance":round(resistance,4),"signal":sig,"source":data.get("source","Live")}

def eval_trade(symbol, entry, sl, tp, direction="LONG"):
    if direction.upper()=="LONG": risk=entry-sl; reward=tp-entry
    else: risk=sl-entry; reward=entry-tp
    if risk<=0: return {"error":"SL invalide"}
    rr=reward/risk; risk_amount=10000*0.01; size=risk_amount/risk; max_pos=10000*5/entry; size=min(size,max_pos) if entry>0 else size
    status = "FAVORABLE" if rr>=2 else "RISQUÉ" if rr>=1 else "DÉCONSEILLÉ"
    return {"symbol":symbol.upper(),"direction":direction.upper(),"entry":entry,"stop_loss":sl,"take_profit":tp,"risk":round(risk,4),"reward":round(reward,4),"rr":round(rr,2),"size":round(size,4),"risk_usd":round(risk_amount,2),"profit":round(size*reward,2),"status":status}

async def on_start(update, ctx):
    if str(update.effective_user.id)!=ANALYST_CHAT_ID: await update.message.reply_text("🔒"); return
    kb = [[InlineKeyboardButton("📊 Analyse LIVE",callback_data="m_a")],[InlineKeyboardButton("💰 Trade",callback_data="m_t")],[InlineKeyboardButton("💼 Portfolio",callback_data="m_p")]]
    await update.message.reply_text("📈 *BOT ANALYSTE FINANCIER*\n/analyse SYM | /trade SYM ENTRY SL TP DIR\n/portfolio\nDonnées live: Yahoo Finance", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def on_btn(update, ctx):
    q = update.callback_query
    if str(q.from_user.id)!=ANALYST_CHAT_ID: await q.answer("🔒",show_alert=True); return
    await q.answer()
    if q.data=="m_a": await q.edit_message_text("📊 /analyse BTC\n/analyse ETH\n/analyse XAUUSD\n/analyse EURUSD\n/analyse AAPL")
    elif q.data=="m_t": await q.edit_message_text("💰 /trade BTC 95000 92000 105000 LONG\n/trade XAUUSD 2650 2600 2750 LONG")
    elif q.data=="m_p": await on_portfolio(update, ctx)

async def on_analyse(update, ctx):
    if str(update.effective_user.id)!=ANALYST_CHAT_ID: await update.message.reply_text("🔒"); return
    if not ctx.args: await update.message.reply_text("Usage: /analyse SYM"); return
    await update.message.reply_text(f"⏳ Analyse {ctx.args[0].upper()}...")
    res = analyze(ctx.args[0])
    if "error" in res: await update.message.reply_text(f"❌ {res['error']}"); return
    emoji = "🟢" if "HAUSSE" in res["signal"] else "🔴" if "BAISSE" in res["signal"] else "🟡"
    sma = f"\n📊 SMA(20): {res['sma20']}" if res.get('sma20') else ""
    await update.message.reply_text(f"{emoji} *{res['symbol']}*\n⏰ {res['timestamp']}\n📡 {res.get('source','')}\n💰 {res['price']:,} | 📈 {res['change_pct']:+.2f}%\n📈 RSI: {res['rsi']}{sma}\n📌 Sup: {res['support']} | Rés: {res['resistance']}\n🎯 {res['signal']}", parse_mode="Markdown")

async def on_trade(update, ctx):
    if str(update.effective_user.id)!=ANALYST_CHAT_ID: await update.message.reply_text("🔒"); return
    if len(ctx.args)<5: await update.message.reply_text("Usage: /trade SYM ENTRY SL TP DIR"); return
    sym, entry, sl, tp, direction = ctx.args[0], float(ctx.args[1]), float(ctx.args[2]), float(ctx.args[3]), ctx.args[4] if len(ctx.args)>4 else "LONG"
    res = eval_trade(sym, entry, sl, tp, direction)
    if "error" in res: await update.message.reply_text(f"❌ {res['error']}"); return
    emoji = "✅" if res["status"]=="FAVORABLE" else "⚠️" if res["status"]=="RISQUÉ" else "❌"
    await update.message.reply_text(f"{emoji} *TRADE {res['symbol']} {res['direction']}*\n💰 {res['entry']:,} | 🛑 {res['stop_loss']:,} | 🎯 {res['take_profit']:,}\n⚖️ R/R: {res['rr']}\n💵 Taille: {res['size']:.4f} un.\n💸 Risque: {res['risk_usd']:.2f}$\n📈 Profit: {res['profit']:.2f}$\n📌 {res['status']}", parse_mode="Markdown")

async def on_portfolio(update, ctx):
    if str(update.effective_user.id)!=ANALYST_CHAT_ID: await update.message.reply_text("🔒"); return
    await update.message.reply_text("💼 *PORTFOLIO*\n💰 10,000.00$\n📊 0 positions\n- 1%/trade | 5x | 3-10j", parse_mode="Markdown")

def main():
    logger.info("🚀 Bot Analyste Financier – polling propre")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CommandHandler("help", on_start))
    app.add_handler(CommandHandler("analyse", on_analyse))
    app.add_handler(CommandHandler("trade", on_trade))
    app.add_handler(CommandHandler("portfolio", on_portfolio))
    app.add_handler(CallbackQueryHandler(on_btn))
    logger.info("✅ Handlers enregistrés – démarrage polling")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, close_loop=False)

if __name__ == "__main__":
    main()
