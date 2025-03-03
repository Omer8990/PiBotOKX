import os
import logging
import json
import time
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
TRADE_COOLDOWN = 300  # 5 minutes
RETRY_DELAY = 120  # 2 minutes retry delay

# Trading statistics
total_trades = 0
winning_trades = 0
losing_trades = 0
total_profit_loss = 0

last_trade_time = None
in_position = False
entry_price = 0

# ✅ Jarvis-style messages
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

async def is_market_oversold():
    """Check if the market is oversold using RSI before buying"""
    try:
        candles = exchange.fetch_ohlcv(SYMBOL, '5m', limit=14)
        closes = [candle[4] for candle in candles]

        gains = sum(max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes)))
        losses = sum(max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes)))

        rs = (gains / 14) / (losses / 14) if losses > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        return rsi < 30  # Buy only if RSI is below 30 (oversold)

    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return False

async def calculate_atr():
    """Calculate Average True Range (ATR) for dynamic stop-loss"""
    try:
        candles = exchange.fetch_ohlcv(SYMBOL, '5m', limit=14)
        tr_values = [max(candle[2] - candle[3], abs(candle[2] - candle[4]), abs(candle[3] - candle[4])) for candle in candles]
        return sum(tr_values) / len(tr_values)

    except Exception as e:
        logger.error(f"Error calculating ATR: {e}")
        return STOP_LOSS

async def is_market_trending_up():
    """Check if the market is in an uptrend using moving averages"""
    try:
        candles = exchange.fetch_ohlcv(SYMBOL, '5m', limit=50)
        closes = [candle[4] for candle in candles]

        sma_10 = sum(closes[-10:]) / 10
        sma_50 = sum(closes[-50:]) / 50

        return sma_10 > sma_50  # Buy only if SMA-10 is above SMA-50

    except Exception as e:
        logger.error(f"Error calculating trend: {e}")
        return False

async def trading_loop():
    """Main trading loop"""
    await send_telegram_message(random.choice(JARVIS_GREETINGS))

    while True:
        try:
            market_data = await get_market_data()
            if not market_data:
                await asyncio.sleep(RETRY_DELAY)
                continue

            current_price = market_data['price']

            if in_position:
                profit_percentage = (current_price - entry_price) / entry_price
                if profit_percentage >= PROFIT_THRESHOLD:
                    await send_telegram_message(random.choice(JARVIS_SELL_MESSAGES))
                elif profit_percentage <= -await calculate_atr():
                    await send_telegram_message(random.choice(JARVIS_STOP_LOSS_MESSAGES))

            elif await is_market_oversold() and await is_market_trending_up():
                if last_trade_time and (datetime.now() - last_trade_time).seconds < TRADE_COOLDOWN:
                    await send_telegram_message("Trade cooldown active. Waiting for next opportunity.")
                else:
                    await send_telegram_message(random.choice(JARVIS_BUY_MESSAGES))

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            await send_telegram_message(f"{random.choice(JARVIS_ERROR_MESSAGES)}\nRestarting system in {RETRY_DELAY} seconds.")
            await asyncio.sleep(RETRY_DELAY)

async def main():
    """Initialize trading bot and Telegram commands"""
    logging.info("Trading bot activated!")
    await asyncio.gather(trading_loop())

if __name__ == "__main__":
    asyncio.run(main())
