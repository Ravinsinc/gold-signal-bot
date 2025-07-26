import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

# Your max risk per trade
MAX_RISK = 600  # dollars
TICK_VALUE = 1.0  # $1 per tick for MGC
TICKS_PER_PIP = 10  # 10 ticks per pip

# Signal pattern examples:
SIGNAL_PATTERNS = [
    r"(buy|sell)\s+(xauusd|gold).*(sl\s*[:@]?\s*([\d.]+))",  # e.g. buy xauusd now sl: 1933.5
    r"(buy|sell).*gold.*entry\s*[@]?\s*([\d.]+).*sl\s*([@\s]*([\d.]+))",  # Selling Gold @ 3324.8 Sl 3326.8
]

async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()

    for pattern in SIGNAL_PATTERNS:
        match = re.search(pattern, message)
        if match:
            direction = match.group(1).upper()
            try:
                stop_loss_price = float(match.group(4))
            except (IndexError, ValueError):
                continue

            stop_loss_pips = abs(float(stop_loss_price))  # you may adapt based on Entry/SL
            stop_loss_ticks = stop_loss_pips * TICKS_PER_PIP
            risk_per_contract = stop_loss_ticks * TICK_VALUE

            contracts = int(MAX_RISK / risk_per_contract)

            reply = f"📡 {direction} Signal Detected\n"
            reply += f"🔻 Stop Loss: {stop_loss_price} ({stop_loss_pips} pips)\n"
            reply += f"🧮 Contracts to Risk $600: {contracts}"

            await update.message.reply_text(reply)
            return

    await update.message.reply_text("❌ Could not parse signal.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_signal))
    print("Bot is running...")
    app.run_polling()
