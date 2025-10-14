"""Environment variable discovery and analysis."""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import re


logger = logging.getLogger(__name__)


class EnvironmentDiscovery:
    """Discovers and analyzes environment variables for OpenProject configuration."""
    
    # OpenProject-related environment variable patterns
    OPENPROJECT_PATTERNS = [
        r'^OPENPROJECT_.*',
        r'^OP_.*',
        r'^SECRET_KEY_BASE$',
        r'^RAILS_ENV$',
        r'^RAILS_.*',
        r'^DATABASE_.*',
        r'^DB_.*',
        r'^POSTGRES_.*',
        r'^MYSQL_.*',
        r'^SMTP_.*',
        r'^EMAIL_.*',
        r'^SSL_.*',
        r'^DOMAIN$',
        r'^HOST$',
        r'^PORT$',
        r'^.*_URL$',
        r'^.*_HOST$',
        r'^.*_PORT$',
        r'^.*_PASSWORD$',
        r'^.*_USER.*',
        r'^BACKUP_.*',
        r'^LOG_.*',
        r'^CACHE_.*',
        r'^REDIS_.*',
        r'^MEMCACHE.*',
    ]
    
    # Sensitive patterns that should be masked
    SENSITIVE_PATTERNS = [
        r'.*PASSWORD.*',
        r'.*SECRET.*',
        r'.*KEY.*',
        r'.*TOKEN.*',
        r'.*CREDENTIALS.*',
    ]
    
    def __init__(self):
        """Initialize environment discovery."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.OPENPROJECT_PATTERNS]
        self.sensitive_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SENSITIVE_PATTERNS]
    
    def discover(self) -> Dict[str, Any]:
        """
        Discover environment variables relevant to OpenProject configuration.
        
        Returns:
            Dictionary containing discovered environment data
        """
        logger.info("Starting environment variable discovery")
        
        env_data = {
            'relevant_vars': {},
            'all_vars_count': len(os.environ),
            'relevant_count': 0,
            'sensitive_count': 0,
            'docker_vars': {},
            'compose_vars': {},
            'dotenv_files': []
        }
        
        # Scan current environment variables
        relevant_vars = self._scan_environment_variables()
        env_data['relevant_vars'] = relevant_vars
        env_data['relevant_count'] = len(relevant_vars)
        
        # Count sensitive variables
        env_data['sensitive_count'] = sum(
            1 for var in relevant_vars.keys() 
            if self._is_sensitive_variable(var)
        )
        
        # Look for Docker environment files
        env_data['dotenv_files'] = self._find_dotenv_files()
        
        # Scan for Docker Compose environment variables
        env_data['compose_vars'] = self._scan_compose_environment()
        
        # Scan for Docker-specific variables
        env_data['docker_vars'] = self._scan_docker_environment()
        
        logger.info(f"Environment discovery completed: {env_data['relevant_count']} relevant variables found")
        
        return env_data
    
    def _scan_environment_variables(self) -> Dict[str, str]:
        """Scan current environment for OpenProject-related variables."""
        relevant_vars = {}
        
        for var_name, var_value in os.environ.items():
            if self._is_relevant_variable(var_name):
                # Mask sensitive values
                if self._is_sensitive_variable(var_name):
                    relevant_vars[var_name] = self._mask_sensitive_value(var_value)
                else:
                    relevant_vars[var_name] = var_value
        
        return relevant_vars
    
    def _is_relevant_variable(self, var_name: str) -> bool:
        """Check if a variable name matches OpenProject patterns."""
        return any(pattern.match(var_name) for pattern in self.compiled_patterns)
    
    def _is_sensitive_variable(self, var_name: str) -> bool:
        """Check if a variable contains sensitive information."""
        return any(pattern.match(var_name) for pattern in self.sensitive_patterns)
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive values for logging/display."""
        if not value:
            return ""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    
    def _find_dotenv_files(self) -> List[Dict[str, Any]]:
        """Find .env files in the current directory and subdirectories."""
        dotenv_files = []
        current_dir = Path.cwd()
        
        # Common .env file patterns
        env_patterns = [
            '.env',
            '.env.local',
            '.env.development',
            '.env.production',
            '.env.example',
            '*.env',
        ]
        
        for pattern in env_patterns:
            for env_file in current_dir.glob(pattern):
                if env_file.is_file():
                    try:
                        file_info = {
                            'path': str(env_file),
                            'size': env_file.stat().st_size,
                            'modified': env_file.stat().st_mtime,
                            'variables': self._parse_dotenv_file(env_file)
                        }
                        dotenv_files.append(file_info)
                    except Exception as e:
                        logger.warning(f"Failed to parse {env_file}: {e}")
        
        return dotenv_files
    
    def _parse_dotenv_file(self, file_path: Path) -> Dict[str, str]:
        """Parse a .env file and extract variables."""
        variables = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse variable assignment
                    if '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            # Only include if relevant
                            if self._is_relevant_variable(key):
                                if self._is_sensitive_variable(key):
                                    variables[key] = self._mask_sensitive_value(value)
                                else:
                                    variables[key] = value
                        except Exception as e:
                            logger.warning(f"Failed to parse line {line_num} in {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
        
        return variables
    
    def _scan_compose_environment(self) -> Dict[str, Any]:
        """Scan for Docker Compose environment configurations."""
        compose_vars = {
            'compose_files': [],
            'services': {},
            'networks': [],
            'volumes': []
        }
        
        current_dir = Path.cwd()
        
        # Look for Docker Compose files
        compose_patterns = [
            'docker-compose.yml',
            'docker-compose.yaml',
            'docker-compose.*.yml',
            'docker-compose.*.yaml',
            'compose.yml',
            'compose.yaml'
        ]
        
        for pattern in compose_patterns:
            for compose_file in current_dir.glob(pattern):
                if compose_file.is_file():
                    try:
                        file_info = {
                            'path': str(compose_file),
                            'size': compose_file.stat().st_size,
                            'services': self._extract_compose_services(compose_file)
                        }
                        compose_vars['compose_files'].append(file_info)
                    except Exception as e:
                        logger.warning(f"Failed to parse {compose_file}: {e}")
        
        return compose_vars
    
    def _extract_compose_services(self, compose_file: Path) -> List[str]:
        """Extract service names from Docker Compose file."""
        services = []
        
        try:
            import yaml
            
            with open(compose_file, 'r', encoding='utf-8') as f:
                compose_data = yaml.safe_load(f)
            
            if compose_data and 'services' in compose_data:
                services = list(compose_data['services'].keys())
        
        except ImportError:
            logger.warning("PyYAML not available, skipping Docker Compose parsing")
        except Exception as e:
            logger.warning(f"Failed to parse Docker Compose file {compose_file}: {e}")
        
        return services
    
    def _scan_docker_environment(self) -> Dict[str, Any]:
        """Scan for Docker-specific environment variables."""
        docker_vars = {}
        
        # Docker-related environment variables
        docker_env_vars = [
            'DOCKER_HOST',
            'DOCKER_CERT_PATH',
            'DOCKER_TLS_VERIFY',
            'DOCKER_API_VERSION',
            'DOCKER_CONFIG',
            'DOCKER_CONTENT_TRUST',
            'COMPOSE_PROJECT_NAME',
            'COMPOSE_FILE',
            'COMPOSE_HTTP_TIMEOUT',
            'COMPOSE_TLS_VERSION'
        ]
        
        for var in docker_env_vars:
            if var in os.environ:
                docker_vars[var] = os.environ[var]
        
        return docker_vars
    
    def get_suggested_values(self, variable_name: str) -> Optional[str]:
        """Get suggested value for a configuration variable based on discovered environment."""
        # Check current environment first
        if variable_name in os.environ:
            return os.environ[variable_name]
        
        # Check for common aliases
        aliases = {
            'SECRET_KEY_BASE': ['SECRET_KEY', 'RAILS_SECRET_KEY_BASE'],
            'DATABASE_PASSWORD': ['DB_PASSWORD', 'POSTGRES_PASSWORD', 'MYSQL_PASSWORD'],
            'DATABASE_HOST': ['DB_HOST', 'POSTGRES_HOST', 'MYSQL_HOST'],
            'DATABASE_PORT': ['DB_PORT', 'POSTGRES_PORT', 'MYSQL_PORT'],
            'DATABASE_NAME': ['DB_NAME', 'POSTGRES_DB', 'MYSQL_DATABASE'],
            'DATABASE_USERNAME': ['DB_USER', 'POSTGRES_USER', 'MYSQL_USER'],
        }
        
        if variable_name in aliases:
            for alias in aliases[variable_name]:
                if alias in os.environ:
                    return os.environ[alias]
        
        return None