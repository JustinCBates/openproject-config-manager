"""Tests for main CLI interface."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from click.testing import CliRunner

from openproject_config_manager.main import (
    cli, configure, update, validate, discover, export, version
)
from openproject_config_manager.core.config import Configuration


class TestMainCLI:
    """Test main CLI interface."""
    
    def test_cli_group(self):
        """Test CLI group is properly configured."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'OpenProject Configuration Manager' in result.output
        assert 'configure' in result.output
        assert 'update' in result.output
        assert 'validate' in result.output
        assert 'discover' in result.output
        assert 'export' in result.output
        assert 'version' in result.output
    
    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(version)
        
        assert result.exit_code == 0
        assert 'OpenProject Configuration Manager' in result.output
        assert 'version' in result.output.lower()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_default(self, mock_manager_class):
        """Test configure command with defaults."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.return_value = True
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(configure)
        
        assert result.exit_code == 0
        mock_manager.run_full_process.assert_called_once()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_with_output_file(self, mock_manager_class):
        """Test configure command with custom output file."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.return_value = True
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(configure, ['--output', 'custom.cfg'])
        
        assert result.exit_code == 0
        # Check that manager was initialized with custom output path
        mock_manager_class.assert_called_once()
        call_args = mock_manager_class.call_args
        assert 'custom.cfg' in str(call_args)
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_with_discovered_data(self, mock_manager_class):
        """Test configure command with discovered data file."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.return_value = True
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a mock discovered data file
            Path('discovered.json').write_text('{"environment": {}}')
            
            result = runner.invoke(configure, ['--discovered-data', 'discovered.json'])
        
        assert result.exit_code == 0
        mock_manager.run_full_process.assert_called_once()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_skip_discovery(self, mock_manager_class):
        """Test configure command with skip discovery option."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.return_value = True
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(configure, ['--skip-discovery'])
        
        assert result.exit_code == 0
        # Should still call run_full_process but with empty discovered data
        mock_manager.run_full_process.assert_called_once()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_failure(self, mock_manager_class):
        """Test configure command when process fails."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.return_value = False
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(configure)
        
        assert result.exit_code == 1
        assert 'Configuration process failed' in result.output
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_exception(self, mock_manager_class):
        """Test configure command when exception occurs."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.side_effect = Exception("Test error")
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(configure)
        
        assert result.exit_code == 1
        assert 'Error during configuration' in result.output
        assert 'Test error' in result.output
    
    @patch('openproject_config_manager.collector.interactive.InteractiveCollector')
    @patch('openproject_config_manager.export.cfg_writer.CfgWriter')
    def test_update_command_basic(self, mock_writer_class, mock_collector_class):
        """Test update command basic functionality."""
        # Setup mocks
        mock_collector = Mock()
        mock_collector_class.return_value = mock_collector
        mock_collector.collect_configuration.return_value = Mock(spec=Configuration)
        
        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer
        mock_writer.write_configuration.return_value = "output.cfg"
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create existing config file
            Path('existing.cfg').write_text('SECRET_KEY_BASE=old_key')
            
            result = runner.invoke(update, ['existing.cfg'])
        
        assert result.exit_code == 0
        mock_collector.collect_configuration.assert_called_once()
        mock_writer.write_configuration.assert_called_once()
    
    @patch('openproject_config_manager.collector.interactive.InteractiveCollector')
    def test_update_command_missing_file(self, mock_collector_class):
        """Test update command with missing configuration file."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(update, ['nonexistent.cfg'])
        
        assert result.exit_code == 1
        assert 'Configuration file not found' in result.output
    
    @patch('openproject_config_manager.validation.validator.ConfigurationValidator')
    def test_validate_command_basic(self, mock_validator_class):
        """Test validate command basic functionality."""
        # Setup mock
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_configuration.return_value = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create config file
            Path('test.cfg').write_text('SECRET_KEY_BASE=test_key')
            
            result = runner.invoke(validate, ['test.cfg'])
        
        assert result.exit_code == 0
        mock_validator.validate_configuration.assert_called_once()
    
    @patch('openproject_config_manager.validation.validator.ConfigurationValidator')
    def test_validate_command_invalid_config(self, mock_validator_class):
        """Test validate command with invalid configuration."""
        # Setup mock
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_configuration.return_value = {
            'valid': False,
            'errors': ['Error 1', 'Error 2'],
            'warnings': ['Warning 1']
        }
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create config file
            Path('test.cfg').write_text('SECRET_KEY_BASE=test_key')
            
            result = runner.invoke(validate, ['test.cfg'])
        
        assert result.exit_code == 1
        assert 'Configuration validation failed' in result.output
    
    @patch('openproject_config_manager.validation.validator.ConfigurationValidator')
    def test_validate_command_missing_file(self, mock_validator_class):
        """Test validate command with missing file."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(validate, ['nonexistent.cfg'])
        
        assert result.exit_code == 1
        assert 'Configuration file not found' in result.output
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_discover_command_basic(self, mock_manager_class):
        """Test discover command basic functionality."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_discovery_phase.return_value = {"environment": {}}
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(discover)
        
        assert result.exit_code == 0
        mock_manager.run_discovery_phase.assert_called_once()
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_discover_command_with_output(self, mock_manager_class):
        """Test discover command with output file."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_discovery_phase.return_value = {"environment": {}}
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(discover, ['--output', 'discovered.json'])
        
        assert result.exit_code == 0
        mock_manager.run_discovery_phase.assert_called_once()
        # Check that output file was created
        assert Path('discovered.json').exists()
    
    @patch('openproject_config_manager.export.cfg_writer.CfgWriter')
    def test_export_command_basic(self, mock_writer_class):
        """Test export command basic functionality."""
        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer
        mock_writer.write_configuration.return_value = "output.cfg"
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create input config file
            Path('input.cfg').write_text('SECRET_KEY_BASE=test_key')
            
            result = runner.invoke(export, ['input.cfg', 'output.cfg'])
        
        assert result.exit_code == 0
        mock_writer.write_configuration.assert_called_once()
    
    @patch('openproject_config_manager.export.cfg_writer.CfgWriter')
    def test_export_command_with_format(self, mock_writer_class):
        """Test export command with specific format."""
        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer
        mock_writer.write_docker_compose_env.return_value = "output.env"
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create input config file
            Path('input.cfg').write_text('SECRET_KEY_BASE=test_key')
            
            result = runner.invoke(export, ['input.cfg', 'output.env', '--format', 'env'])
        
        assert result.exit_code == 0
        mock_writer.write_docker_compose_env.assert_called_once()
    
    def test_export_command_missing_input(self):
        """Test export command with missing input file."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(export, ['nonexistent.cfg', 'output.cfg'])
        
        assert result.exit_code == 1
        assert 'Input configuration file not found' in result.output
    
    def test_export_command_invalid_format(self):
        """Test export command with invalid format."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create input config file
            Path('input.cfg').write_text('SECRET_KEY_BASE=test_key')
            
            result = runner.invoke(export, ['input.cfg', 'output.txt', '--format', 'invalid'])
        
        assert result.exit_code == 1
        assert 'Unsupported export format' in result.output
    
    @patch('json.load')
    def test_load_discovered_data_valid_json(self, mock_json_load):
        """Test loading valid discovered data."""
        mock_json_load.return_value = {"environment": {"TEST": "value"}}
        
        from openproject_config_manager.main import load_discovered_data
        
        with patch('builtins.open', mock_open_file):
            result = load_discovered_data("test.json")
        
        assert result == {"environment": {"TEST": "value"}}
        mock_json_load.assert_called_once()
    
    def test_load_discovered_data_missing_file(self):
        """Test loading missing discovered data file."""
        from openproject_config_manager.main import load_discovered_data
        
        result = load_discovered_data("nonexistent.json")
        assert result == {}
    
    @patch('json.load')
    def test_load_discovered_data_invalid_json(self, mock_json_load):
        """Test loading invalid JSON discovered data."""
        mock_json_load.side_effect = ValueError("Invalid JSON")
        
        from openproject_config_manager.main import load_discovered_data
        
        with patch('builtins.open', mock_open_file):
            result = load_discovered_data("invalid.json")
        
        assert result == {}
    
    def test_cli_integration_help(self):
        """Test CLI integration with help commands."""
        runner = CliRunner()
        
        # Test main help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        # Test subcommand help
        commands = ['configure', 'update', 'validate', 'discover', 'export', 'version']
        for cmd in commands:
            result = runner.invoke(cli, [cmd, '--help'])
            assert result.exit_code == 0, f"Help for {cmd} failed"
    
    @patch('openproject_config_manager.core.manager.ConfigurationManager')
    def test_configure_command_with_all_options(self, mock_manager_class):
        """Test configure command with all options."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.run_full_process.return_value = True
        
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create discovered data file
            Path('data.json').write_text('{"environment": {}}')
            
            result = runner.invoke(configure, [
                '--output', 'custom.cfg',
                '--discovered-data', 'data.json',
                '--skip-discovery',
                '--format', 'cfg'
            ])
        
        assert result.exit_code == 0
        mock_manager.run_full_process.assert_called_once()


def mock_open_file(*args, **kwargs):
    """Mock file opening."""
    return MagicMock()