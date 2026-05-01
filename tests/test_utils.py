import pytest
import sys
import os
from unittest.mock import patch

class TestConfigValidation:
    
    def test_config_validation_passes(self):
        """Test config validation with valid keys"""
        with patch.dict(os.environ, {'BINANCE_API_KEY': 'valid_key', 'BINANCE_SECRET_KEY': 'valid_secret'}):
            from config import validate_config
            # Should not raise exception
            assert validate_config() is True
    
    def test_config_validation_fails_missing_key(self):
        """Test config validation fails when key missing"""
        with patch.dict(os.environ, {'BINANCE_SECRET_KEY': 'valid_secret'}):
            from config import validate_config
            with pytest.raises(ValueError, match="Please set your API credentials"):
                validate_config()