import os
import logging
import json
from datetime import datetime
import asyncio
import ccxt
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# OKX API domains
domain_myokx = 'https://my.okx.com'
domain_www = 'https://www.okx.com'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OKX exchange using myokx
exchange = ccxt.myokx({
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET'),
    'password': os.getenv('OKX_PASSWORD'),
    'enableRateLimit': True,
})

# Telegram configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Trading parameters
SYMBOL = 'PI-USD'
BASE_ORDER_SIZE = 0.85
PROFIT_THRESHOLD = 0.03
STOP_LOSS = 0.035

# Trading statistics
total_trades = 0
winning_trades = 0
losing_trades = 0
total_profit_loss = 0

last_trade_time = None
in_position = False
entry_price = 0


JARVIS_GREETINGS = [
    "Good day, sir. JARVIS is online and monitoring the PI market.",
    "Systems operational. Scanning PI market conditions now.",
    "JARVIS at your service. Market analysis engaged.",
    "Booting up trading protocols. Let's make some profits, sir."
]

JARVIS_STATUS_MESSAGES = {
    "positive": [
        "Sir, the portfolio is in excellent shape. Profits are accumulating.",
        "All systems are green, sir. The market is working in our favor.",
        "Your trading strategy is performing admirably. Gains are being secured.",
        "Impressive results, sir. Our profit trajectory remains strong."
    ],
    "neutral": [
        "Market conditions are stable. No significant shifts detected.",
        "Nothing extraordinary to report, sir. We are maintaining course.",
        "Your portfolio is in a balanced state. No immediate concerns.",
        "Data suggests a steady market. Monitoring for new opportunities."
    ],
    "negative": [
        "Sir, losses have been detected. Adjustments may be required.",
        "Market conditions have not been favorable. A recalibration might be necessary.",
        "Red flags detected in our strategy. We might need to rethink our approach.",
        "Performance is suboptimal, sir. I suggest a reassessment of our parameters."
    ]
}

async def send_telegram_message(message):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

async def get_market_data():
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        return {'price': ticker['last']}
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        await send_telegram_message("Sir, an unexpected anomaly has occurred while fetching market data.")
        return None

async def get_available_balance():
    try:
        balance = exchange.fetch_balance()
        return balance['USD']['free']
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        await send_telegram_message("Sir, I regret to inform you that balance retrieval has failed.")
        return 0

async def status_command(update, context):
    market_data = await get_market_data()
    balance = await get_available_balance()

    global total_trades, winning_trades, losing_trades, total_profit_loss
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    avg_profit_loss = (total_profit_loss / total_trades) if total_trades > 0 else 0

    # Determine Jarvis' status response
    if total_profit_loss > 50:
        status_message = random.choice(JARVIS_STATUS_MESSAGES["positive"])
    elif total_profit_loss < -50:
        status_message = random.choice(JARVIS_STATUS_MESSAGES["negative"])
    else:
        status_message = random.choice(JARVIS_STATUS_MESSAGES["neutral"])

    status_report = f"📊 **Status Report - {datetime.now().strftime('%H:%M:%S')}**\n"
    status_report += f"{status_message}\n\n"
    status_report += f"🔹 **PI Price:** ${market_data['price']:.4f}\n"
    status_report += f"🔹 **USD Balance:** ${balance:.2f}\n"
    status_report += f"🔹 **Total Trades:** {total_trades}\n"
    status_report += f"🔹 **Winning Trades:** {winning_trades}\n"
    status_report += f"🔹 **Losing Trades:** {losing_trades}\n"
    status_report += f"🔹 **Win Rate:** {win_rate:.2f}%\n"
    status_report += f"🔹 **Total Profit/Loss:** ${total_profit_loss:.2f}\n"
    status_report += f"🔹 **Avg Profit/Loss per Trade:** ${avg_profit_loss:.2f}\n"

    await update.message.reply_text(status_report)

async def setup_telegram_commands():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def main():
    logging.info("Trading bot activated!")
    await setup_telegram_commands()

if __name__ == "__main__":
    asyncio.run(main())
