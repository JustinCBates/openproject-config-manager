"""Tests for configuration manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from openproject_config_manager.core.manager import ConfigurationManager
from openproject_config_manager.core.config import Configuration


class TestConfigurationManager:
    """Test ConfigurationManager class."""
    
    def test_init_default(self):
        """Test manager initialization with defaults."""
        manager = ConfigurationManager()
        
        assert manager.project_root == Path.cwd()
        assert manager.config_file is None
        assert manager.verbose is False
        assert manager.configuration is None
        assert manager.discovered_data == {}
    
    def test_init_with_params(self, temp_dir):
        """Test manager initialization with parameters."""
        config_file = str(temp_dir / "config.cfg")
        
        manager = ConfigurationManager(
            project_root=str(temp_dir),
            config_file=config_file,
            verbose=True
        )
        
        assert manager.project_root == temp_dir
        assert manager.config_file == config_file
        assert manager.verbose is True
    
    @patch('openproject_config_manager.core.manager.EnvironmentDiscovery')
    @patch('openproject_config_manager.core.manager.SystemDiscovery')
    @patch('openproject_config_manager.core.manager.DockerDiscovery')
    def test_run_discovery_phase(self, mock_docker_discovery, mock_system_discovery, 
                                mock_env_discovery, mock_console_ui):
        """Test discovery phase execution."""
        # Setup mocks
        mock_env_discovery.return_value.discover.return_value = {'env': 'data'}
        mock_system_discovery.return_value.discover.return_value = {'system': 'data'}
        mock_docker_discovery.return_value.discover.return_value = {'docker': 'data'}
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        # Run discovery
        result = manager.run_discovery_phase()
        
        # Verify results
        assert 'environment' in result
        assert 'system' in result
        assert 'docker' in result
        assert 'existing_configs' in result
        
        # Verify UI calls
        mock_console_ui.show_phase_header.assert_called_with(
            "Discovery Phase", "Scanning environment and system..."
        )
        mock_console_ui.show_step.assert_called()
        mock_console_ui.show_success.assert_called()
    
    @patch('openproject_config_manager.core.manager.InteractiveCollector')
    def test_run_interactive_collection_phase(self, mock_collector, mock_console_ui, 
                                            sample_configuration, sample_discovered_data):
        """Test interactive collection phase."""
        # Setup mocks
        mock_collector.return_value.collect_configuration.return_value = sample_configuration
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        manager.discovered_data = sample_discovered_data
        
        # Run interactive collection
        result = manager.run_interactive_collection_phase()
        
        # Verify results
        assert result == sample_configuration
        assert manager.configuration == sample_configuration
        
        # Verify collector was called
        mock_collector.return_value.collect_configuration.assert_called_once()
    
    @patch('openproject_config_manager.core.manager.ConfigurationValidator')
    def test_run_validation_phase_success(self, mock_validator, mock_console_ui, 
                                        sample_configuration):
        """Test validation phase with successful validation."""
        # Setup mocks
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.errors = []
        mock_validation_result.warnings = []
        mock_validator.return_value.validate_configuration.return_value = mock_validation_result
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        manager.configuration = sample_configuration
        
        # Run validation
        result = manager.run_validation_phase()
        
        # Verify results
        assert result is True
        mock_console_ui.show_success.assert_called_with("Configuration validation passed")
    
    @patch('openproject_config_manager.core.manager.ConfigurationValidator')
    def test_run_validation_phase_failure(self, mock_validator, mock_console_ui, 
                                        sample_configuration):
        """Test validation phase with validation failure."""
        # Setup mocks
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["Error 1", "Error 2"]
        mock_validation_result.warnings = ["Warning 1"]
        mock_validator.return_value.validate_configuration.return_value = mock_validation_result
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        manager.configuration = sample_configuration
        
        # Run validation
        result = manager.run_validation_phase()
        
        # Verify results
        assert result is False
        mock_console_ui.show_error.assert_called()
    
    def test_run_validation_phase_no_config(self, mock_console_ui):
        """Test validation phase without configuration."""
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        with pytest.raises(ValueError, match="No configuration to validate"):
            manager.run_validation_phase()
    
    @patch('openproject_config_manager.core.manager.CfgWriter')
    def test_run_export_phase(self, mock_writer, mock_console_ui, 
                            sample_configuration, temp_dir):
        """Test export phase execution."""
        # Setup mocks
        output_path = str(temp_dir / "exported_config.cfg")
        mock_writer.return_value.write_configuration.return_value = output_path
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        manager.configuration = sample_configuration
        
        # Run export
        result = manager.run_export_phase()
        
        # Verify results
        assert result == output_path
        mock_writer.return_value.write_configuration.assert_called_once()
        mock_console_ui.show_success.assert_called()
    
    def test_run_export_phase_no_config(self, mock_console_ui):
        """Test export phase without configuration."""
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        with pytest.raises(ValueError, match="No configuration to export"):
            manager.run_export_phase()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_discovery_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_interactive_collection_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_validation_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_export_phase')
    def test_run_full_process_success(self, mock_export, mock_validation, 
                                    mock_collection, mock_discovery, mock_console_ui,
                                    sample_configuration, sample_discovered_data):
        """Test full process execution with success."""
        # Setup mocks
        mock_discovery.return_value = sample_discovered_data
        mock_collection.return_value = sample_configuration
        mock_validation.return_value = True
        mock_export.return_value = "config.cfg"
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        # Run full process
        result = manager.run_full_process()
        
        # Verify all phases were called
        mock_discovery.assert_called_once()
        mock_collection.assert_called_once()
        mock_validation.assert_called_once()
        mock_export.assert_called_once()
        
        assert result == "config.cfg"
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_discovery_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_interactive_collection_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_validation_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_export_phase')
    def test_run_full_process_validation_failure_continue(self, mock_export, mock_validation, 
                                                        mock_collection, mock_discovery, 
                                                        mock_console_ui, sample_configuration,
                                                        sample_discovered_data):
        """Test full process with validation failure but user continues."""
        # Setup mocks
        mock_discovery.return_value = sample_discovered_data
        mock_collection.return_value = sample_configuration
        mock_validation.return_value = False
        mock_export.return_value = "config.cfg"
        mock_console_ui.confirm.return_value = True  # User chooses to continue
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        # Run full process
        result = manager.run_full_process()
        
        # Verify export was still called
        mock_export.assert_called_once()
        assert result == "config.cfg"
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_discovery_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_interactive_collection_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_validation_phase')
    def test_run_full_process_validation_failure_abort(self, mock_validation, 
                                                     mock_collection, mock_discovery, 
                                                     mock_console_ui, sample_configuration,
                                                     sample_discovered_data):
        """Test full process with validation failure and user aborts."""
        # Setup mocks
        mock_discovery.return_value = sample_discovered_data
        mock_collection.return_value = sample_configuration
        mock_validation.return_value = False
        mock_console_ui.confirm.return_value = False  # User chooses to abort
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        # Run full process should raise exception
        with pytest.raises(ValueError, match="Configuration validation failed"):
            manager.run_full_process()
    
    @patch('openproject_config_manager.core.manager.Configuration.from_cfg_file')
    def test_load_existing_configuration(self, mock_from_cfg, mock_console_ui, 
                                       sample_configuration, temp_dir):
        """Test loading existing configuration."""
        # Setup mocks
        config_file = temp_dir / "config.cfg"
        mock_from_cfg.return_value = sample_configuration
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        # Load configuration
        result = manager.load_existing_configuration(str(config_file))
        
        # Verify results
        assert result == sample_configuration
        assert manager.configuration == sample_configuration
        mock_from_cfg.assert_called_once_with(str(config_file))
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_validation_phase')
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_export_phase')
    @patch('openproject_config_manager.core.manager.InteractiveCollector')
    def test_update_configuration_success(self, mock_collector, mock_export, 
                                        mock_validation, mock_console_ui, 
                                        sample_configuration):
        """Test configuration update with success."""
        # Setup mocks
        updated_config = sample_configuration
        updated_config.rails_env = "development"
        mock_collector.return_value.collect_configuration.return_value = updated_config
        mock_validation.return_value = True
        mock_export.return_value = "updated_config.cfg"
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        manager.configuration = sample_configuration
        
        # Update configuration
        result = manager.update_configuration()
        
        # Verify results
        assert result == "updated_config.cfg"
        assert manager.configuration == updated_config
    
    def test_update_configuration_no_existing(self, mock_console_ui):
        """Test update without existing configuration."""
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        with pytest.raises(ValueError, match="No configuration loaded"):
            manager.update_configuration()
    
    def test_find_existing_configs(self, temp_dir):
        """Test finding existing configuration files."""
        # Create test files
        (temp_dir / "test.cfg").touch()
        (temp_dir / "docker-compose.yml").touch()
        (temp_dir / ".env").touch()
        (temp_dir / "other.txt").touch()  # Should not be found
        
        manager = ConfigurationManager(project_root=str(temp_dir))
        
        found_files = manager._find_existing_configs()
        
        # Should find .cfg, .yml, and .env files
        assert len(found_files) >= 3
        assert any("test.cfg" in f for f in found_files)
        assert any("docker-compose.yml" in f for f in found_files)
        assert any(".env" in f for f in found_files)
        assert not any("other.txt" in f for f in found_files)
    
    def test_create_initial_config(self, sample_discovered_data):
        """Test creating initial configuration from discovered data."""
        manager = ConfigurationManager()
        manager.discovered_data = sample_discovered_data
        
        initial_config = manager._create_initial_config()
        
        # Should have basic structure
        assert initial_config.secret_key_base == ""  # Will be generated later
        assert initial_config.proxy.domain == "test-host.local"  # From discovered data
        assert initial_config.database.adapter == "postgresql"
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_discovery_phase')
    def test_keyboard_interrupt_handling(self, mock_discovery, mock_console_ui):
        """Test handling of keyboard interrupt."""
        mock_discovery.side_effect = KeyboardInterrupt()
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        with pytest.raises(SystemExit):
            manager.run_full_process()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager.run_discovery_phase')
    def test_exception_handling(self, mock_discovery, mock_console_ui):
        """Test handling of general exceptions."""
        mock_discovery.side_effect = Exception("Test error")
        
        manager = ConfigurationManager()
        manager.ui = mock_console_ui
        
        with pytest.raises(Exception, match="Test error"):
            manager.run_full_process()