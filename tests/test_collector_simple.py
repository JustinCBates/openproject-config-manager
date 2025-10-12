"""Simple tests for interactive configuration collection."""

import pytest
from unittest.mock import Mock, patch
from openproject_config_manager.collector.interactive import InteractiveCollector


class TestInteractiveCollectorBasic:
    """Basic tests for InteractiveCollector class."""
    
    def test_init(self):
        """Test InteractiveCollector initialization."""
        collector = InteractiveCollector()
        assert collector is not None
        assert collector.ui is not None
    
    def test_init_with_custom_ui(self):
        """Test InteractiveCollector initialization with custom UI."""
        mock_ui = Mock()
        collector = InteractiveCollector(ui=mock_ui)
        assert collector.ui is mock_ui
    
    def test_parse_comma_separated_string(self):
        """Test parsing comma-separated strings."""
        collector = InteractiveCollector()
        
        # Test normal case
        result = collector._parse_comma_separated_string("a,b,c")
        assert result == ["a", "b", "c"]
        
        # Test with spaces
        result = collector._parse_comma_separated_string("a, b , c ")
        assert result == ["a", "b", "c"]
        
        # Test empty string
        result = collector._parse_comma_separated_string("")
        assert result == []
        
        # Test single item
        result = collector._parse_comma_separated_string("single")
        assert result == ["single"]
    
    def test_parse_key_value_pairs(self):
        """Test parsing key=value pairs."""
        collector = InteractiveCollector()
        
        # Test normal case
        result = collector._parse_key_value_pairs("KEY1=value1,KEY2=value2")
        assert result == {"KEY1": "value1", "KEY2": "value2"}
        
        # Test with spaces
        result = collector._parse_key_value_pairs("KEY1=value1, KEY2=value2 ")
        assert result == {"KEY1": "value1", "KEY2": "value2"}
        
        # Test empty string
        result = collector._parse_key_value_pairs("")
        assert result == {}
        
        # Test malformed pairs (should be skipped)
        result = collector._parse_key_value_pairs("KEY1=value1,MALFORMED,KEY2=value2")
        assert result == {"KEY1": "value1", "KEY2": "value2"}
    
    def test_get_default_value(self):
        """Test getting default values from discovered data."""
        discovered_data = {
            "environment": {
                "DATABASE_HOST": "env.host.com",
                "DATABASE_PORT": "5432"
            },
            "system": {
                "hostname": "system.host.com"
            }
        }
        
        collector = InteractiveCollector()
        
        # Test environment variable lookup
        result = collector._get_default_value(discovered_data, "DATABASE_HOST", "default.com")
        assert result == "env.host.com"
        
        # Test system info lookup
        result = collector._get_default_value(discovered_data, "hostname", "default.com", source="system")
        assert result == "system.host.com"
        
        # Test fallback to default
        result = collector._get_default_value(discovered_data, "NONEXISTENT", "fallback.com")
        assert result == "fallback.com"
        
        # Test no default provided
        result = collector._get_default_value(discovered_data, "NONEXISTENT")
        assert result is None
    
    def test_generate_secret_key(self):
        """Test secret key generation."""
        collector = InteractiveCollector()
        secret_key = collector._generate_secret_key()
        
        # Should be exactly 64 characters
        assert len(secret_key) == 64
        # Should be hexadecimal
        assert all(c in '0123456789abcdef' for c in secret_key)
    
    def test_generate_password(self):
        """Test password generation."""
        collector = InteractiveCollector()
        password = collector._generate_password()
        
        # Should be at least 16 characters
        assert len(password) >= 16
        # Should contain alphanumeric characters
        assert any(c.isalpha() for c in password)
        assert any(c.isdigit() for c in password)