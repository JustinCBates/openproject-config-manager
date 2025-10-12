"""Tests for environment discovery."""

import pytest
import os
from unittest.mock import patch, mock_open, Mock
from pathlib import Path

from openproject_config_manager.discovery.environment import EnvironmentDiscovery


class TestEnvironmentDiscovery:
    """Test EnvironmentDiscovery class."""
    
    def test_init(self):
        """Test environment discovery initialization."""
        discovery = EnvironmentDiscovery()
        
        assert len(discovery.compiled_patterns) > 0
        assert len(discovery.sensitive_patterns) > 0
    
    @patch.dict(os.environ, {
        'OPENPROJECT_SECRET': 'secret_value',
        'SECRET_KEY_BASE': 'base_secret',
        'DATABASE_HOST': 'localhost',
        'SMTP_PASSWORD': 'smtp_pass',
        'UNRELATED_VAR': 'unrelated'
    })
    def test_discover(self):
        """Test environment discovery process."""
        discovery = EnvironmentDiscovery()
        
        result = discovery.discover()
        
        # Check structure
        assert 'relevant_vars' in result
        assert 'all_vars_count' in result
        assert 'relevant_count' in result
        assert 'sensitive_count' in result
        assert 'docker_vars' in result
        assert 'compose_vars' in result
        assert 'dotenv_files' in result
        
        # Check relevant variables were found
        relevant_vars = result['relevant_vars']
        assert 'OPENPROJECT_SECRET' in relevant_vars
        assert 'SECRET_KEY_BASE' in relevant_vars
        assert 'DATABASE_HOST' in relevant_vars
        assert 'SMTP_PASSWORD' in relevant_vars
        assert 'UNRELATED_VAR' not in relevant_vars
        
        # Check sensitive variables are masked
        assert '*' in relevant_vars['OPENPROJECT_SECRET']
        assert '*' in relevant_vars['SMTP_PASSWORD']
        
        # Check counts
        assert result['relevant_count'] == 4
        assert result['sensitive_count'] == 2
    
    def test_is_relevant_variable(self):
        """Test relevant variable detection."""
        discovery = EnvironmentDiscovery()
        
        # Relevant variables
        relevant_vars = [
            'OPENPROJECT_SECRET',
            'SECRET_KEY_BASE',
            'DATABASE_HOST',
            'DB_PASSWORD',
            'RAILS_ENV',
            'SMTP_ADDRESS',
            'SSL_CERT'
        ]
        
        for var in relevant_vars:
            assert discovery._is_relevant_variable(var) is True
        
        # Non-relevant variables
        non_relevant_vars = [
            'PATH',
            'HOME',
            'USER',
            'SHELL',
            'RANDOM_VAR'
        ]
        
        for var in non_relevant_vars:
            assert discovery._is_relevant_variable(var) is False
    
    def test_is_sensitive_variable(self):
        """Test sensitive variable detection."""
        discovery = EnvironmentDiscovery()
        
        # Sensitive variables
        sensitive_vars = [
            'SECRET_KEY_BASE',
            'DATABASE_PASSWORD',
            'SMTP_PASSWORD',
            'SSL_PRIVATE_KEY',
            'AUTH_TOKEN',
            'API_CREDENTIALS'
        ]
        
        for var in sensitive_vars:
            assert discovery._is_sensitive_variable(var) is True
        
        # Non-sensitive variables
        non_sensitive_vars = [
            'DATABASE_HOST',
            'SMTP_ADDRESS',
            'LOG_LEVEL',
            'RAILS_ENV'
        ]
        
        for var in non_sensitive_vars:
            assert discovery._is_sensitive_variable(var) is False
    
    def test_mask_sensitive_value(self):
        """Test sensitive value masking."""
        discovery = EnvironmentDiscovery()
        
        # Test various value lengths
        test_cases = [
            ("", ""),
            ("a", "*"),
            ("ab", "**"),
            ("abc", "***"),
            ("abcd", "****"),
            ("abcde", "ab*de"),
            ("very_long_password", "ve*********rd"),
        ]
        
        for input_val, expected in test_cases:
            result = discovery._mask_sensitive_value(input_val)
            assert result == expected
    
    @patch('builtins.open', new_callable=mock_open, read_data='''
# Example .env file
SECRET_KEY_BASE="test_secret_key"
DATABASE_HOST=localhost
DATABASE_PASSWORD="test_password"
# Comment line
INVALID_LINE_WITHOUT_EQUALS

QUOTED_VALUE="quoted value"
UNQUOTED_VALUE=unquoted
''')
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    def test_find_dotenv_files(self, mock_stat, mock_is_file, mock_glob, mock_file):
        """Test finding and parsing .env files."""
        # Setup mocks
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat_result.st_mtime = 1234567890
        mock_stat.return_value = mock_stat_result
        
        mock_is_file.return_value = True
        mock_glob.return_value = [Path('.env')]
        
        discovery = EnvironmentDiscovery()
        
        result = discovery._find_dotenv_files()
        
        assert len(result) == 1
        env_file = result[0]
        
        assert env_file['path'] == '.env'
        assert env_file['size'] == 1024
        assert 'variables' in env_file
        
        # Check parsed variables
        variables = env_file['variables']
        assert 'SECRET_KEY_BASE' in variables
        assert 'DATABASE_HOST' in variables
        assert 'DATABASE_PASSWORD' in variables
        assert 'QUOTED_VALUE' in variables
        assert 'UNQUOTED_VALUE' in variables
        
        # Check that sensitive values are masked
        assert '*' in variables['SECRET_KEY_BASE']
        assert '*' in variables['DATABASE_PASSWORD']
        
        # Check that non-sensitive values are not masked
        assert variables['DATABASE_HOST'] == 'localhost'
    
    @patch('builtins.open', new_callable=mock_open, read_data='''
version: '3.8'
services:
  app:
    image: openproject:latest
  db:
    image: postgres:13
  redis:
    image: redis:6
''')
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.is_file')
    @patch('openproject_config_manager.discovery.environment.yaml')
    def test_scan_compose_environment(self, mock_yaml, mock_is_file, mock_glob, mock_file):
        """Test scanning Docker Compose environment."""
        # Setup mocks
        mock_is_file.return_value = True
        mock_glob.return_value = [Path('docker-compose.yml')]
        
        mock_yaml.safe_load.return_value = {
            'services': {
                'app': {'image': 'openproject:latest'},
                'db': {'image': 'postgres:13'},
                'redis': {'image': 'redis:6'}
            }
        }
        
        discovery = EnvironmentDiscovery()
        
        result = discovery._scan_compose_environment()
        
        assert 'compose_files' in result
        assert len(result['compose_files']) == 1
        
        compose_file = result['compose_files'][0]
        assert compose_file['path'] == 'docker-compose.yml'
        assert 'services' in compose_file
        assert set(compose_file['services']) == {'app', 'db', 'redis'}
    
    @patch.dict(os.environ, {
        'DOCKER_HOST': 'tcp://localhost:2376',
        'DOCKER_TLS_VERIFY': '1',
        'COMPOSE_PROJECT_NAME': 'openproject'
    })
    def test_scan_docker_environment(self):
        """Test scanning Docker environment variables."""
        discovery = EnvironmentDiscovery()
        
        result = discovery._scan_docker_environment()
        
        assert 'DOCKER_HOST' in result
        assert 'DOCKER_TLS_VERIFY' in result
        assert 'COMPOSE_PROJECT_NAME' in result
        assert result['DOCKER_HOST'] == 'tcp://localhost:2376'
        assert result['COMPOSE_PROJECT_NAME'] == 'openproject'
    
    def test_get_suggested_values(self):
        """Test getting suggested values for variables."""
        discovery = EnvironmentDiscovery()
        
        # Test direct environment variable
        with patch.dict(os.environ, {'SECRET_KEY_BASE': 'direct_value'}):
            result = discovery.get_suggested_values('SECRET_KEY_BASE')
            assert result == 'direct_value'
        
        # Test alias mapping
        with patch.dict(os.environ, {'DB_PASSWORD': 'alias_value'}):
            result = discovery.get_suggested_values('DATABASE_PASSWORD')
            assert result == 'alias_value'
        
        # Test no suggestion available
        with patch.dict(os.environ, {}, clear=True):
            result = discovery.get_suggested_values('UNKNOWN_VAR')
            assert result is None
    
    def test_parse_dotenv_file_edge_cases(self, temp_dir):
        """Test .env file parsing with edge cases."""
        # Create test .env file with various formats
        env_content = '''
# Comment line
  # Indented comment

SIMPLE_VAR=simple_value
QUOTED_VAR="quoted value"
SINGLE_QUOTED='single quoted'
EMPTY_VAR=
WHITESPACE_VAR=  value with spaces  

MULTILINE_VAR="line1
line2"

EQUALS_IN_VALUE=key=value=more
NO_EQUALS_LINE_SHOULD_BE_IGNORED

# Sensitive variable for testing
SECRET_KEY="secret_value"
'''
        
        env_file = temp_dir / '.env'
        env_file.write_text(env_content, encoding='utf-8')
        
        discovery = EnvironmentDiscovery()
        variables = discovery._parse_dotenv_file(env_file)
        
        # Check parsed variables
        assert variables['SIMPLE_VAR'] == 'simple_value'
        assert variables['QUOTED_VAR'] == 'quoted value'
        assert variables['SINGLE_QUOTED'] == 'single quoted'
        assert variables['EMPTY_VAR'] == ''
        assert variables['WHITESPACE_VAR'] == 'value with spaces'
        assert variables['EQUALS_IN_VALUE'] == 'key=value=more'
        
        # Check sensitive masking
        assert '*' in variables['SECRET_KEY']
        
        # Check that invalid lines are ignored
        assert len([k for k in variables.keys() if 'NO_EQUALS' in k]) == 0