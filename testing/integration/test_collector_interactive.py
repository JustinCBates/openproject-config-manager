"""Tests for interactive configuration collection."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from openproject_config_manager.collector.interactive import InteractiveCollector
from openproject_config_manager.core.config import Configuration


class TestInteractiveCollector:
    """Test InteractiveCollector class."""
    
    def test_init(self):
        """Test InteractiveCollector initialization."""
        collector = InteractiveCollector()
        assert collector is not None
        assert collector.console is not None
    
    @patch('openproject_config_manager.collector.interactive.Console')
    def test_init_with_console(self, mock_console_class):
        """Test InteractiveCollector initialization with custom console."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        collector = InteractiveCollector()
        assert collector.console == mock_console
    
    @patch('openproject_config_manager.ui.console.ConsoleUI.select')
    @patch('openproject_config_manager.ui.console.ConsoleUI.prompt')
    @patch('openproject_config_manager.ui.console.ConsoleUI.show_section_header')
    def test_collect_configuration_minimal(self, mock_header, mock_prompt, mock_select):
        """Test basic configuration collection."""
        # Setup mocks for minimal configuration
        mock_prompt.side_effect = [
            "test-secret-key-123456789012345678901234567890123456789012345678901234",  # secret_key_base
            "example.com",  # domain
            "localhost",  # database host
            "5432",  # database port
            "openproject_db",  # database name
            "openproject_user",  # database user
            "secure_password"  # database password
        ]
        
        mock_select.side_effect = [
            "production",  # rails_env
            "postgresql"  # database adapter
        ]
        
        collector = InteractiveCollector()
        
        with patch.object(collector, '_collect_optional_sections', return_value={}):
            config = collector.collect_configuration({})
        
        assert isinstance(config, Configuration)
        assert config.secret_key_base == "test-secret-key-123456789012345678901234567890123456789012345678901234"
        assert config.rails_env == "production"
        assert config.proxy.domain == "example.com"
        assert config.database.adapter == "postgresql"
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.database.name == "openproject_db"
        assert config.database.username == "openproject_user"
        assert config.database.password == "secure_password"
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_choice')
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_core_settings(self, mock_text, mock_choice):
        """Test collection of core settings."""
        mock_text.return_value = "test-secret-key-123456789012345678901234567890123456789012345678901234"
        mock_choice.return_value = "development"
        
        collector = InteractiveCollector()
        core_settings = collector._collect_core_settings({})
        
        assert "secret_key_base" in core_settings
        assert "rails_env" in core_settings
        assert core_settings["secret_key_base"] == "test-secret-key-123456789012345678901234567890123456789012345678901234"
        assert core_settings["rails_env"] == "development"
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_proxy_settings(self, mock_text):
        """Test collection of proxy settings."""
        mock_text.side_effect = ["example.com", "8080"]
        
        collector = InteractiveCollector()
        
        with patch.object(collector.ui, 'prompt_boolean', return_value=False):
            proxy_settings = collector._collect_proxy_settings({})
        
        assert "domain" in proxy_settings
        assert "port" in proxy_settings
        assert "ssl_enabled" in proxy_settings
        assert proxy_settings["domain"] == "example.com"
        assert proxy_settings["port"] == 8080
        assert proxy_settings["ssl_enabled"] is False
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean')
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_proxy_settings_with_ssl(self, mock_text, mock_boolean):
        """Test collection of proxy settings with SSL enabled."""
        mock_text.side_effect = [
            "secure.example.com",  # domain
            "443",  # port
            "/path/to/cert.pem",  # ssl_cert_path
            "/path/to/key.pem",  # ssl_key_path
            "additional1.com,additional2.com"  # additional_domains
        ]
        
        mock_boolean.side_effect = [
            True,  # ssl_enabled
            False,  # lets_encrypt
            True   # additional_domains prompt
        ]
        
        collector = InteractiveCollector()
        proxy_settings = collector._collect_proxy_settings({})
        
        assert proxy_settings["ssl_enabled"] is True
        assert proxy_settings["lets_encrypt"] is False
        assert proxy_settings["ssl_cert_path"] == "/path/to/cert.pem"
        assert proxy_settings["ssl_key_path"] == "/path/to/key.pem"
        assert proxy_settings["additional_domains"] == ["additional1.com", "additional2.com"]
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_choice')
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_database_settings(self, mock_text, mock_choice):
        """Test collection of database settings."""
        mock_choice.return_value = "mysql2"
        mock_text.side_effect = [
            "db.example.com",  # host
            "3306",  # port
            "openproject_prod",  # name
            "op_user",  # username
            "secure_db_pass"  # password
        ]
        
        collector = InteractiveCollector()
        db_settings = collector._collect_database_settings({})
        
        assert db_settings["adapter"] == "mysql2"
        assert db_settings["host"] == "db.example.com"
        assert db_settings["port"] == 3306
        assert db_settings["name"] == "openproject_prod"
        assert db_settings["username"] == "op_user"
        assert db_settings["password"] == "secure_db_pass"
    
    def test_collect_database_settings_with_defaults(self):
        """Test database settings collection with provided defaults."""
        discovered_data = {
            "environment": {
                "DATABASE_HOST": "discovered.host.com",
                "DATABASE_PORT": "5433",
                "DATABASE_NAME": "discovered_db"
            }
        }
        
        collector = InteractiveCollector()
        
        with patch.object(collector.ui, 'prompt_choice', return_value="postgresql"), \
             patch.object(collector.ui, 'prompt_text') as mock_text:
            
            mock_text.side_effect = [
                "",  # host (use default)
                "",  # port (use default)  
                "",  # name (use default)
                "new_user",  # username
                "new_pass"  # password
            ]
            
            db_settings = collector._collect_database_settings(discovered_data)
        
        assert db_settings["host"] == "discovered.host.com"
        assert db_settings["port"] == 5433
        assert db_settings["name"] == "discovered_db"
        assert db_settings["username"] == "new_user"
        assert db_settings["password"] == "new_pass"
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean')
    def test_collect_optional_sections_none_selected(self, mock_boolean):
        """Test optional sections when none are selected."""
        mock_boolean.return_value = False  # No to all optional sections
        
        collector = InteractiveCollector()
        optional_settings = collector._collect_optional_sections({})
        
        # Should return empty dict when no sections selected
        assert optional_settings == {}
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean')
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_optional_sections_email_selected(self, mock_text, mock_boolean):
        """Test optional sections with email configuration."""
        mock_boolean.side_effect = [
            True,  # Configure email
            False, False, False, False  # No to other sections
        ]
        
        mock_text.side_effect = [
            "smtp.example.com",  # smtp_address
            "587",  # smtp_port
            "noreply@example.com",  # smtp_user_name
            "smtp_password",  # smtp_password
            "openproject@example.com"  # from_email
        ]
        
        collector = InteractiveCollector()
        optional_settings = collector._collect_optional_sections({})
        
        assert "email" in optional_settings
        email_config = optional_settings["email"]
        assert email_config["smtp_address"] == "smtp.example.com"
        assert email_config["smtp_port"] == 587
        assert email_config["smtp_user_name"] == "noreply@example.com"
        assert email_config["smtp_password"] == "smtp_password"
        assert email_config["from_email"] == "openproject@example.com"
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_email_settings(self, mock_text):
        """Test email settings collection."""
        mock_text.side_effect = [
            "mail.example.com",
            "465",
            "admin@example.com",
            "mail_secret",
            "system@example.com"
        ]
        
        collector = InteractiveCollector()
        
        with patch.object(collector.ui, 'prompt_choice', return_value="smtp"):
            email_settings = collector._collect_email_settings({})
        
        assert email_settings["delivery_method"] == "smtp"
        assert email_settings["smtp_address"] == "mail.example.com"
        assert email_settings["smtp_port"] == 465
        assert email_settings["smtp_user_name"] == "admin@example.com"
        assert email_settings["smtp_password"] == "mail_secret"
        assert email_settings["from_email"] == "system@example.com"
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean')
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_storage_settings(self, mock_text, mock_boolean):
        """Test storage settings collection."""
        mock_boolean.side_effect = [True, True]  # Enable backup, configure S3
        mock_text.side_effect = [
            "/backup/location",  # backup_location
            "7",  # backup_retention_days
            "0 2 * * *",  # backup_schedule
            "us-west-2",  # s3_region
            "my-backup-bucket",  # s3_bucket
            "AKIAIOSFODNN7EXAMPLE",  # s3_access_key_id
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # s3_secret_access_key
        ]
        
        collector = InteractiveCollector()
        storage_settings = collector._collect_storage_settings({})
        
        assert storage_settings["backup_enabled"] is True
        assert storage_settings["backup_location"] == "/backup/location"
        assert storage_settings["backup_retention_days"] == 7
        assert storage_settings["backup_schedule"] == "0 2 * * *"
        assert storage_settings["s3_region"] == "us-west-2"
        assert storage_settings["s3_bucket"] == "my-backup-bucket"
        assert storage_settings["s3_access_key_id"] == "AKIAIOSFODNN7EXAMPLE"
        assert storage_settings["s3_secret_access_key"] == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_performance_settings(self, mock_text):
        """Test performance settings collection."""
        mock_text.side_effect = [
            "4",  # worker_processes
            "redis://localhost:6379/0",  # redis_url
            "512m",  # worker_memory_limit
            "30"  # worker_timeout
        ]
        
        collector = InteractiveCollector()
        perf_settings = collector._collect_performance_settings({})
        
        assert perf_settings["worker_processes"] == 4
        assert perf_settings["redis_url"] == "redis://localhost:6379/0"
        assert perf_settings["worker_memory_limit"] == "512m"
        assert perf_settings["worker_timeout"] == 30
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_security_settings(self, mock_text):
        """Test security settings collection."""
        mock_text.side_effect = [
            "30",  # session_timeout
            "5",  # login_attempt_limit
            "admin,superuser",  # admin_users
            "example.com,*.example.com"  # allowed_hosts
        ]
        
        collector = InteractiveCollector()
        
        with patch.object(collector.ui, 'prompt_boolean', return_value=True):
            security_settings = collector._collect_security_settings({})
        
        assert security_settings["session_timeout"] == 30
        assert security_settings["login_attempt_limit"] == 5
        assert security_settings["force_ssl"] is True
        assert security_settings["admin_users"] == ["admin", "superuser"]
        assert security_settings["allowed_hosts"] == ["example.com", "*.example.com"]
    
    @patch('openproject_config_manager.ui.console.UIConsole.prompt_text')
    def test_collect_custom_variables(self, mock_text):
        """Test custom variables collection."""
        mock_text.side_effect = [
            "CUSTOM_VAR1=value1,CUSTOM_VAR2=value2"
        ]
        
        collector = InteractiveCollector()
        
        with patch.object(collector.ui, 'prompt_boolean', return_value=True):
            custom_vars = collector._collect_custom_variables({})
        
        assert custom_vars == {
            "CUSTOM_VAR1": "value1",
            "CUSTOM_VAR2": "value2"
        }
    
    def test_collect_custom_variables_skip(self):
        """Test skipping custom variables collection."""
        collector = InteractiveCollector()
        
        with patch.object(collector.ui, 'prompt_boolean', return_value=False):
            custom_vars = collector._collect_custom_variables({})
        
        assert custom_vars == {}
    
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