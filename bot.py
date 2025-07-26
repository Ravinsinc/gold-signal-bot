import os
import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

MAX_RISK = 600
POINT_VALUE = 10  # Micro Gold futures: $10 per point (or $1 per 0.1 pip)

# Pattern examples for gold trade signals
SIGNAL_PATTERNS = [
    r"(?i)(buy|sell)(?:ing)?\s+gold|xauusd.*?(sl|stop\s*loss)[^\d]*([\d.]+)",
    r"(?i)(buy|sell).*?xauusd.*?sl[^\d]*([\d.]+).*?([\d.]+)"
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.lower()
    if "xauusd" not in message_text and "gold" not in message_text:
        return  # Not a gold signal

    # Try to extract direction and SL from known patterns
    direction = "buy" if "buy" in message_text else "sell" if "sell" in message_text else None
    if not direction:
        return

    sl_match = re.search(r"sl\s*[:@\-\s]*([\d.]+)[^\d]*\(?([\d]*)\s*pips?\)?", message_text)
    if sl_match:
        try:
            sl_price = float(sl_match.group(1))
            pip_value = float(sl_match.group(2)) if sl_match.group(2) else 0
        except:
            return
    else:
        return

    # Risk logic
    if pip_value > 0:
        contract_size = MAX_RISK / (pip_value * 1)
    else:
        return

    contract_size = round(contract_size)

    response = (
        f"Signal detected: {direction.upper()} GOLD\n"
        f"Stop Loss: {sl_price} ({pip_value} pips)\n"
        f"Trade up to: {contract_size} micro lots to risk max ${MAX_RISK}."
    )
    await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling()
