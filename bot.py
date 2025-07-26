import os
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")  # Read token from environment

MAX_RISK = 600  # Max USD risk per trade

# Signal Parsing Function
def parse_signal(message: str):
    pattern = r"(buy|sell)[^\d]*(\d{4,}\.\d{1,})[^\d]+sl[^\d]*(\d{4,}\.\d{1,})"
    match = re.search(pattern, message, re.IGNORECASE)
    if match:
        direction = match.group(1).upper()
        entry_price = float(match.group(2))
        sl_price = float(match.group(3))
        return direction, entry_price, sl_price
    return None

# Risk Calculator
def calculate_lot_size(entry, sl, max_risk=MAX_RISK):
    stop_loss_ticks = abs(entry - sl) / 0.1  # MGC = $1 per 0.1 move
    if stop_loss_ticks == 0:
        return 0
    contracts = int(max_risk / stop_loss_ticks)
    return contracts

# Message Handler
async def signal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message = update.message.text.lower()

    if "xauusd" not in message and "gold" not in message:
        return

    result = parse_signal(message)
    if result:
        direction, entry, sl = result
        contracts = calculate_lot_size(entry, sl)
        response = (
            f"📢 Signal Detected: {direction}\n"
            f"🎯 Entry: {entry}\n"
            f"🛑 SL: {sl}\n"
            f"📏 Contracts: {contracts} (max $600 risk)"
        )
        await update.message.reply_text(response)

# Main App
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, signal_handler))
    app.run_polling()
