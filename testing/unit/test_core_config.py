"""Tests for core configuration models."""

import pytest
from pathlib import Path
from pydantic import ValidationError

from openproject_config_manager.core.config import (
    Configuration, 
    ConfigurationVariable, 
    DatabaseConfig, 
    ProxyConfig, 
    StorageConfig
)


class TestConfigurationVariable:
    """Test ConfigurationVariable model."""
    
    def test_create_valid_variable(self):
        """Test creating a valid configuration variable."""
        var = ConfigurationVariable(
            name="TEST_VAR",
            value="test_value",
            description="Test variable",
            category="test"
        )
        
        assert var.name == "TEST_VAR"
        assert var.value == "test_value"
        assert var.description == "Test variable"
        assert var.category == "test"
        assert var.required is True
        assert var.sensitive is False
    
    def test_name_validation(self):
        """Test variable name validation."""
        # Valid names
        valid_names = ["TEST_VAR", "DB_HOST", "SSL-ENABLED", "VAR123"]
        for name in valid_names:
            var = ConfigurationVariable(
                name=name,
                description="Test",
                category="test"
            )
            assert var.name == name.upper()
        
        # Invalid names
        invalid_names = ["", "123_VAR", "VAR@SPECIAL", "VAR SPACE"]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                ConfigurationVariable(
                    name=name,
                    description="Test",
                    category="test"
                )
    
    def test_effective_value(self):
        """Test effective value property."""
        # With value
        var = ConfigurationVariable(
            name="TEST_VAR",
            value="actual_value",
            default="default_value",
            description="Test",
            category="test"
        )
        assert var.effective_value == "actual_value"
        
        # Without value, with default
        var = ConfigurationVariable(
            name="TEST_VAR",
            default="default_value",
            description="Test",
            category="test"
        )
        assert var.effective_value == "default_value"
        
        # Without value or default
        var = ConfigurationVariable(
            name="TEST_VAR",
            description="Test",
            category="test"
        )
        assert var.effective_value is None
    
    def test_is_valid(self):
        """Test variable validation."""
        # Required variable with value
        var = ConfigurationVariable(
            name="TEST_VAR",
            value="test_value",
            description="Test",
            category="test",
            required=True
        )
        assert var.is_valid() is True
        
        # Required variable without value
        var = ConfigurationVariable(
            name="TEST_VAR",
            description="Test",
            category="test",
            required=True
        )
        assert var.is_valid() is False
        
        # Optional variable without value
        var = ConfigurationVariable(
            name="TEST_VAR",
            description="Test",
            category="test",
            required=False
        )
        assert var.is_valid() is True
        
        # Variable with choices
        var = ConfigurationVariable(
            name="TEST_VAR",
            value="valid_choice",
            description="Test",
            category="test",
            choices=["valid_choice", "another_choice"]
        )
        assert var.is_valid() is True
        
        # Variable with invalid choice
        var = ConfigurationVariable(
            name="TEST_VAR",
            value="invalid_choice",
            description="Test",
            category="test",
            choices=["valid_choice", "another_choice"]
        )
        assert var.is_valid() is False


class TestDatabaseConfig:
    """Test DatabaseConfig model."""
    
    def test_create_valid_database_config(self):
        """Test creating valid database configuration."""
        db_config = DatabaseConfig(
            adapter="postgresql",
            host="db",
            port=5432,
            name="openproject",
            username="openproject",
            password="test_password"
        )
        
        assert db_config.adapter == "postgresql"
        assert db_config.host == "db"
        assert db_config.port == 5432
        assert db_config.name == "openproject"
        assert db_config.username == "openproject"
        assert db_config.password == "test_password"
        assert db_config.encoding == "utf8"  # default
    
    def test_port_validation(self):
        """Test database port validation."""
        # Valid ports
        valid_ports = [1, 5432, 3306, 65535]
        for port in valid_ports:
            db_config = DatabaseConfig(
                adapter="postgresql",
                host="db",
                port=port,
                name="openproject",
                username="openproject",
                password="test_password"
            )
            assert db_config.port == port
        
        # Invalid ports
        invalid_ports = [0, -1, 65536, 100000]
        for port in invalid_ports:
            with pytest.raises(ValidationError):
                DatabaseConfig(
                    adapter="postgresql",
                    host="db",
                    port=port,
                    name="openproject",
                    username="openproject",
                    password="test_password"
                )


class TestProxyConfig:
    """Test ProxyConfig model."""
    
    def test_create_valid_proxy_config(self):
        """Test creating valid proxy configuration."""
        proxy_config = ProxyConfig(
            domain="openproject.example.com",
            additional_domains=["op.example.com"],
            ssl_enabled=True,
            lets_encrypt=True,
            lets_encrypt_email="admin@example.com"
        )
        
        assert proxy_config.domain == "openproject.example.com"
        assert proxy_config.additional_domains == ["op.example.com"]
        assert proxy_config.ssl_enabled is True
        assert proxy_config.lets_encrypt is True
        assert proxy_config.lets_encrypt_email == "admin@example.com"
    
    def test_domain_validation(self):
        """Test domain validation."""
        # Valid domains
        valid_domains = ["example.com", "sub.example.com", "test-site.com"]
        for domain in valid_domains:
            proxy_config = ProxyConfig(domain=domain)
            assert proxy_config.domain == domain.lower()
        
        # Invalid domains
        invalid_domains = ["", "invalid", "domain."]
        for domain in invalid_domains:
            with pytest.raises(ValidationError):
                ProxyConfig(domain=domain)


class TestStorageConfig:
    """Test StorageConfig model."""
    
    def test_create_valid_storage_config(self):
        """Test creating valid storage configuration."""
        storage_config = StorageConfig(
            data_volume="openproject_data",
            logs_volume="openproject_logs",
            backup_enabled=True,
            backup_schedule="0 2 * * *",
            backup_retention_days=30,
            backup_location="./backups"
        )
        
        assert storage_config.data_volume == "openproject_data"
        assert storage_config.logs_volume == "openproject_logs"
        assert storage_config.backup_enabled is True
        assert storage_config.backup_schedule == "0 2 * * *"
        assert storage_config.backup_retention_days == 30
        assert storage_config.backup_location == "./backups"
    
    def test_backup_retention_validation(self):
        """Test backup retention validation."""
        # Valid retention periods
        valid_periods = [1, 30, 365]
        for period in valid_periods:
            storage_config = StorageConfig(backup_retention_days=period)
            assert storage_config.backup_retention_days == period
        
        # Invalid retention periods
        invalid_periods = [0, -1]
        for period in invalid_periods:
            with pytest.raises(ValidationError):
                StorageConfig(backup_retention_days=period)


class TestConfiguration:
    """Test Configuration model."""
    
    def test_create_minimal_configuration(self):
        """Test creating minimal configuration."""
        config = Configuration(
            secret_key_base="a" * 64,
            proxy={"domain": "openproject.local"}
        )
        
        assert config.secret_key_base == "a" * 64
        assert config.proxy.domain == "openproject.local"
        assert config.rails_env == "production"  # default
    
    def test_create_complete_configuration(self, sample_config_data):
        """Test creating complete configuration."""
        config = Configuration(**sample_config_data)
        
        assert config.secret_key_base == sample_config_data['secret_key_base']
        assert config.rails_env == sample_config_data['rails_env']
        assert config.database.adapter == sample_config_data['database']['adapter']
        assert config.proxy.domain == sample_config_data['proxy']['domain']
        assert config.storage.backup_enabled == sample_config_data['storage']['backup_enabled']
    
    def test_to_cfg_format(self, sample_configuration):
        """Test configuration export to .cfg format."""
        cfg_content = sample_configuration.to_cfg_format()
        
        # Check that key sections are present
        assert "# OpenProject Configuration" in cfg_content
        assert 'SECRET_KEY_BASE=' in cfg_content
        assert 'DATABASE_ADAPTER=' in cfg_content
        assert 'DOMAIN=' in cfg_content
        
        # Check specific values
        assert f'SECRET_KEY_BASE="{sample_configuration.secret_key_base}"' in cfg_content
        assert f'RAILS_ENV="{sample_configuration.rails_env}"' in cfg_content
        assert f'DATABASE_ADAPTER="{sample_configuration.database.adapter}"' in cfg_content
    
    def test_from_cfg_file(self, temp_dir, sample_cfg_content):
        """Test loading configuration from .cfg file."""
        cfg_file = temp_dir / "test_config.cfg"
        cfg_file.write_text(sample_cfg_content, encoding='utf-8')
        
        config = Configuration.from_cfg_file(cfg_file)
        
        assert config.secret_key_base == "test_secret_key"
        assert config.rails_env == "production"
        assert config.database.adapter == "postgresql"
        assert config.database.host == "db"
        assert config.database.port == 5432
        assert config.proxy.domain == "openproject.example.com"
        assert config.proxy.ssl_enabled is True
        assert config.proxy.lets_encrypt is True
    
    def test_from_cfg_file_not_found(self, temp_dir):
        """Test loading configuration from non-existent file."""
        cfg_file = temp_dir / "nonexistent.cfg"
        
        with pytest.raises(FileNotFoundError):
            Configuration.from_cfg_file(cfg_file)
    
    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed in configuration."""
        config_data = {
            'secret_key_base': 'a' * 64,
            'proxy': {'domain': 'openproject.local'},
            'custom_field': 'custom_value'
        }
        
        config = Configuration(**config_data)
        assert hasattr(config, 'custom_field')
        assert config.custom_field == 'custom_value'
    
    def test_validation_assignment(self, sample_configuration):
        """Test that validation occurs on assignment."""
        # Valid assignment
        sample_configuration.rails_env = "development"
        assert sample_configuration.rails_env == "development"
        
        # Invalid assignment should raise ValidationError
        with pytest.raises(ValidationError):
            sample_configuration.database.port = -1
    
    def test_custom_variables(self):
        """Test custom variables handling."""
        config = Configuration(
            secret_key_base="a" * 64,
            proxy={"domain": "openproject.local"},
            custom_variables={"CUSTOM_VAR": "custom_value", "ANOTHER_VAR": "another_value"}
        )
        
        assert config.custom_variables["CUSTOM_VAR"] == "custom_value"
        assert config.custom_variables["ANOTHER_VAR"] == "another_value"
        
        # Test in .cfg export
        cfg_content = config.to_cfg_format()
        assert 'CUSTOM_VAR="custom_value"' in cfg_content
        assert 'ANOTHER_VAR="another_value"' in cfg_content