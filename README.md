# Binance Testnet Trading CLI

A Python command-line application for placing orders on Binance Testnet with proper error handling and logging.

## 🚀 Quick Start

### 1. Get Testnet API Keys
# Go to the testnet website:
https://testnet.binance.vision
# Register/Login → API Management → Create New API Key

2. Configure API Keys
Edit config.py or set environment variables:
# In config.py
API_KEY = "your_testnet_api_key_here"
SECRET_KEY = "your_testnet_secret_key_here"

Or create a .env file:
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

3. Install Dependencies
pip install -r requirements.txt

4.run the application

direct CLI mode
# Market Order
python cli_handler.py BTCUSDT BUY MARKET 0.001

# Limit Order
python cli_handler.py BTCUSDT SELL LIMIT 0.001 --price 50000

interactive mode
python cli_handler.py interactive

project structure
binance_trading/
├── binance_client.py    # API client with connection logic
├── cli_handler.py       # Command-line interface
├── config.py            # Configuration (API keys, URLs)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (optional)
└── README.md            # This file

base url

BASE_URL = "https://testnet.binance.vision"


Endpoints:
/api/v3/ping - Test connection (Spot API)

/api/v3/order - Place orders (Spot API)


Features
✅ Market and Limit orders
✅ BUY and SELL sides
✅ Input validation
✅ Error handling
✅ Logging to file (binance_trading.log)
✅ Clean CLI interface
✅ Structured code architecture

📝 Logs
All API requests and responses are logged to:

Console output

binance_trading.log file

binance_debug_*.log for detailed debugging
