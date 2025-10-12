"""Interactive configuration collection with rich UI."""

import logging
import secrets
import string
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.text import Text

from ..core.config import Configuration, DatabaseConfig, ProxyConfig, StorageConfig
from ..ui.console import ConsoleUI


logger = logging.getLogger(__name__)


class InteractiveCollector:
    """Interactive configuration collector using Rich UI."""
    
    def __init__(self, ui: Optional[ConsoleUI] = None):
        """
        Initialize the interactive collector.
        
        Args:
            ui: Optional ConsoleUI instance
        """
        self.ui = ui or ConsoleUI()
        self.console = Console()
        
    def collect_configuration(self, 
                            initial_config: Optional[Configuration] = None,
                            discovered_data: Optional[Dict[str, Any]] = None) -> Configuration:
        """
        Collect configuration interactively from the user.
        
        Args:
            initial_config: Optional existing configuration to update
            discovered_data: Data from discovery phase
            
        Returns:
            Complete Configuration object
        """
        self.ui.show_step("Starting interactive configuration collection...")
        
        discovered_data = discovered_data or {}
        
        # Initialize with existing config or create new
        if initial_config:
            config_data = initial_config.dict()
        else:
            config_data = self._get_default_config_data(discovered_data)
        
        # Core OpenProject settings
        config_data = self._collect_core_settings(config_data, discovered_data)
        
        # Database configuration
        config_data['database'] = self._collect_database_config(
            config_data.get('database', {}), discovered_data
        )
        
        # Proxy configuration
        config_data['proxy'] = self._collect_proxy_config(
            config_data.get('proxy', {}), discovered_data
        )
        
        # URL configuration
        config_data = self._collect_url_config(config_data, discovered_data)
        
        # Storage configuration
        config_data['storage'] = self._collect_storage_config(
            config_data.get('storage', {}), discovered_data
        )
        
        # Email configuration
        config_data = self._collect_email_config(config_data, discovered_data)
        
        # Performance settings
        config_data = self._collect_performance_config(config_data, discovered_data)
        
        # Security settings
        config_data = self._collect_security_config(config_data, discovered_data)
        
        # Feature settings
        config_data = self._collect_feature_config(config_data, discovered_data)
        
        # Custom variables
        config_data['custom_variables'] = self._collect_custom_variables(
            config_data.get('custom_variables', {})
        )
        
        # Create and return configuration
        try:
            configuration = Configuration(**config_data)
            self.ui.show_success("Configuration collection completed successfully")
            
            # Show summary
            self._show_configuration_summary(configuration)
            
            return configuration
            
        except Exception as e:
            logger.error(f"Failed to create configuration: {e}")
            self.ui.show_error(f"Configuration validation failed: {e}")
            raise
    
    def _get_default_config_data(self, discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get default configuration data based on discovered information."""
        # Extract recommendations from discovered data
        system_data = discovered_data.get('system', {})
        docker_data = discovered_data.get('docker', {})
        
        # Get system recommendations
        system_recommendations = system_data.get('recommendations', {})
        docker_recommendations = docker_data.get('recommendations', {})
        
        # Default domain from system hostname
        default_domain = (
            system_recommendations.get('network', {}).get('suggested_domain') or
            docker_recommendations.get('networking', {}).get('suggested_domain') or
            'openproject.local'
        )
        
        return {
            'secret_key_base': '',
            'rails_env': 'production',
            'rails_cache_store': 'memcache',
            'uri_namespace_enabled': False,
            'uri_namespace': '',
            'database': {
                'adapter': 'postgresql',
                'host': 'db',
                'port': 5432,
                'name': 'openproject',
                'username': 'openproject',
                'password': '',
                'encoding': 'utf8'
            },
            'proxy': {
                'domain': default_domain,
                'additional_domains': [],
                'ssl_enabled': True,
                'lets_encrypt': True,
                'reverse_proxy_enabled': True
            },
            'storage': {
                'data_volume': 'openproject_data',
                'logs_volume': 'openproject_logs',
                'backup_enabled': True,
                'backup_schedule': '0 2 * * *',
                'backup_retention_days': 30,
                'backup_location': './backups'
            }
        }
    
    def _collect_core_settings(self, config_data: Dict[str, Any], 
                             discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect core OpenProject settings."""
        self.ui.show_section_header("Core OpenProject Settings")
        
        # Secret key base
        if not config_data.get('secret_key_base'):
            self.ui.show_info("Generating secure secret key...")
            config_data['secret_key_base'] = self._generate_secret_key()
            self.ui.show_success("Secret key generated")
        else:
            if self.ui.confirm("Regenerate secret key? (Warning: This will invalidate existing sessions)"):
                config_data['secret_key_base'] = self._generate_secret_key()
                self.ui.show_success("New secret key generated")
        
        # Rails environment
        rails_env_choices = ['production', 'development']
        config_data['rails_env'] = self.ui.select(
            "Select Rails environment",
            choices=rails_env_choices,
            default=config_data.get('rails_env', 'production')
        )
        
        # Cache store
        cache_choices = ['memcache', 'redis', 'file_store']
        config_data['rails_cache_store'] = self.ui.select(
            "Select cache store",
            choices=cache_choices,
            default=config_data.get('rails_cache_store', 'memcache')
        )
        
        return config_data
    
    def _collect_database_config(self, db_config: Dict[str, Any], 
                               discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect database configuration."""
        self.ui.show_section_header("Database Configuration")
        
        # Check for existing database containers
        docker_data = discovered_data.get('docker', {})
        db_containers = docker_data.get('database_containers', [])
        db_recommendations = docker_data.get('recommendations', {}).get('database', {})
        
        if db_containers:
            self.ui.show_info(f"Found {len(db_containers)} existing database container(s)")
            for container in db_containers:
                self.ui.show_info(f"  - {container['name']} ({container.get('database_type', 'unknown')})")
        
        # Database adapter
        adapter_choices = ['postgresql', 'mysql']
        suggested_adapter = db_recommendations.get('suggested_adapter', db_config.get('adapter', 'postgresql'))
        
        db_config['adapter'] = self.ui.select(
            "Select database adapter",
            choices=adapter_choices,
            default=suggested_adapter
        )
        
        # Database host
        suggested_host = db_recommendations.get('suggested_host', db_config.get('host', 'db'))
        db_config['host'] = self.ui.prompt(
            "Database host",
            default=suggested_host
        )
        
        # Database port
        default_port = 5432 if db_config['adapter'] == 'postgresql' else 3306
        db_config['port'] = self.ui.prompt_int(
            "Database port",
            default=db_config.get('port', default_port),
            min_value=1,
            max_value=65535
        )
        
        # Database name
        db_config['name'] = self.ui.prompt(
            "Database name",
            default=db_config.get('name', 'openproject')
        )
        
        # Database username
        db_config['username'] = self.ui.prompt(
            "Database username",
            default=db_config.get('username', 'openproject')
        )
        
        # Database password
        if not db_config.get('password'):
            self.ui.show_info("Generating secure database password...")
            db_config['password'] = self._generate_password()
            self.ui.show_success("Database password generated")
        else:
            if self.ui.confirm("Generate new database password?"):
                db_config['password'] = self._generate_password()
                self.ui.show_success("New database password generated")
        
        # Database encoding
        db_config['encoding'] = self.ui.prompt(
            "Database encoding",
            default=db_config.get('encoding', 'utf8')
        )
        
        return db_config
    
    def _collect_proxy_config(self, proxy_config: Dict[str, Any], 
                            discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect proxy and SSL configuration."""
        self.ui.show_section_header("Proxy & SSL Configuration")
        
        # Get system recommendations
        system_data = discovered_data.get('system', {})
        network_recommendations = system_data.get('recommendations', {}).get('network', {})
        
        # Primary domain
        suggested_domain = network_recommendations.get('suggested_domain', proxy_config.get('domain', 'openproject.local'))
        proxy_config['domain'] = self.ui.prompt(
            "Primary domain",
            default=suggested_domain
        )
        
        # Additional domains
        if self.ui.confirm("Add additional domains?"):
            additional_domains = []
            while True:
                domain = self.ui.prompt("Additional domain (empty to finish)", allow_empty=True)
                if not domain:
                    break
                additional_domains.append(domain)
            proxy_config['additional_domains'] = additional_domains
        else:
            proxy_config['additional_domains'] = proxy_config.get('additional_domains', [])
        
        # SSL configuration
        proxy_config['ssl_enabled'] = self.ui.confirm(
            "Enable SSL/TLS?",
            default=proxy_config.get('ssl_enabled', True)
        )
        
        if proxy_config['ssl_enabled']:
            # Let's Encrypt vs Custom certificates
            proxy_config['lets_encrypt'] = self.ui.confirm(
                "Use Let's Encrypt for SSL certificates?",
                default=proxy_config.get('lets_encrypt', True)
            )
            
            if proxy_config['lets_encrypt']:
                proxy_config['lets_encrypt_email'] = self.ui.prompt(
                    "Email for Let's Encrypt notifications",
                    default=proxy_config.get('lets_encrypt_email', '')
                )
            else:
                # Custom SSL certificates
                proxy_config['ssl_cert_path'] = self.ui.prompt(
                    "Path to SSL certificate file",
                    default=proxy_config.get('ssl_cert_path', '')
                )
                proxy_config['ssl_key_path'] = self.ui.prompt(
                    "Path to SSL private key file",
                    default=proxy_config.get('ssl_key_path', '')
                )
        
        # Reverse proxy
        proxy_config['reverse_proxy_enabled'] = self.ui.confirm(
            "Enable reverse proxy?",
            default=proxy_config.get('reverse_proxy_enabled', True)
        )
        
        return proxy_config
    
    def _collect_url_config(self, config_data: Dict[str, Any], 
                           discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect URL and namespace configuration."""
        self.ui.show_section_header("URL Configuration")
        
        # Show helpful information
        self.ui.show_info("Configure how OpenProject URLs will be structured")
        
        # URI namespace enabled
        uri_namespace_enabled = self.ui.confirm(
            "Enable URI namespacing?\n"
            "  This allows you to host OpenProject at a subpath like '/projects' or '/openproject'",
            default=config_data.get('uri_namespace_enabled', False)
        )
        
        config_data['uri_namespace_enabled'] = uri_namespace_enabled
        
        if uri_namespace_enabled:
            # Show examples to help users understand
            self.ui.show_info("Examples of URI namespaces:")
            self.ui.show_info("  • '/openproject' → https://example.com/openproject")
            self.ui.show_info("  • '/projects' → https://example.com/projects") 
            self.ui.show_info("  • '/mycompany' → https://example.com/mycompany")
            self.ui.show_info("  • '/StatesmenProjects' → https://example.com/StatesmenProjects")
            
            # Get the namespace path
            current_namespace = config_data.get('uri_namespace', '')
            if current_namespace and not current_namespace.startswith('/'):
                current_namespace = f"/{current_namespace}"
                
            uri_namespace = self.ui.prompt(
                "URI namespace path (should start with '/'):\n"
                "  Enter the path where OpenProject will be accessible",
                default=current_namespace or '/openproject'
            )
            
            # Validate and clean the namespace
            if not uri_namespace.startswith('/'):
                uri_namespace = f"/{uri_namespace}"
            
            # Remove trailing slash if present
            if uri_namespace.endswith('/') and len(uri_namespace) > 1:
                uri_namespace = uri_namespace.rstrip('/')
                
            config_data['uri_namespace'] = uri_namespace
            
            # Show confirmation
            proxy_domain = config_data.get('proxy', {}).get('domain', 'example.com')
            self.ui.show_success(f"OpenProject will be accessible at: https://{proxy_domain}{uri_namespace}")
            
        else:
            # If namespace is disabled, ensure it's not set
            config_data['uri_namespace'] = ''
            proxy_domain = config_data.get('proxy', {}).get('domain', 'example.com')
            self.ui.show_info(f"OpenProject will be accessible at the root: https://{proxy_domain}")
        
        return config_data
    
    def _collect_storage_config(self, storage_config: Dict[str, Any], 
                              discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect storage and backup configuration."""
        self.ui.show_section_header("Storage & Backup Configuration")
        
        # Get storage recommendations
        system_data = discovered_data.get('system', {})
        storage_recommendations = system_data.get('recommendations', {}).get('storage', {})
        
        # Data volume
        storage_config['data_volume'] = self.ui.prompt(
            "Data volume name",
            default=storage_config.get('data_volume', 'openproject_data')
        )
        
        # Logs volume
        storage_config['logs_volume'] = self.ui.prompt(
            "Logs volume name",
            default=storage_config.get('logs_volume', 'openproject_logs')
        )
        
        # Backup configuration
        storage_config['backup_enabled'] = self.ui.confirm(
            "Enable automated backups?",
            default=storage_config.get('backup_enabled', True)
        )
        
        if storage_config['backup_enabled']:
            # Backup schedule
            storage_config['backup_schedule'] = self.ui.prompt(
                "Backup schedule (cron format)",
                default=storage_config.get('backup_schedule', '0 2 * * *')
            )
            
            # Backup retention
            storage_config['backup_retention_days'] = self.ui.prompt_int(
                "Backup retention (days)",
                default=storage_config.get('backup_retention_days', 30),
                min_value=1,
                max_value=365
            )
            
            # Backup location
            suggested_location = storage_recommendations.get('backup_location', storage_config.get('backup_location', './backups'))
            storage_config['backup_location'] = self.ui.prompt(
                "Backup location",
                default=suggested_location
            )
        
        return storage_config
    
    def _collect_email_config(self, config_data: Dict[str, Any], 
                            discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect email configuration."""
        self.ui.show_section_header("Email Configuration")
        
        # Email delivery method
        delivery_methods = ['smtp', 'sendmail', 'letter_opener']
        config_data['email_delivery_method'] = self.ui.select(
            "Email delivery method",
            choices=delivery_methods,
            default=config_data.get('email_delivery_method', 'smtp')
        )
        
        if config_data['email_delivery_method'] == 'smtp':
            # SMTP configuration
            config_data['smtp_address'] = self.ui.prompt(
                "SMTP server address",
                default=config_data.get('smtp_address', '')
            )
            
            config_data['smtp_port'] = self.ui.prompt_int(
                "SMTP port",
                default=config_data.get('smtp_port', 587),
                min_value=1,
                max_value=65535
            )
            
            config_data['smtp_domain'] = self.ui.prompt(
                "SMTP domain",
                default=config_data.get('smtp_domain', ''),
                allow_empty=True
            )
            
            config_data['smtp_user_name'] = self.ui.prompt(
                "SMTP username",
                default=config_data.get('smtp_user_name', ''),
                allow_empty=True
            )
            
            if self.ui.confirm("Set SMTP password?"):
                config_data['smtp_password'] = self.ui.prompt_password("SMTP password")
            
            config_data['smtp_enable_starttls_auto'] = self.ui.confirm(
                "Enable STARTTLS?",
                default=config_data.get('smtp_enable_starttls_auto', True)
            )
        
        return config_data
    
    def _collect_performance_config(self, config_data: Dict[str, Any], 
                                  discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect performance configuration."""
        self.ui.show_section_header("Performance Settings")
        
        # Get performance recommendations
        system_data = discovered_data.get('system', {})
        perf_recommendations = system_data.get('recommendations', {}).get('performance', {})
        
        # Web concurrency
        suggested_concurrency = perf_recommendations.get('web_concurrency', config_data.get('web_concurrency', 2))
        config_data['web_concurrency'] = self.ui.prompt_int(
            "Web worker processes",
            default=suggested_concurrency,
            min_value=1,
            max_value=16
        )
        
        # Web timeout
        config_data['web_timeout'] = self.ui.prompt_int(
            "Web request timeout (seconds)",
            default=config_data.get('web_timeout', 60),
            min_value=30,
            max_value=300
        )
        
        # Max requests per worker
        config_data['web_max_requests'] = self.ui.prompt_int(
            "Max requests per worker",
            default=config_data.get('web_max_requests', 1000),
            min_value=100,
            max_value=10000
        )
        
        # Cache configuration
        if config_data.get('rails_cache_store') == 'memcache':
            config_data['memcached_server'] = self.ui.prompt(
                "Memcached server",
                default=config_data.get('memcached_server', 'cache:11211')
            )
        elif config_data.get('rails_cache_store') == 'redis':
            config_data['redis_url'] = self.ui.prompt(
                "Redis URL",
                default=config_data.get('redis_url', 'redis://redis:6379/0')
            )
        
        return config_data
    
    def _collect_security_config(self, config_data: Dict[str, Any], 
                               discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect security configuration."""
        self.ui.show_section_header("Security Settings")
        
        # Force SSL
        config_data['force_ssl'] = self.ui.confirm(
            "Force SSL/HTTPS?",
            default=config_data.get('force_ssl', True)
        )
        
        # Session cookie security
        config_data['session_cookie_secure'] = self.ui.confirm(
            "Secure session cookies?",
            default=config_data.get('session_cookie_secure', True)
        )
        
        return config_data
    
    def _collect_feature_config(self, config_data: Dict[str, Any], 
                              discovered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect feature configuration."""
        self.ui.show_section_header("Feature Settings")
        
        # Attachments storage
        storage_choices = ['file', 'fog']
        config_data['attachments_storage'] = self.ui.select(
            "Attachments storage backend",
            choices=storage_choices,
            default=config_data.get('attachments_storage', 'file')
        )
        
        if config_data['attachments_storage'] == 'fog':
            self.ui.show_info("Fog (cloud storage) configuration will need to be set up separately")
        
        # Log level
        log_levels = ['debug', 'info', 'warn', 'error']
        config_data['log_level'] = self.ui.select(
            "Log level",
            choices=log_levels,
            default=config_data.get('log_level', 'info')
        )
        
        # Rails logging
        config_data['rails_log_to_stdout'] = self.ui.confirm(
            "Log to stdout?",
            default=config_data.get('rails_log_to_stdout', True)
        )
        
        return config_data
    
    def _collect_custom_variables(self, custom_vars: Dict[str, str]) -> Dict[str, str]:
        """Collect custom environment variables."""
        self.ui.show_section_header("Custom Variables")
        
        if not self.ui.confirm("Add custom environment variables?"):
            return custom_vars
        
        new_vars = custom_vars.copy()
        
        while True:
            var_name = self.ui.prompt("Variable name (empty to finish)", allow_empty=True)
            if not var_name:
                break
            
            var_value = self.ui.prompt(f"Value for {var_name}")
            new_vars[var_name.upper()] = var_value
        
        return new_vars
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        # Generate 128-character hex string (64 bytes)
        return secrets.token_hex(64)
    
    def _generate_password(self, length: int = 32) -> str:
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _show_configuration_summary(self, configuration: Configuration):
        """Show a summary of the collected configuration."""
        self.ui.show_section_header("Configuration Summary")
        
        summary_table = Table(title="Configuration Overview", show_header=True, header_style="bold magenta")
        summary_table.add_column("Category", style="cyan", width=20)
        summary_table.add_column("Key Settings", style="white", width=60)
        
        # Core settings
        core_settings = [
            f"Environment: {configuration.rails_env}",
            f"Cache Store: {configuration.rails_cache_store}",
            f"Secret Key: {'Set' if configuration.secret_key_base else 'Not Set'}"
        ]
        summary_table.add_row("Core", "\\n".join(core_settings))
        
        # Database settings
        db_settings = [
            f"Adapter: {configuration.database.adapter}",
            f"Host: {configuration.database.host}:{configuration.database.port}",
            f"Database: {configuration.database.name}",
            f"User: {configuration.database.username}"
        ]
        summary_table.add_row("Database", "\\n".join(db_settings))
        
        # Proxy settings
        proxy_settings = [
            f"Domain: {configuration.proxy.domain}",
            f"SSL: {'Enabled' if configuration.proxy.ssl_enabled else 'Disabled'}",
            f"Let's Encrypt: {'Yes' if configuration.proxy.lets_encrypt else 'No'}"
        ]
        if configuration.proxy.additional_domains:
            proxy_settings.append(f"Additional Domains: {len(configuration.proxy.additional_domains)}")
        summary_table.add_row("Proxy", "\\n".join(proxy_settings))
        
        # URL settings
        url_settings = []
        uri_namespace_enabled = getattr(configuration, 'uri_namespace_enabled', False)
        uri_namespace = getattr(configuration, 'uri_namespace', '')
        
        if uri_namespace_enabled and uri_namespace:
            url_settings.append(f"Namespace: Enabled ({uri_namespace})")
            url_settings.append(f"Access URL: https://{configuration.proxy.domain}{uri_namespace}")
        else:
            url_settings.append("Namespace: Disabled")
            url_settings.append(f"Access URL: https://{configuration.proxy.domain}")
            
        summary_table.add_row("URL", "\\n".join(url_settings))
        
        # Storage settings
        storage_settings = [
            f"Data Volume: {configuration.storage.data_volume}",
            f"Backup: {'Enabled' if configuration.storage.backup_enabled else 'Disabled'}"
        ]
        if configuration.storage.backup_enabled:
            storage_settings.append(f"Retention: {configuration.storage.backup_retention_days} days")
        summary_table.add_row("Storage", "\\n".join(storage_settings))
        
        # Performance settings
        perf_settings = [
            f"Web Workers: {configuration.web_concurrency}",
            f"Timeout: {configuration.web_timeout}s",
            f"Max Requests: {configuration.web_max_requests}"
        ]
        summary_table.add_row("Performance", "\\n".join(perf_settings))
        
        self.console.print(summary_table)
        
        # Show any warnings
        warnings = []
        if not configuration.proxy.ssl_enabled:
            warnings.append("SSL is disabled - not recommended for production")
        if configuration.rails_env == 'development':
            warnings.append("Development environment selected")
        if configuration.web_concurrency == 1:
            warnings.append("Single web worker - may impact performance")
        
        if warnings:
            self.ui.show_warning("Configuration Warnings:")
            for warning in warnings:
                self.ui.show_warning(f"  - {warning}")
        
        self.ui.show_success("Configuration summary complete")