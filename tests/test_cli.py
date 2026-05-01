# tests/test_cli.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from unittest.mock import patch
from cli_handler import validate_inputs, format_order_response

class TestCLIValidation:
    
    def test_valid_market_order_input(self):
        """Test valid market order inputs"""
        result = validate_inputs('BTCUSDT', 'BUY', 'MARKET', '0.001', None)
        assert result == ('BTCUSDT', 'BUY', 'MARKET', 0.001, None)
    
    def test_valid_limit_order_input(self):
        """Test valid limit order inputs"""
        result = validate_inputs('ETHUSDT', 'SELL', 'LIMIT', '0.1', '2500')
        assert result == ('ETHUSDT', 'SELL', 'LIMIT', 0.1, 2500.0)
    
    def test_invalid_symbol(self):
        """Test empty symbol validation"""
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_inputs('', 'BUY', 'MARKET', '0.001', None)
    
    def test_invalid_side(self):
        """Test invalid side validation"""
        with pytest.raises(ValueError, match="Side must be BUY or SELL"):
            validate_inputs('BTCUSDT', 'INVALID', 'MARKET', '0.001', None)
    
    def test_invalid_order_type(self):
        """Test invalid order type validation"""
        with pytest.raises(ValueError, match="Order type must be MARKET or LIMIT"):
            validate_inputs('BTCUSDT', 'BUY', 'INVALID', '0.001', None)
    
    def test_invalid_quantity(self):
        """Test invalid quantity (non-numeric)"""
        with pytest.raises(ValueError, match="Quantity must be a valid number"):
            validate_inputs('BTCUSDT', 'BUY', 'MARKET', 'abc', None)
    
    def test_negative_quantity(self):
        """Test negative quantity validation"""
        with pytest.raises(ValueError, match="Quantity must be greater than 0"):
            validate_inputs('BTCUSDT', 'BUY', 'MARKET', '-0.001', None)
    
    def test_missing_price_for_limit(self):
        """Test limit order requires price"""
        with pytest.raises(ValueError, match="Price is required for LIMIT orders"):
            validate_inputs('BTCUSDT', 'BUY', 'LIMIT', '0.001', None)
    
    def test_invalid_price_for_limit(self):
        """Test invalid price for limit order"""
        with pytest.raises(ValueError, match="Price must be a valid number"):
            validate_inputs('BTCUSDT', 'BUY', 'LIMIT', '0.001', 'abc')
    
    def test_negative_price_for_limit(self):
        """Test negative price validation"""
        with pytest.raises(ValueError, match="Price must be greater than 0"):
            validate_inputs('BTCUSDT', 'BUY', 'LIMIT', '0.001', '-100')

class TestFormatOrderResponse:
    
    def test_format_successful_order(self):
        """Test formatting successful order response"""
        response = {
            'orderId': '12345',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'status': 'FILLED',
            'origQty': '0.001',
            'executedQty': '0.001',
            'price': '0'
        }
        
        output = format_order_response(response)
        assert 'ORDER PLACED SUCCESSFULLY' in output
        assert 'Order ID: 12345' in output
        assert 'Symbol: BTCUSDT' in output
    
    def test_format_api_error(self):
        """Test formatting API error response"""
        response = {
            'code': -1100,
            'msg': 'Invalid symbol'
        }
        
        output = format_order_response(response)
        assert 'API ERROR' in output
        assert 'Invalid symbol' in output