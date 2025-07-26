import os
import re
import math
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Use your new valid token
TOKEN = "6894555381:AAFh19M7lM-GyJv0jomBsl_AfT_t_-jpWM4"

async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        chat_id = update.effective_chat.id
        
        # Log received message
        logger.info(f"Received message: {text}")
        
        # Check if message is a gold signal
        if not re.search(r'(XAUUSD|Gold|GOLD)', text, re.IGNORECASE):
            logger.info("Ignoring non-gold message")
            return
        
        # Parse signal components
        direction = re.search(r'\b(BUY|SELL|buy|sell|Buying|Selling)\b', text, re.IGNORECASE)
        sl_match = re.search(r'SL\s*[:@]?\s*(\d+\.\d+)', text, re.IGNORECASE)
        entry_match = re.search(r'(?:entry|@|entry:)\s*(\d+\.\d+)', text, re.IGNORECASE)
        
        if not direction:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Missing direction (BUY/SELL) in signal"
            )
            return
            
        if not sl_match:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Missing stop loss (SL) in signal"
            )
            return
        
        direction = direction.group(1).upper()
        sl_price = float(sl_match.group(1))
        
        # Try to get entry price from different patterns
        entry_price = None
        if entry_match:
            entry_price = float(entry_match.group(1))
        else:
            # Try alternative patterns
            price_match = re.search(r'@\s*(\d+\.\d+)', text)
            if price_match:
                entry_price = float(price_match.group(1))
        
        # Calculate stop loss distance
        if entry_price:
            stop_loss_distance = abs(entry_price - sl_price)
        else:
            # Handle signals without explicit entry price
            pip_match = re.search(r'\((\d+)\s*PIPS?\)', text, re.IGNORECASE)
            if pip_match:
                stop_loss_distance = float(pip_match.group(1)) * 0.01
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Cannot calculate SL distance. Need entry price or pip value."
                )
                return
        
        # Calculate risk parameters
        RISK_PER_CONTRACT = stop_loss_distance * 10  # $ per contract (MGC = 10 troy ounces)
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
        logger.info(f"Sent response: {response}")
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error processing signal: {str(e)}"
        )

if __name__ == "__main__":
    logger.info("Bot starting...")
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_signal))
        logger.info("Bot is polling...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
