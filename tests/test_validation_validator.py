"""Tests for configuration validation."""

import pytest
from unittest.mock import patch, Mock
import socket

from openproject_config_manager.validation.validator import ConfigurationValidator, ValidationResult
from openproject_config_manager.core.config import Configuration, DatabaseConfig, ProxyConfig, StorageConfig


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_init(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            recommendations=[]
        )
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.recommendations == []
    
    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        result.add_error("Test error")
        
        assert result.is_valid is False
        assert "Test error" in result.errors
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        result.add_warning("Test warning")
        
        assert result.is_valid is True  # Warnings don't affect validity
        assert "Test warning" in result.warnings
    
    def test_add_recommendation(self):
        """Test adding recommendations."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        result.add_recommendation("Test recommendation")
        
        assert result.is_valid is True
        assert "Test recommendation" in result.recommendations


class TestConfigurationValidator:
    """Test ConfigurationValidator class."""
    
    def test_init(self):
        """Test validator initialization."""
        validator = ConfigurationValidator()
        assert validator is not None
    
    def test_validate_configuration_valid(self, sample_configuration):
        """Test validation of valid configuration."""
        validator = ConfigurationValidator()
        
        with patch.object(validator, '_test_host_connectivity', return_value=True):
            result = validator.validate_configuration(sample_configuration)
        
        # Should pass validation (may have warnings but no errors)
        assert isinstance(result, ValidationResult)
    
    def test_validate_core_settings_valid(self, sample_configuration):
        """Test core settings validation with valid data."""
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_core_settings(sample_configuration, result)
        
        # Should not add errors for valid configuration
        assert len(result.errors) == 0
    
    def test_validate_core_settings_missing_secret_key(self):
        """Test core settings validation with missing secret key."""
        config = Configuration(
            secret_key_base="",  # Empty secret key
            proxy={"domain": "test.com"}
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_core_settings(config, result)
        
        # Should add error for missing secret key
        assert any("SECRET_KEY_BASE is required" in error for error in result.errors)
    
    def test_validate_core_settings_short_secret_key(self):
        """Test core settings validation with short secret key."""
        config = Configuration(
            secret_key_base="short",  # Too short
            proxy={"domain": "test.com"}
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_core_settings(config, result)
        
        # Should add warning for short secret key
        assert any("at least 64 characters" in warning for warning in result.warnings)
    
    def test_validate_core_settings_invalid_rails_env(self):
        """Test core settings validation with invalid Rails environment."""
        config = Configuration(
            secret_key_base="a" * 64,
            rails_env="invalid_env",
            proxy={"domain": "test.com"}
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_core_settings(config, result)
        
        # Should add error for invalid Rails environment
        assert any("Invalid RAILS_ENV" in error for error in result.errors)
    
    def test_validate_database_config_valid(self, sample_configuration):
        """Test database configuration validation with valid data."""
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        with patch.object(validator, '_test_host_connectivity', return_value=True):
            validator._validate_database_config(
                sample_configuration.database, result, {}
            )
        
        # Should not add errors for valid configuration
        assert len(result.errors) == 0
    
    def test_validate_database_config_invalid_adapter(self):
        """Test database validation with invalid adapter."""
        db_config = DatabaseConfig(
            adapter="invalid_adapter",
            host="db",
            port=5432,
            name="openproject",
            username="openproject",
            password="password"
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_database_config(db_config, result, {})
        
        # Should add error for invalid adapter
        assert any("Unsupported database adapter" in error for error in result.errors)
    
    def test_validate_database_config_missing_host(self):
        """Test database validation with missing host."""
        db_config = DatabaseConfig(
            adapter="postgresql",
            host="",  # Empty host
            port=5432,
            name="openproject",
            username="openproject",
            password="password"
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_database_config(db_config, result, {})
        
        # Should add error for missing host
        assert any("Database host is required" in error for error in result.errors)
    
    def test_validate_database_config_invalid_port(self):
        """Test database validation with invalid port."""
        db_config = DatabaseConfig(
            adapter="postgresql",
            host="db",
            port=0,  # Invalid port
            name="openproject",
            username="openproject",
            password="password"
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_database_config(db_config, result, {})
        
        # Should add error for invalid port
        assert any("Invalid database port" in error for error in result.errors)
    
    def test_validate_proxy_config_valid(self, sample_configuration):
        """Test proxy configuration validation with valid data."""
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_proxy_config(sample_configuration.proxy, result)
        
        # Should not add errors for valid configuration
        assert len(result.errors) == 0
    
    def test_validate_proxy_config_missing_domain(self):
        """Test proxy validation with missing domain."""
        proxy_config = ProxyConfig(domain="")  # Empty domain
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_proxy_config(proxy_config, result)
        
        # Should add error for missing domain
        assert any("Primary domain is required" in error for error in result.errors)
    
    def test_validate_proxy_config_invalid_domain(self):
        """Test proxy validation with invalid domain."""
        proxy_config = ProxyConfig(domain="invalid_domain")
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_proxy_config(proxy_config, result)
        
        # Should add error for invalid domain format
        assert any("Invalid domain format" in error for error in result.errors)
    
    def test_validate_proxy_config_lets_encrypt_missing_email(self):
        """Test proxy validation with Let's Encrypt but missing email."""
        proxy_config = ProxyConfig(
            domain="test.com",
            ssl_enabled=True,
            lets_encrypt=True,
            lets_encrypt_email=""  # Missing email
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_proxy_config(proxy_config, result)
        
        # Should add error for missing Let's Encrypt email
        assert any("Let's Encrypt email is required" in error for error in result.errors)
    
    def test_validate_proxy_config_lets_encrypt_localhost(self):
        """Test proxy validation with Let's Encrypt and localhost domain."""
        proxy_config = ProxyConfig(
            domain="localhost",
            ssl_enabled=True,
            lets_encrypt=True,
            lets_encrypt_email="test@example.com"
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_proxy_config(proxy_config, result)
        
        # Should add error for Let's Encrypt with localhost
        assert any("Let's Encrypt cannot issue certificates for localhost" in error for error in result.errors)
    
    def test_validate_storage_config_valid(self, sample_configuration):
        """Test storage configuration validation with valid data."""
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_storage_config(sample_configuration.storage, result)
        
        # Should not add errors for valid configuration
        assert len(result.errors) == 0
    
    def test_validate_storage_config_invalid_cron(self):
        """Test storage validation with invalid cron schedule."""
        storage_config = StorageConfig(
            backup_enabled=True,
            backup_schedule="invalid cron"  # Invalid format
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_storage_config(storage_config, result)
        
        # Should add error for invalid cron schedule
        assert any("Invalid backup schedule format" in error for error in result.errors)
    
    def test_validate_storage_config_invalid_retention(self):
        """Test storage validation with invalid retention period."""
        storage_config = StorageConfig(
            backup_enabled=True,
            backup_retention_days=0  # Invalid retention
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_storage_config(storage_config, result)
        
        # Should add error for invalid retention
        assert any("Backup retention must be at least 1 day" in error for error in result.errors)
    
    def test_validate_email_config_smtp_missing_address(self):
        """Test email validation with SMTP but missing address."""
        config = Configuration(
            secret_key_base="a" * 64,
            proxy={"domain": "test.com"},
            email_delivery_method="smtp",
            smtp_address=""  # Missing SMTP address
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_email_config(config, result)
        
        # Should add error for missing SMTP address
        assert any("SMTP address is required" in error for error in result.errors)
    
    def test_validate_email_config_invalid_port(self):
        """Test email validation with invalid SMTP port."""
        config = Configuration(
            secret_key_base="a" * 64,
            proxy={"domain": "test.com"},
            email_delivery_method="smtp",
            smtp_address="smtp.example.com",
            smtp_port=0  # Invalid port
        )
        
        validator = ConfigurationValidator()
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        validator._validate_email_config(config, result)
        
        # Should add error for invalid SMTP port
        assert any("Invalid SMTP port" in error for error in result.errors)
    
    def test_is_valid_domain(self):
        """Test domain validation helper."""
        validator = ConfigurationValidator()
        
        # Valid domains
        valid_domains = [
            "example.com",
            "sub.example.com",
            "test-site.com",
            "site123.org",
            "a.b.c.d.example.com"
        ]
        
        for domain in valid_domains:
            assert validator._is_valid_domain(domain) is True
        
        # Invalid domains
        invalid_domains = [
            "",
            "invalid",
            "-example.com",
            "example-.com",
            "exam ple.com",
            "ex@mple.com",
            "a" * 300  # Too long
        ]
        
        for domain in invalid_domains:
            assert validator._is_valid_domain(domain) is False
    
    def test_is_valid_email(self):
        """Test email validation helper."""
        validator = ConfigurationValidator()
        
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.org",
            "user123@sub.example.com"
        ]
        
        for email in valid_emails:
            assert validator._is_valid_email(email) is True
        
        # Invalid emails
        invalid_emails = [
            "",
            "invalid",
            "@example.com",
            "user@",
            "user.example.com",
            "user@example",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            assert validator._is_valid_email(email) is False
    
    def test_is_valid_cron_schedule(self):
        """Test cron schedule validation helper."""
        validator = ConfigurationValidator()
        
        # Valid cron schedules
        valid_schedules = [
            "0 2 * * *",  # Daily at 2 AM
            "30 1 * * 0",  # Weekly on Sunday at 1:30 AM
            "0 0 1 * *",  # Monthly on 1st at midnight
            "*/15 * * * *",  # Every 15 minutes
            "0 9-17 * * 1-5"  # Hourly during business hours on weekdays
        ]
        
        for schedule in valid_schedules:
            assert validator._is_valid_cron_schedule(schedule) is True
        
        # Invalid cron schedules
        invalid_schedules = [
            "",
            "invalid",
            "0 2 * *",  # Too few fields
            "0 2 * * * *",  # Too many fields
            "60 2 * * *",  # Invalid minute
            "0 25 * * *",  # Invalid hour
            "0 2 32 * *",  # Invalid day
            "0 2 * 13 *",  # Invalid month
            "0 2 * * 8"  # Invalid weekday
        ]
        
        for schedule in invalid_schedules:
            assert validator._is_valid_cron_schedule(schedule) is False
    
    @patch('socket.socket')
    def test_test_host_connectivity_success(self, mock_socket):
        """Test host connectivity check success."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0  # Success
        mock_socket.return_value = mock_sock
        
        validator = ConfigurationValidator()
        result = validator._test_host_connectivity("example.com", 80)
        
        assert result is True
        mock_sock.connect_ex.assert_called_once_with(("example.com", 80))
        mock_sock.close.assert_called_once()
    
    @patch('socket.socket')
    def test_test_host_connectivity_failure(self, mock_socket):
        """Test host connectivity check failure."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1  # Failure
        mock_socket.return_value = mock_sock
        
        validator = ConfigurationValidator()
        result = validator._test_host_connectivity("example.com", 80)
        
        assert result is False
    
    @patch('socket.socket')
    def test_test_host_connectivity_exception(self, mock_socket):
        """Test host connectivity check with exception."""
        mock_socket.side_effect = Exception("Network error")
        
        validator = ConfigurationValidator()
        result = validator._test_host_connectivity("example.com", 80)
        
        assert result is False
    
    def test_parse_server_address(self):
        """Test server address parsing helper."""
        validator = ConfigurationValidator()
        
        # Test cases: (input, default_port, expected_host, expected_port)
        test_cases = [
            ("example.com:8080", 80, "example.com", 8080),
            ("example.com", 80, "example.com", 80),
            ("localhost:3306", 5432, "localhost", 3306),
            ("192.168.1.1:5432", 3306, "192.168.1.1", 5432),
            ("server:invalid_port", 80, "server:invalid_port", 80),  # Invalid port falls back
        ]
        
        for address, default_port, expected_host, expected_port in test_cases:
            host, port = validator._parse_server_address(address, default_port)
            assert host == expected_host
            assert port == expected_port
    
    def test_is_weak_secret_key(self):
        """Test weak secret key detection."""
        validator = ConfigurationValidator()
        
        # Weak keys
        weak_keys = [
            "short",  # Too short
            "a" * 32,  # Too short
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # Low entropy
            "abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef",  # Repeated pattern
            "passwordpasswordpasswordpasswordpasswordpasswordpasswordpassword",  # Contains 'password'
        ]
        
        for key in weak_keys:
            assert validator._is_weak_secret_key(key) is True
        
        # Strong keys
        strong_keys = [
            "a" * 64,  # Long enough, acceptable
            "f4e5d6c7b8a9f0e1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5e4f38291b0a",  # Good entropy
        ]
        
        for key in strong_keys:
            assert validator._is_weak_secret_key(key) is False