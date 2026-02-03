import hmac
import hashlib
import time
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from config import Config

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """Client for interacting with Binance Futures Testnet API"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = Config.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for request"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _send_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                      signed: bool = False) -> Dict[str, Any]:
        """Send HTTP request to Binance API"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            logger.info(f"Sending {method} request to {endpoint} with params: {params}")
            
            if method == 'GET':
                # response = self.session.get(url, params=params, timeout=10)
                response = self.session.get(url, data=params, timeout=10)
            elif method == 'POST':
                # response = self.session.post(url, params=params, timeout=10)
                response = self.session.post(url, data=params, timeout=10)
                # Add after getting response:
                if response.history:  # Check for redirects
                    raise Exception(f"Request redirected! Wrong URL or endpoint. Final URL: {response.url}")
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Response received: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            raise Exception(f"Network error: {str(e)}")
        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")
            raise Exception(f"Invalid response from server: {str(e)}")
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                    quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place a new order on Binance Futures
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Required for LIMIT orders
        
        Returns:
            Order response from Binance API
        """
        # Validate inputs
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be either 'BUY' or 'SELL'")
        
        if order_type not in ['MARKET', 'LIMIT']:
            raise ValueError("Order type must be either 'MARKET' or 'LIMIT'")
        
        if order_type == 'LIMIT' and price is None:
            raise ValueError("Price is required for LIMIT orders")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        # Prepare order parameters
        params = {
            'symbol': symbol.upper(),
            'side': side,
            'type': order_type,
            'quantity': round(quantity, 8),  # Binance precision
            'newOrderRespType': 'ACK'  # Get full response
        }
        
        if order_type == 'LIMIT':
            params['timeInForce'] = 'GTC'  # Good Till Cancel
            params['price'] = round(price, 2)  # Adjust precision as needed
        
        logger.info(f"Placing order: {params}")
        
        try:
            # response = self._send_request('POST', '/fapi/v1/order', params, signed=True)
            print(params)
            print("these are the parameters")
            response = self._send_request('POST', '/api/v3/order', params, signed=True)
            return response
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get current account information"""
        # return self._send_request('GET', '/fapi/v2/account', signed=True)
        return self._send_request('GET', '/api/v3/account', signed=True)
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # response = self._send_request('POST', '/api/v3/order', params, signed=True)
            response = self._send_request('GET', '/api/v3/ping')
            return True
        except:
            return False