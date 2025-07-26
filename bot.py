import os
import re
import math
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or "8480482125:AAHFUkEpa-msTfCGZx2eaeaNjfVvGUPPWWc"

async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    
    # Check if message is a gold signal
    if not re.search(r'(XAUUSD|Gold|GOLD)', text, re.IGNORECASE):
        return
    
    # Parse signal components
    direction = re.search(r'\b(BUY|SELL|buy|sell|Buying|Selling)\b', text, re.IGNORECASE)
    sl_match = re.search(r'SL\s*[:@]?\s*(\d+\.\d+)', text, re.IGNORECASE)
    entry_match = re.search(r'(?:entry|@)\s*(\d+\.\d+)', text, re.IGNORECASE)
    
    if not all([direction, sl_match]):
        return
    
    direction = direction.group(1).upper()
    sl_price = float(sl_match.group(1))
    entry_price = float(entry_match.group(1)) if entry_match else None
    
    # Calculate stop loss distance
    if entry_price:
        stop_loss_distance = abs(entry_price - sl_price)
    else:
        # Handle signals without explicit entry price
        pip_match = re.search(r'\((\d+)PIPS?\)', text)
        if pip_match:
            stop_loss_distance = float(pip_match.group(1)) * 0.01
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Cannot calculate SL distance. Need entry price or pip value."
            )
            return
    
    # Calculate risk parameters
    RISK_PER_CONTRACT = stop_loss_distance * 10  # $ per contract
    MAX_RISK = 600  # $ per trade
    
    if RISK_PER_CONTRACT <= 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Invalid risk calculation: Stop loss distance must be positive"
        )
        return
    
    contracts = min(math.floor(MAX_RISK / RISK_PER_CONTRACT), 600)
    actual_risk = contracts * RISK_PER_CONTRACT
    
    # Prepare response
    response = (
        f"📊 *Trade Calculated* 📊\n"
        f"• Direction: {direction}\n"
        f"• Entry: {entry_price or 'MARKET'}\n"
        f"• SL: {sl_price} ({stop_loss_distance:.2f} $/oz)\n"
        f"• Risk/Contract: ${RISK_PER_CONTRACT:.2f}\n"
        f"• Max Contracts: {contracts}\n"
        f"• Actual Risk: ${actual_risk:.2f}/${MAX_RISK}\n\n"
        f"_Trading MGC Futures | ${stop_loss_distance*10:.2f} risk per contract_"
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=response,
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    print("Bot started...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_signal))
    app.run_polling()
