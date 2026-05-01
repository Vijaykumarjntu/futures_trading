import pytest
import json
from unittest.mock import Mock, patch
from binance_client import BinanceFuturesClient

class TestBinanceClient:
    
    def test_client_initialization(self):
        """Test client initializes with valid credentials"""
        client = BinanceFuturesClient("test_key", "test_secret")
        assert client.api_key == "test_key"
        assert client.secret_key == "test_secret"
    
    def test_generate_signature(self):
        """Test signature generation is consistent"""
        client = BinanceFuturesClient("key", "secret")
        params = {'symbol': 'BTCUSDT', 'timestamp': 123456}
        
        signature = client._generate_signature(params)
        # HMAC SHA256 produces 64 character hex string
        assert len(signature) == 64
        assert isinstance(signature, str)
    
    @patch('binance_client.requests.post')
    def test_place_market_order_success(self, mock_post):
        """Test successful market order placement"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'orderId': '12345',
            'symbol': 'BTCUSDT',
            'status': 'FILLED',
            'executedQty': '0.001'
        }
        mock_post.return_value = mock_response
        
        client = BinanceFuturesClient("key", "secret")
        result = client.place_order('BTCUSDT', 'BUY', 'MARKET', 0.001)
        
        assert result['orderId'] == '12345'
        assert result['status'] == 'FILLED'
        mock_post.assert_called_once()
    
    @patch('binance_client.requests.post')
    def test_place_limit_order_success(self, mock_post):
        """Test successful limit order placement"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'orderId': '67890',
            'symbol': 'ETHUSDT',
            'price': '2500.00'
        }
        mock_post.return_value = mock_response
        
        client = BinanceFuturesClient("key", "secret")
        result = client.place_order('ETHUSDT', 'SELL', 'LIMIT', 0.1, price=2500)
        
        assert result['orderId'] == '67890'
        assert result['price'] == '2500.00'
    
    def test_place_order_invalid_side(self):
        """Test validation for invalid side"""
        client = BinanceFuturesClient("key", "secret")
        
        with pytest.raises(ValueError, match="Side must be either 'BUY' or 'SELL'"):
            client.place_order('BTCUSDT', 'INVALID', 'MARKET', 0.001)
    
    def test_place_order_invalid_type(self):
        """Test validation for invalid order type"""
        client = BinanceFuturesClient("key", "secret")
        
        with pytest.raises(ValueError, match="Order type must be either 'MARKET' or 'LIMIT'"):
            client.place_order('BTCUSDT', 'BUY', 'INVALID', 0.001)
    
    def test_place_order_missing_price_for_limit(self):
        """Test limit order requires price"""
        client = BinanceFuturesClient("key", "secret")
        
        with pytest.raises(ValueError, match="Price is required for LIMIT orders"):
            client.place_order('BTCUSDT', 'BUY', 'LIMIT', 0.001)
    
    def test_place_order_negative_quantity(self):
        """Test validation for negative quantity"""
        client = BinanceFuturesClient("key", "secret")
        
        with pytest.raises(ValueError, match="Quantity must be greater than 0"):
            client.place_order('BTCUSDT', 'BUY', 'MARKET', -0.001)
    
    @patch('binance_client.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test handling of API errors"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'code': -1100,
            'msg': 'Invalid symbol'
        }
        mock_post.return_value = mock_response
        
        client = BinanceFuturesClient("key", "secret")
        
        with pytest.raises(Exception):
            client.place_order('INVALID', 'BUY', 'MARKET', 0.001)
    
    @patch('binance_client.requests.get')
    def test_test_connection_success(self, mock_get):
        """Test connection test passes"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        client = BinanceFuturesClient("key", "secret")
        result = client.test_connection()
        
        assert result is True
    
    @patch('binance_client.requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test connection test handles failure"""
        mock_get.side_effect = Exception("Network error")
        
        client = BinanceFuturesClient("key", "secret")
        result = client.test_connection()
        
        assert result is False