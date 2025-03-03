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

# Jarvis-style messages
JARVIS_GREETINGS = [
    "Good day, sir. JARVIS is online and monitoring the PI market.",
    "Systems operational. Scanning PI market conditions now.",
    "JARVIS at your service. Market analysis engaged.",
    "Booting up trading protocols. Let's make some profits, sir."
]

JARVIS_BUY_MESSAGES = [
    "Sir, the market presents an opportunity. Executing buy protocol.",
    "A favorable entry point detected. Acquiring PI now.",
    "The risk-reward ratio looks excellent. Initiating purchase.",
    "Deploying capital into PI. The probabilities are in our favor."
]

JARVIS_SELL_MESSAGES = [
    "Sir, profit target achieved. Selling PI now.",
    "We have reached the optimal exit point. Executing sell order.",
    "The PI rocket has reached orbit. Time to eject, sir.",
    "Profit secured. Shall I prepare a celebratory beverage?"
]

JARVIS_STOP_LOSS_MESSAGES = [
    "Stop-loss activated. Exiting position to prevent further losses.",
    "The trade did not go as expected, sir. Cutting our losses.",
    "Sometimes, strategic retreats are necessary. Selling now.",
    "Initiating damage control. Position liquidated."
]

JARVIS_ERROR_MESSAGES = [
    "Sir, an unexpected anomaly has occurred. Investigating now.",
    "System error detected. Executing recovery protocols.",
    "I regret to inform you, sir, that we have a problem.",
    "Something is off. Running diagnostics."
]

async def send_telegram_message(message):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

async def get_market_data():
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        return {'price': ticker['last']}
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        await send_telegram_message(f"{random.choice(JARVIS_ERROR_MESSAGES)}\nError: {e}")
        return None

async def get_available_balance():
    try:
        balance = exchange.fetch_balance()
        return balance['USD']['free']
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        await send_telegram_message(f"{random.choice(JARVIS_ERROR_MESSAGES)}\nError retrieving balance: {e}")
        return 0

async def buy_pi(current_price):
    global in_position, entry_price, last_trade_time

    try:
        usd_balance = await get_available_balance()
        order_size_usd = usd_balance * BASE_ORDER_SIZE
        if order_size_usd < 10:
            await send_telegram_message("Insufficient USD to execute trade, sir.")
            return False

        amount = order_size_usd / current_price
        exchange.create_market_buy_order(SYMBOL, amount)

        in_position = True
        entry_price = current_price
        last_trade_time = datetime.now()

        await send_telegram_message(f"{random.choice(JARVIS_BUY_MESSAGES)}\nBought {amount:.4f} PI @ ${current_price:.4f}")
        return True

    except Exception as e:
        logger.error(f"Error placing buy order: {e}")
        await send_telegram_message(f"{random.choice(JARVIS_ERROR_MESSAGES)}\nBuy order failed: {e}")
        return False

async def sell_pi(current_price, reason="profit"):
    global in_position, entry_price, last_trade_time, total_trades, winning_trades, losing_trades, total_profit_loss

    try:
        balance = exchange.fetch_balance()
        pi_amount = balance['PI']['free']
        if pi_amount * current_price < 10:
            await send_telegram_message("Position too small to sell, sir.")
            return False

        exchange.create_market_sell_order(SYMBOL, pi_amount)

        entry_value = pi_amount * entry_price
        exit_value = pi_amount * current_price
        profit_loss = exit_value - entry_value

        total_trades += 1
        total_profit_loss += profit_loss
        if profit_loss > 0:
            winning_trades += 1
            message = random.choice(JARVIS_SELL_MESSAGES)
        else:
            losing_trades += 1
            message = random.choice(JARVIS_STOP_LOSS_MESSAGES)

        await send_telegram_message(f"{message}\nSold {pi_amount:.4f} PI @ ${current_price:.4f}\nProfit/Loss: ${profit_loss:.2f}")
        in_position = False
        last_trade_time = datetime.now()
        return True

    except Exception as e:
        logger.error(f"Error placing sell order: {e}")
        await send_telegram_message(f"{random.choice(JARVIS_ERROR_MESSAGES)}\nSell order failed: {e}")
        return False

async def trading_loop():
    """Main trading loop"""
    await send_telegram_message(random.choice(JARVIS_GREETINGS))

    while True:
        try:
            current_data = await get_market_data()
            if not current_data:
                await asyncio.sleep(60)
                continue

            current_price = current_data['price']

            # Check if we need to exit position
            if in_position:
                profit_percentage = (current_price - entry_price) / entry_price

                if profit_percentage >= PROFIT_THRESHOLD:
                    await sell_pi(current_price, "profit")
                elif profit_percentage <= -STOP_LOSS:
                    await sell_pi(current_price, "stop_loss")

            else:
                await buy_pi(current_price)

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            await send_telegram_message(f"{random.choice(JARVIS_ERROR_MESSAGES)}\nTrading systems rebooting.")
            await asyncio.sleep(120)

async def setup_telegram_commands():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def main():
    logging.info("Trading bot activated!")
    await asyncio.gather(setup_telegram_commands(), trading_loop())

if __name__ == "__main__":
    asyncio.run(main())
