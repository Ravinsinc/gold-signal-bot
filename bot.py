import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load token from environment
TOKEN = os.environ.get("BOT_TOKEN")
MAX_RISK = 600  # dollars per trade

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    if "xauusd" in message or "gold" in message:
        stop_loss_pips = None

        # Format 1: SL: 3373.98(100PIPS)
        sl_pip_match = re.search(r'sl[:\s@]*[\d.]+\s*\(?(\d+)\s*pips?\)?', message, re.IGNORECASE)
        if sl_pip_match:
            stop_loss_pips = int(sl_pip_match.group(1))
        else:
            # Format 2: Entry + SL values
            prices = re.findall(r'(\d{3,4}\.\d{1,4})', message)
            if len(prices) >= 2:
                try:
                    entry = float(prices[0])
                    sl = float(prices[1])
                    stop_loss_pips = int(abs(entry - sl) * 10)
                except:
                    stop_loss_pips = None

        if stop_loss_pips:
            pip_value = 0.10  # $0.10 per pip for MGC
            stop_loss_dollars = stop_loss_pips * pip_value
            num_contracts = int(MAX_RISK / stop_loss_dollars)

            if num_contracts < 1:
                response = f"⚠️ SL too large to risk ${MAX_RISK}"
            else:
                response = f"✅ Gold Signal\nRisk: ${MAX_RISK}\nSL: {stop_loss_pips} pips\nContracts: {num_contracts}"
        else:
            response = "⚠️ Could not detect stop loss in the signal."

        await update.message.reply_text(response)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

