import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import re, math

TOKEN = os.getenv("BOT_TOKEN")
MAX_RISK = 600
MGC_PIP_VALUE = 1

def extract_pips_or_prices(text):
    pips_match = re.search(r'\((\d+)\s*pips?\)', text, re.IGNORECASE)
    if pips_match:
        return int(pips_match.group(1))
    price_match = re.search(r'(?:sl|stop loss)[^\d]*(\d{3,5}\.\d+)', text, re.IGNORECASE)
    entry_match = re.search(r'(?:entry|now\s*@?|market entry)[^\d]*(\d{3,5}\.\d+)', text, re.IGNORECASE)
    if price_match and entry_match:
        sl_price = float(price_match.group(1))
        entry_price = float(entry_match.group(2))
        pip_diff = abs(sl_price - entry_price) * 10
        return round(pip_diff)
    return None

def is_gold_signal(text):
    return any(k in text.lower() for k in ["xauusd", "gold"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if not is_gold_signal(text):
        return
    sl_pips = extract_pips_or_prices(text)
    if not sl_pips:
        await update.message.reply_text("⚠️ Could not determine SL in pips.")
        return
    contracts = math.floor(MAX_RISK / (sl_pips * MGC_PIP_VALUE))
    contracts = max(1, contracts)
    resp = (
        f"📩 *Gold Signal Detected*\n"
        f"SL: `{sl_pips}` pips\n"
        f"Max Risk: `${MAX_RISK}`\n"
        f"✅ Use: *{contracts} MGC contracts*"
    )
    await update.message.reply_text(resp, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
