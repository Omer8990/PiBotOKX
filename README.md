# JARVIS PI Trading Bot: Setup and Usage Guide - Currently supports only MEXC and OKX

## Overview

The JARVIS PI Trading Bot is an automated trading system designed to trade the PI/USDT pair on the OKX cryptocurrency exchange. This bot features:

- Automated technical analysis and trading decisions
- Profit targets and stop-loss mechanisms
- Telegram integration for notifications and manual control
- JARVIS-themed persona for notifications

## Requirements

- Python 3.8 or higher
- OKX exchange account
- Telegram account
- Basic understanding of cryptocurrency trading

## Installation

1. Clone or download the bot code to your server or local machine
2. Install required dependencies:

```
pip install python-telegram-bot ccxt python-dotenv asyncio
```

3. Create a `.env` file in the same directory as the script

## Configuration

### Setting Up Your .env File

Create a file named `.env` in the project directory with the following variables:

```
Values for OKX accounts:
---------------------
# OKX API Credentials
OKX_API_KEY=your_okx_api_key
OKX_SECRET=your_okx_secret
OKX_PASSWORD=your_okx_api_password

# Telegram Configuration
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
---------------------
Values for MEXC Accounts:
---------------------

TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET=your_mexc_secret_key
---------------------------


```

### Getting OKX API Credentials

1. Log in to your OKX account
2. Navigate to "Account" > "API Management"
3. Click "Create API Key"
4. Set permissions to:
   - "Read" (required)
   - "Trade" (required)
   - "Withdraw" (not recommended unless you need this functionality)
5. Complete verification and save your:
   - API Key
   - Secret Key
   - API Password (Passphrase)

**IMPORTANT**: Store these credentials securely. Anyone with access to these credentials can control your OKX account.

### Creating a Telegram Bot

1. Open Telegram and search for "@BotFather"
2. Start a chat with BotFather
3. Send the command: `/newbot`
4. Follow instructions to name your bot
5. Once created, BotFather will provide a token like: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
6. Copy this token to the `TELEGRAM_TOKEN` field in your `.env` file

### Finding Your Telegram Chat ID

1. Search for "@userinfobot" on Telegram
2. Start a chat with this bot
3. Send any message to the bot
4. The bot will reply with your information, including your Chat ID
5. Copy the Chat ID to the `TELEGRAM_CHAT_ID` field in your `.env` file

## Adjusting Trading Parameters

The bot comes with default trading parameters that can be modified in the code:

```python
# Default Trading parameters (high risk settings)
SYMBOL = 'PI/USDT'
BASE_ORDER_SIZE = 0.85  # Use 85% of available USDT for each trade
PROFIT_THRESHOLD = 0.03  # 3% profit target
STOP_LOSS = 0.05  # 5% stop loss
VOLATILITY_THRESHOLD = 0.02  # 2% price movement to trigger analysis
CHECK_INTERVAL = 60  # Check market every 60 seconds
TRADE_COOLDOWN = 300  # 5 minutes cooldown between trades
```

### Risk Management Guidelines

- **BASE_ORDER_SIZE**: Controls what percentage of your available USDT is used per trade
  - Low risk: 0.1-0.3 (10-30% of balance)
  - Medium risk: 0.4-0.6 (40-60% of balance)
  - High risk: 0.7-0.9 (70-90% of balance)

- **PROFIT_THRESHOLD**: Sets the target profit percentage to trigger a sell
  - Conservative: 0.01-0.02 (1-2%)
  - Moderate: 0.03-0.05 (3-5%)
  - Aggressive: 0.06+ (6%+)

- **STOP_LOSS**: Sets the maximum loss percentage before cutting losses
  - Tight: 0.02-0.03 (2-3%)
  - Standard: 0.04-0.06 (4-6%)
  - Wide: 0.07-0.1 (7-10%)

- **VOLATILITY_THRESHOLD**: Minimum price movement to trigger analysis
  - Lower values (e.g., 0.01) will make the bot more active
  - Higher values (e.g., 0.03) will make the bot more selective

- **CHECK_INTERVAL**: How frequently the bot checks market conditions (in seconds)
  - More frequent: 30-60 seconds
  - Less frequent: 120-300 seconds

- **TRADE_COOLDOWN**: Minimum time between trades (in seconds)
  - Short cooldown: 60-180 seconds (more trades)
  - Long cooldown: 300-1800 seconds (fewer trades)

## Adjusting Parameters via Telegram

You can also adjust the main trading parameters while the bot is running using the Telegram command:

```
/set_params [order_size] [profit] [stop_loss]
```

Example:
```
/set_params 0.5 0.02 0.04
```
This sets:
- 50% of USDT balance per trade
- 2% profit target
- 4% stop loss

## Running the Bot

1. Make sure all configurations are set in the `.env` file
2. Run the bot:

```
python pi_trading_bot.py
```

3. The bot will start and send an initialization message to your Telegram

## Telegram Commands

The following commands can be used to control the bot via Telegram:

- `/start` - Initialize the bot
- `/status` - Get current trading status, price, and balance information
- `/buy` - Manually execute a buy order
- `/sell` - Manually execute a sell order
- `/set_params [order_size] [profit] [stop_loss]` - Adjust trading parameters

## Understanding Bot Behavior

### Analysis Method

The bot uses a combination of technical indicators to make trading decisions:
- Short and long moving averages
- RSI (Relative Strength Index)
- Volatility analysis
- Recent price performance
- Random factor (20% chance of buying regardless of indicators)

These factors combine to create a "risk score" that determines buy signals.

### Trading Logic

1. The bot checks if it's already in a position
   - If yes, it monitors for profit target or stop loss
   - If no, it analyzes market conditions for potential entry

2. Entry conditions require:
   - No active cooldown period
   - Sufficient risk score from technical analysis
   - Adequate USDT balance

3. Exit conditions are triggered when:
   - Profit target is reached
   - Stop loss is triggered
   - Manual sell command is issued

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API credentials are correct
   - Check internet connection
   - Ensure OKX services are online

2. **Insufficient Funds Errors**
   - Ensure enough USDT is available in your OKX account
   - Check if BASE_ORDER_SIZE is too high

3. **Bot Not Responding to Commands**
   - Verify TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are correct
   - Restart the bot
   - Check if bot process is still running

### Error Messages

The bot logs errors and sends notifications via Telegram. Common error messages include:
- "Error fetching market data" - Issues connecting to OKX API
- "Error in market analysis" - Problems with calculation of indicators
- "Error placing buy/sell order" - Issues executing trades

## Important Warnings

1. **This is high-risk trading software.** The bot is designed to take significant risks with your capital, which may result in substantial losses.

2. **Never invest more than you can afford to lose.** Cryptocurrency trading is highly volatile.

3. **Keep your API keys secure.** Never share your .env file or API credentials.

4. **Monitor the bot regularly.** While automated, the bot should not run completely unsupervised for extended periods.

5. **Use a dedicated account.** Consider using a separate OKX account with limited funds for bot trading.

## Maintenance and Updates

- Regularly check for updates to the bot code
- Monitor your OKX API key expiration dates
- Review trading performance and adjust parameters as needed

## Legal Disclaimer

This trading bot is provided for educational and entertainment purposes only. Use at your own risk. The creator is not responsible for any financial losses incurred through the use of this software.

## Support

For questions, issues, or feature requests, please contact the developer directly. Do not share your API credentials or .env file when seeking support.