"""Integration tests for OpenProject Configuration Manager."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

from openproject_config_manager.core.manager import ConfigurationManager
from openproject_config_manager.core.config import Configuration
from openproject_config_manager.collector.interactive import InteractiveCollector
from openproject_config_manager.validation.validator import ConfigurationValidator
from openproject_config_manager.export.cfg_writer import CfgWriter


class TestIntegrationFullProcess:
    """Integration tests for the complete configuration process."""
    
    def test_full_configuration_process_minimal(self, temp_dir):
        """Test complete configuration process with minimal settings."""
        output_file = temp_dir / "integration_test.cfg"
        
        # Mock all user inputs for minimal configuration
        with patch('openproject_config_manager.ui.console.UIConsole.prompt_text') as mock_text, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_choice') as mock_choice, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean') as mock_boolean:
            
            # Setup minimal configuration inputs
            mock_text.side_effect = [
                "test-secret-key-1234567890123456789012345678901234567890123456789012",  # secret_key_base
                "test.example.com",  # domain
                "localhost",  # database host
                "5432",  # database port
                "openproject_test",  # database name
                "test_user",  # database username
                "test_password"  # database password
            ]
            
            mock_choice.side_effect = [
                "development",  # rails_env
                "postgresql"  # database adapter
            ]
            
            mock_boolean.return_value = False  # No to all optional sections
            
            # Run the configuration manager
            manager = ConfigurationManager(output_file)
            
            # Mock discovery to return empty data
            with patch.object(manager, 'run_discovery_phase', return_value={}):
                result = manager.run_full_process({})
            
            assert result is True
            assert output_file.exists()
            
            # Verify the configuration file content
            content = output_file.read_text(encoding='utf-8')
            assert 'SECRET_KEY_BASE=' in content
            assert 'RAILS_ENV=development' in content
            assert 'DOMAIN=test.example.com' in content
            assert 'DATABASE_ADAPTER=postgresql' in content
    
    def test_configuration_roundtrip(self, temp_dir):
        """Test configuration export and import roundtrip."""
        cfg_file = temp_dir / "roundtrip.cfg"
        
        # Create a comprehensive configuration
        config = Configuration(
            secret_key_base="a" * 64,
            rails_env="production",
            proxy={
                "domain": "example.com",
                "port": 443,
                "ssl_enabled": True,
                "lets_encrypt": False,
                "ssl_cert_path": "/path/to/cert.pem",
                "ssl_key_path": "/path/to/key.pem"
            },
            database={
                "adapter": "postgresql",
                "host": "db.example.com",
                "port": 5432,
                "name": "openproject_prod",
                "username": "op_user",
                "password": "secure_password"
            },
            email={
                "delivery_method": "smtp",
                "smtp_address": "smtp.example.com",
                "smtp_port": 587,
                "smtp_user_name": "noreply@example.com",
                "smtp_password": "smtp_secret",
                "from_email": "system@example.com"
            },
            storage={
                "backup_enabled": True,
                "backup_location": "/backups",
                "backup_retention_days": 30,
                "backup_schedule": "0 2 * * *"
            },
            custom_variables={
                "CUSTOM_VAR1": "value1",
                "CUSTOM_VAR2": "value2"
            }
        )
        
        # Export configuration
        writer = CfgWriter()
        writer.write_configuration(config, cfg_file, add_comments=False)
        
        # Import configuration back
        imported_config = Configuration.from_cfg_file(cfg_file)
        
        # Verify key fields match
        assert imported_config.secret_key_base == config.secret_key_base
        assert imported_config.rails_env == config.rails_env
        assert imported_config.proxy.domain == config.proxy.domain
        assert imported_config.proxy.ssl_enabled == config.proxy.ssl_enabled
        assert imported_config.database.adapter == config.database.adapter
        assert imported_config.database.host == config.database.host
        assert imported_config.email.smtp_address == config.email.smtp_address
        assert imported_config.storage.backup_enabled == config.storage.backup_enabled
        assert imported_config.custom_variables == config.custom_variables
    
    def test_configuration_validation_integration(self, sample_configuration):
        """Test configuration validation integration."""
        validator = ConfigurationValidator()
        
        # Test valid configuration
        results = validator.validate_configuration(sample_configuration)
        
        assert results["valid"] is True
        assert len(results["errors"]) == 0
        assert "checks" in results
        
        # Verify specific validation checks
        check_names = [check["name"] for check in results["checks"]]
        assert "Secret Key Validation" in check_names
        assert "Database Configuration" in check_names
        assert "Domain Configuration" in check_names
    
    def test_discovery_to_export_integration(self, temp_dir):
        """Test integration from discovery through export."""
        output_file = temp_dir / "discovery_integration.cfg"
        discovered_file = temp_dir / "discovered.json"
        
        # Create mock discovered data
        discovered_data = {
            "environment": {
                "DATABASE_HOST": "discovered.db.com",
                "DATABASE_PORT": "5432",
                "DATABASE_NAME": "discovered_db",
                "REDIS_URL": "redis://localhost:6379/0"
            },
            "system": {
                "hostname": "test-host",
                "os": "Linux",
                "memory_total": "8GB"
            },
            "docker": {
                "containers": [],
                "networks": []
            }
        }
        
        # Write discovered data to file
        discovered_file.write_text(json.dumps(discovered_data, indent=2), encoding='utf-8')
        
        # Mock interactive input to use discovered defaults
        with patch('openproject_config_manager.ui.console.UIConsole.prompt_text') as mock_text, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_choice') as mock_choice, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean') as mock_boolean:
            
            # Use discovered values (empty strings = use defaults)
            mock_text.side_effect = [
                "test-secret-key-1234567890123456789012345678901234567890123456789012",  # secret_key_base
                "production.example.com",  # domain
                "",  # database host (use discovered)
                "",  # database port (use discovered)
                "",  # database name (use discovered)
                "prod_user",  # database username
                "prod_password"  # database password
            ]
            
            mock_choice.side_effect = [
                "production",  # rails_env
                "postgresql"  # database adapter
            ]
            
            mock_boolean.return_value = False  # No optional sections
            
            # Create manager and run process
            manager = ConfigurationManager(output_file)
            
            # Mock discovery to return our test data
            with patch.object(manager, 'run_discovery_phase', return_value=discovered_data):
                result = manager.run_full_process(discovered_data)
            
            assert result is True
            assert output_file.exists()
            
            # Verify discovered values were used
            content = output_file.read_text(encoding='utf-8')
            assert 'DATABASE_HOST=discovered.db.com' in content
            assert 'DATABASE_PORT=5432' in content
            assert 'DATABASE_NAME=discovered_db' in content
    
    def test_configuration_update_integration(self, temp_dir):
        """Test configuration update integration."""
        original_file = temp_dir / "original.cfg"
        updated_file = temp_dir / "updated.cfg"
        
        # Create original configuration
        original_config = Configuration(
            secret_key_base="a" * 64,
            rails_env="development",
            proxy={"domain": "dev.example.com"},
            database={
                "adapter": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "openproject_dev",
                "username": "dev_user",
                "password": "dev_password"
            }
        )
        
        # Write original configuration
        writer = CfgWriter()
        writer.write_configuration(original_config, original_file, add_comments=False)
        
        # Create collector to simulate update process
        collector = InteractiveCollector()
        
        # Mock updated inputs
        with patch('openproject_config_manager.ui.console.UIConsole.prompt_text') as mock_text, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_choice') as mock_choice, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean') as mock_boolean:
            
            # Update some values, keep others
            mock_text.side_effect = [
                "",  # secret_key_base (keep existing)
                "prod.example.com",  # domain (update)
                "",  # database host (keep existing)
                "",  # database port (keep existing)
                "openproject_prod",  # database name (update)
                "",  # database username (keep existing)
                "new_secure_password"  # database password (update)
            ]
            
            mock_choice.side_effect = [
                "production",  # rails_env (update)
                "postgresql"  # database adapter (keep)
            ]
            
            mock_boolean.return_value = False  # No optional sections
            
            # Load existing configuration as discovered data
            existing_config = Configuration.from_cfg_file(original_file)
            discovered_data = {
                "environment": existing_config.to_cfg_format()
            }
            
            # Collect updated configuration
            updated_config = collector.collect_configuration(discovered_data)
            
            # Write updated configuration
            writer.write_configuration(updated_config, updated_file)
            
            # Verify updates
            updated_content = updated_file.read_text(encoding='utf-8')
            assert 'RAILS_ENV=production' in updated_content
            assert 'DOMAIN=prod.example.com' in updated_content
            assert 'DATABASE_NAME=openproject_prod' in updated_content
            assert 'DATABASE_PASSWORD=new_secure_password' in updated_content
            
            # Verify unchanged values
            assert 'DATABASE_HOST=localhost' in updated_content
            assert 'DATABASE_PORT=5432' in updated_content
    
    def test_error_handling_integration(self, temp_dir):
        """Test error handling throughout the process."""
        output_file = temp_dir / "error_test.cfg"
        
        # Test with invalid configuration
        with patch('openproject_config_manager.ui.console.UIConsole.prompt_text') as mock_text, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_choice') as mock_choice, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean') as mock_boolean:
            
            # Provide invalid secret key (too short)
            mock_text.side_effect = [
                "short-key",  # invalid secret_key_base
                "example.com",  # domain
                "localhost",  # database host
                "5432",  # database port
                "test_db",  # database name
                "user",  # database username
                "password"  # database password
            ]
            
            mock_choice.side_effect = [
                "production",  # rails_env
                "postgresql"  # database adapter
            ]
            
            mock_boolean.return_value = False
            
            # Create manager
            manager = ConfigurationManager(output_file)
            
            # Mock discovery
            with patch.object(manager, 'run_discovery_phase', return_value={}):
                # This should fail during validation
                result = manager.run_full_process({})
            
            # Should fail due to invalid configuration
            assert result is False
    
    def test_docker_compose_env_export_integration(self, sample_configuration, temp_dir):
        """Test Docker Compose .env export integration."""
        cfg_file = temp_dir / "test.cfg"
        env_file = temp_dir / "test.env"
        
        # Write configuration
        writer = CfgWriter()
        writer.write_configuration(sample_configuration, cfg_file)
        
        # Export to Docker Compose format
        writer.write_docker_compose_env(sample_configuration, env_file)
        
        # Verify .env file format
        env_content = env_file.read_text(encoding='utf-8')
        
        # Check that values are not quoted (Docker Compose format)
        lines = [line for line in env_content.split('\n') if '=' in line and not line.startswith('#')]
        
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                # Values should not be wrapped in quotes in .env format
                assert not (value.startswith('"') and value.endswith('"'))
        
        # Check specific values
        assert f'SECRET_KEY_BASE={sample_configuration.secret_key_base}' in env_content
        assert f'DOMAIN={sample_configuration.proxy.domain}' in env_content
        assert f'DATABASE_ADAPTER={sample_configuration.database.adapter}' in env_content
    
    def test_comprehensive_configuration_flow(self, temp_dir):
        """Test comprehensive configuration flow with all features."""
        output_file = temp_dir / "comprehensive.cfg"
        
        with patch('openproject_config_manager.ui.console.UIConsole.prompt_text') as mock_text, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_choice') as mock_choice, \
             patch('openproject_config_manager.ui.console.UIConsole.prompt_boolean') as mock_boolean:
            
            # Comprehensive configuration inputs
            mock_text.side_effect = [
                "comprehensive-secret-key-123456789012345678901234567890123456789012345",  # secret_key_base
                "comprehensive.example.com",  # domain
                "443",  # port
                "/ssl/cert.pem",  # ssl_cert_path
                "/ssl/key.pem",  # ssl_key_path
                "api.example.com,admin.example.com",  # additional_domains
                "db.example.com",  # database host
                "5432",  # database port
                "openproject_comp",  # database name
                "comp_user",  # database username
                "comp_secure_password",  # database password
                
                # Email settings
                "smtp.example.com",  # smtp_address
                "587",  # smtp_port
                "noreply@example.com",  # smtp_user_name
                "smtp_secret",  # smtp_password
                "system@example.com",  # from_email
                
                # Storage settings
                "/comprehensive/backups",  # backup_location
                "14",  # backup_retention_days
                "0 1 * * *",  # backup_schedule
                "us-east-1",  # s3_region
                "comp-backup-bucket",  # s3_bucket
                "AKIA...",  # s3_access_key_id
                "secret...",  # s3_secret_access_key
                
                # Performance settings
                "8",  # worker_processes
                "redis://redis.example.com:6379/0",  # redis_url
                "1024m",  # worker_memory_limit
                "60",  # worker_timeout
                
                # Security settings
                "60",  # session_timeout
                "3",  # login_attempt_limit
                "admin,superuser,manager",  # admin_users
                "example.com,*.example.com,api.example.com",  # allowed_hosts
                
                # Custom variables
                "COMP_VAR1=comprehensive1,COMP_VAR2=comprehensive2"
            ]
            
            mock_choice.side_effect = [
                "production",  # rails_env
                "postgresql",  # database adapter
                "smtp",  # email delivery_method
            ]
            
            # Enable all optional sections
            mock_boolean.side_effect = [
                True,  # ssl_enabled
                False,  # lets_encrypt
                True,  # additional_domains
                True,  # configure email
                True,  # configure storage
                True,  # backup_enabled
                True,  # configure S3
                True,  # configure performance
                True,  # configure security
                True,  # force_ssl
                True,  # configure custom variables
            ]
            
            # Run comprehensive configuration
            manager = ConfigurationManager(output_file)
            
            with patch.object(manager, 'run_discovery_phase', return_value={}):
                result = manager.run_full_process({})
            
            assert result is True
            assert output_file.exists()
            
            # Verify comprehensive configuration
            content = output_file.read_text(encoding='utf-8')
            
            # Core settings
            assert 'SECRET_KEY_BASE=' in content
            assert 'RAILS_ENV=production' in content
            assert 'DOMAIN=comprehensive.example.com' in content
            
            # SSL settings
            assert 'SSL_ENABLED=true' in content
            assert 'SSL_CERT_PATH=/ssl/cert.pem' in content
            
            # Database settings
            assert 'DATABASE_ADAPTER=postgresql' in content
            assert 'DATABASE_HOST=db.example.com' in content
            
            # Email settings
            assert 'SMTP_ADDRESS=smtp.example.com' in content
            assert 'FROM_EMAIL=system@example.com' in content
            
            # Storage settings
            assert 'BACKUP_ENABLED=true' in content
            assert 'BACKUP_LOCATION=/comprehensive/backups' in content
            assert 'S3_BUCKET=comp-backup-bucket' in content
            
            # Performance settings
            assert 'WORKER_PROCESSES=8' in content
            assert 'REDIS_URL=redis://redis.example.com:6379/0' in content
            
            # Security settings
            assert 'SESSION_TIMEOUT=60' in content
            assert 'FORCE_SSL=true' in content
            
            # Custom variables
            assert 'COMP_VAR1=comprehensive1' in content
            assert 'COMP_VAR2=comprehensive2' in content