import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Get the bot token from environment variable set in Render
TOKEN = os.environ.get("BOT_TOKEN")

# Set max risk per trade in dollars
MAX_RISK = 600

# Signal detection and response logic
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    if "xauusd" in message or "gold" in message:

        # Extract stop loss from message
        stop_loss_pips = None

        # Try various signal formats
        sl_pip_match = re.search(r'sl[:\s@]*[\d.]+\s*\(?(\d+)\s*pips?\)?', message, re.IGNORECASE)
        if sl_pip_match:
            stop_loss_pips = int(sl_pip_match.group(1))
        else:
            # fallback - detect SL via two price difference logic
            price_match = re.findall(r'(\d{3,4}\.\d{1,3})', message)
            if len(price_match) >= 2:
                try:
                    entry = float(price_match[0])
                    sl = float(price_match[1])
                    stop_loss_pips = int(abs(entry - sl) * 10)  # for MGC (0.10 per tick)
                except:
                    stop_loss_pips = None

        if stop_loss_pips:
            # MGC tick value = $1.00 = 10 pips (1 pip = $0.10)
            pip_value = 0.10
            stop_loss_dollars = stop_loss_pips * pip_value
            num_contracts = int(MAX_RISK / stop_loss_dollars)

            if num_contracts < 1:
                response = f"⚠️ Signal ignored: SL too large to fit risk limit (${MAX_RISK})."
            else:
                response = f"✅ Signal Detected!\n🟡 Gold Trade\nRisk: ${MAX_RISK} max\nSL: {stop_loss_pips} pips\n📦 Contracts: {num_contracts}"

        else:
            response = "⚠️ Couldn't determine stop loss from the signal."

        await update.message.reply_text(response)

# Main entry
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Catch all messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
