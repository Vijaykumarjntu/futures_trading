import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # BASE_URL = "https://testnet.binancefuture.com"
    BASE_URL = "https://testnet.binance.vision"
    # BASE_URL = "https://demo.binance.com/en/futures/BTCUSDT"
    API_KEY = os.getenv("BINANCE_API_KEY", "your_testnet_api_key")
    SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "your_testnet_secret_key")
    
    @staticmethod
    def validate_config():
        if Config.API_KEY == "your_testnet_api_key" or Config.SECRET_KEY == "your_testnet_secret_key":
            raise ValueError("Please set your API credentials in .env file or config.py")