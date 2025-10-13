"""Core configuration manager implementation."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Add TUI Form Engine to Python path for development environment
_tui_engine_path = Path(__file__).parent.parent.parent.parent.parent / "tui-form-designer" / "src"
if _tui_engine_path.exists() and str(_tui_engine_path) not in sys.path:
    sys.path.insert(0, str(_tui_engine_path))

from ..core.config import Configuration
from ..discovery.environment import EnvironmentDiscovery
from ..discovery.system import SystemDiscovery
from ..discovery.docker import DockerDiscovery
from ..discovery.network import NetworkDiscovery
# from ..collector.interactive import InteractiveCollector  # Temporarily disabled during migration
from ..validation.validator import ConfigurationValidator
from ..export.cfg_writer import CfgWriter
from ..ui.questionary_ui import QuestionaryUI

# Import the TUI Form Engine (external package)
from tui_form_engine.core.flow_engine import FlowEngine


logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Main configuration manager orchestrating the 4-phase process."""
    
    def __init__(self, 
                 project_root: Optional[str] = None,
                 config_file: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize the Configuration Manager.
        
        Args:
            project_root: Path to the project root directory
            config_file: Path to existing configuration file
            verbose: Enable verbose logging
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config_file = config_file
        self.verbose = verbose
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize components
        self.ui = QuestionaryUI()
        self.env_discovery = EnvironmentDiscovery()
        self.system_discovery = SystemDiscovery()
        self.docker_discovery = DockerDiscovery()
        self.network_discovery = NetworkDiscovery()
        
        # Initialize flow engine with layouts directory
        flows_dir = Path(__file__).parent.parent / "collector" / "layouts"
        self.flow_engine = FlowEngine(flows_dir=str(flows_dir))
        
        # Note: Legacy InteractiveCollector removed during Questionary migration
        self.validator = ConfigurationValidator()
        self.exporter = CfgWriter()
        
        # State
        self.discovered_data: Dict[str, Any] = {}
        self.configuration: Optional[Configuration] = None
        
    def run_discovery_phase(self) -> Dict[str, Any]:
        """
        Phase 1: Discovery
        Scan environment, system, and Docker to gather baseline information.
        
        Returns:
            Dictionary containing discovered data
        """
        self.ui.show_phase_header("Discovery Phase", "Scanning environment and system...")
        
        discovered = {}
        
        try:
            # Environment discovery
            self.ui.show_step("Scanning environment variables...")
            env_data = self.env_discovery.discover()
            discovered['environment'] = env_data
            self.ui.show_success(f"Found {len(env_data)} environment variables")
            
            # System discovery
            self.ui.show_step("Scanning system configuration...")
            system_data = self.system_discovery.discover()
            discovered['system'] = system_data
            self.ui.show_success("System scan complete")
            
            # Docker discovery
            self.ui.show_step("Scanning Docker environment...")
            docker_data = self.docker_discovery.discover()
            discovered['docker'] = docker_data
            self.ui.show_success("Docker scan complete")
            
            # Network discovery
            self.ui.show_step("Analyzing network topology and conflicts...")
            network_data = self.network_discovery.discover()
            discovered['network'] = network_data
            conflicts = network_data.get('conflicts', [])
            if conflicts:
                high_severity = len([c for c in conflicts if c.get('severity') == 'high'])
                if high_severity > 0:
                    self.ui.show_warning(f"Found {high_severity} high-severity network conflicts")
                else:
                    self.ui.show_info(f"Found {len(conflicts)} network conflicts")
            else:
                self.ui.show_success("No network conflicts detected")
            
            # Look for existing configuration files
            self.ui.show_step("Scanning for existing configuration files...")
            config_files = self._find_existing_configs()
            discovered['existing_configs'] = config_files
            if config_files:
                self.ui.show_success(f"Found {len(config_files)} existing configuration file(s)")
            else:
                self.ui.show_info("No existing configuration files found")
            
            self.discovered_data = discovered
            logger.info("Discovery phase completed successfully")
            
            return discovered
            
        except Exception as e:
            logger.error(f"Discovery phase failed: {e}")
            self.ui.show_error(f"Discovery failed: {e}")
            raise
    
    def run_interactive_collection_phase(self) -> Configuration:
        """
        Phase 2: Interactive Collection
        Collect configuration values from user with intelligent defaults.
        
        Returns:
            Configuration object with collected values
        """
        self.ui.show_phase_header("Interactive Collection", "Collecting configuration values...")
        
        try:
            # Initialize configuration with discovered defaults
            initial_config = self._create_initial_config()
            initial_data = initial_config.dict() if initial_config else {}
            
            # Generate enhanced defaults from discovery data
            enhanced_defaults = self._generate_enhanced_defaults()
            
            # Prepare variables for flow engine
            flow_variables = {
                'discovered_data': self.discovered_data,
                'initial_config': initial_data,
                'enhanced_defaults': enhanced_defaults,
                'system_data': self.discovered_data.get('system', {}),
                'docker_data': self.discovered_data.get('docker', {}),
                'env_data': self.discovered_data.get('environment', {}),
            }
            
            # Run comprehensive configuration flow
            config_data = {}
            
            # Execute main configuration layout
            self.ui.show_step("Collecting OpenProject configuration...")
            flow_result = self.flow_engine.execute_flow('config_tui.layout', context=flow_variables)
            config_data.update(flow_result)
            
            # Create configuration object
            self.configuration = Configuration(**config_data)
            
            # Show summary
            self._show_configuration_summary(self.configuration)
            
            logger.info("Interactive collection phase completed successfully")
            return self.configuration
            
        except Exception as e:
            logger.error(f"Interactive collection phase failed: {e}")
            self.ui.show_error(f"Configuration collection failed: {e}")
            raise
    
    def run_validation_phase(self) -> bool:
        """
        Phase 3: Validation
        Validate the collected configuration for completeness and correctness.
        
        Returns:
            True if validation passes, False otherwise
        """
        if not self.configuration:
            raise ValueError("No configuration to validate. Run collection phase first.")
        
        self.ui.show_phase_header("Validation Phase", "Validating configuration...")
        
        try:
            # Run validation
            validation_result = self.validator.validate_configuration(
                self.configuration,
                discovered_data=self.discovered_data
            )
            
            if validation_result.is_valid:
                self.ui.show_success("Configuration validation passed")
                logger.info("Validation phase completed successfully")
                return True
            else:
                self.ui.show_error("Configuration validation failed")
                for error in validation_result.errors:
                    self.ui.show_error(f"  - {error}")
                for warning in validation_result.warnings:
                    self.ui.show_warning(f"  - {warning}")
                logger.warning("Validation phase completed with errors")
                return False
                
        except Exception as e:
            logger.error(f"Validation phase failed: {e}")
            self.ui.show_error(f"Validation failed: {e}")
            raise
    
    def run_export_phase(self, output_path: Optional[str] = None) -> str:
        """
        Phase 4: Export
        Export configuration to .cfg file format.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to the exported configuration file
        """
        if not self.configuration:
            raise ValueError("No configuration to export. Run collection and validation phases first.")
        
        self.ui.show_phase_header("Export Phase", "Exporting configuration...")
        
        try:
            # Determine output path
            if not output_path:
                output_path = self.project_root / "interactive_config.cfg"
            
            # Export configuration
            exported_path = self.exporter.write_configuration(
                self.configuration,
                output_path=output_path
            )
            
            self.ui.show_success(f"Configuration exported to: {exported_path}")
            logger.info(f"Export phase completed successfully: {exported_path}")
            
            return str(exported_path)
            
        except Exception as e:
            logger.error(f"Export phase failed: {e}")
            self.ui.show_error(f"Export failed: {e}")
            raise
    
    def run_full_process(self, output_path: Optional[str] = None) -> str:
        """
        Run the complete 4-phase configuration process.
        
        Args:
            output_path: Optional custom output path for configuration file
            
        Returns:
            Path to the exported configuration file
        """
        self.ui.show_title("OpenProject Configuration Manager")
        self.ui.show_info("Starting 4-phase configuration process...")
        
        start_time = datetime.now()
        
        try:
            # Phase 1: Discovery
            self.run_discovery_phase()
            
            # Phase 2: Interactive Collection
            self.run_interactive_collection_phase()
            
            # Phase 3: Validation
            if not self.run_validation_phase():
                if not self.ui.confirm("Validation failed. Continue anyway?"):
                    raise ValueError("Configuration validation failed")
            
            # Phase 4: Export
            exported_path = self.run_export_phase(output_path)
            
            # Success summary
            duration = datetime.now() - start_time
            self.ui.show_success(f"Configuration process completed in {duration.total_seconds():.1f}s")
            self.ui.show_info(f"Configuration file: {exported_path}")
            
            return exported_path
            
        except KeyboardInterrupt:
            self.ui.show_error("Configuration process interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.ui.show_error(f"Configuration process failed: {e}")
            logger.error(f"Full process failed: {e}", exc_info=True)
            raise
    
    def load_existing_configuration(self, config_path: str) -> Configuration:
        """
        Load an existing configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Loaded Configuration object
        """
        self.ui.show_step(f"Loading configuration from {config_path}...")
        
        try:
            self.configuration = Configuration.from_cfg_file(config_path)
            self.ui.show_success("Configuration loaded successfully")
            logger.info(f"Configuration loaded from {config_path}")
            return self.configuration
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.ui.show_error(f"Failed to load configuration: {e}")
            raise
    
    def update_configuration(self) -> str:
        """
        Update an existing configuration interactively.
        
        Returns:
            Path to the updated configuration file
        """
        if not self.configuration:
            raise ValueError("No configuration loaded. Load existing configuration first.")
        
        self.ui.show_title("Update Configuration")
        
        # Run interactive collection with existing configuration as base
        updated_config = self.collector.collect_configuration(
            initial_config=self.configuration,
            discovered_data=self.discovered_data or {}
        )
        
        self.configuration = updated_config
        
        # Validate and export
        if self.run_validation_phase():
            return self.run_export_phase()
        else:
            if self.ui.confirm("Validation failed. Export anyway?"):
                return self.run_export_phase()
            else:
                raise ValueError("Configuration update cancelled due to validation errors")
    
    def _find_existing_configs(self) -> List[str]:
        """Find existing configuration files in the project."""
        config_patterns = [
            "*.cfg",
            "*.env",
            ".env*",
            "config/*.yml",
            "config/*.yaml",
            "docker-compose*.yml",
            "docker-compose*.yaml"
        ]
        
        found_files = []
        for pattern in config_patterns:
            found_files.extend(self.project_root.glob(pattern))
        
        return [str(f) for f in found_files if f.is_file()]
    
    def _create_initial_config(self) -> Configuration:
        """Create initial configuration with discovered defaults."""
        # Extract defaults from discovered data
        defaults = {}
        
        # From environment
        env_data = self.discovered_data.get('environment', {})
        if 'SECRET_KEY_BASE' in env_data:
            defaults['secret_key_base'] = env_data['SECRET_KEY_BASE']
        
        # From Docker
        docker_data = self.discovered_data.get('docker', {})
        if docker_data.get('containers'):
            # Check for existing database containers
            for container in docker_data['containers']:
                if 'postgres' in container.get('image', '').lower():
                    defaults.setdefault('database', {})['adapter'] = 'postgresql'
                elif 'mysql' in container.get('image', '').lower():
                    defaults.setdefault('database', {})['adapter'] = 'mysql'
        
        # From system
        system_data = self.discovered_data.get('system', {})
        if system_data.get('hostname'):
            defaults.setdefault('proxy', {})['domain'] = f"{system_data['hostname']}.local"
        
        # Create configuration with intelligent defaults
        try:
            return Configuration(**defaults) if defaults else Configuration(
                secret_key_base="",
                proxy={"domain": "openproject.local"},
                database={
                    "adapter": "postgresql",
                    "host": "db", 
                    "port": 5432,
                    "name": "openproject",
                    "username": "openproject",
                    "password": "changeme"  # Default password, will be collected in flow
                }
            )
        except Exception:
            # Fallback to minimal configuration
            return Configuration(
                secret_key_base="",
                proxy={"domain": "openproject.local"},
                database={
                    "adapter": "postgresql",
                    "host": "db",
                    "port": 5432, 
                    "name": "openproject",
                    "username": "openproject",
                    "password": "changeme"  # Default password
                }
            )
    
    def _generate_enhanced_defaults(self) -> Dict[str, Any]:
        """Generate enhanced defaults structure from discovery data for TUI flow engine."""
        from datetime import datetime
        
        # Extract discovery data
        system_data = self.discovered_data.get('system', {})
        network_data = self.discovered_data.get('network', {})
        docker_data = self.discovered_data.get('docker', {})
        env_data = self.discovered_data.get('environment', {})
        
        # Build metadata section
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'probe_version': '1.0.0',
            'layout_file': 'config_tui.layout.yml',
            'system_info': self._extract_system_metadata(system_data),
            'network_info': self._extract_network_metadata(network_data),
            'services_info': self._extract_services_metadata(docker_data, env_data),
            'storage_info': self._extract_storage_metadata(system_data)
        }
        
        # Build intelligent defaults section
        defaults = {
            'domain': self._generate_domain_default(network_data, system_data),
            'port': self._generate_port_default(network_data),
            'memory_limit': self._generate_memory_default(system_data),
            'database_setup': self._generate_database_default(docker_data),
            'ssl_configuration': self._generate_ssl_default(network_data),
        }
        
        return {
            'metadata': metadata,
            'defaults': defaults
        }
    
    def _extract_system_metadata(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract system metadata for enhanced defaults."""
        platform_info = system_data.get('platform', {})
        hardware_info = system_data.get('hardware', {})
        
        return {
            'os': platform_info.get('system', 'Unknown'),
            'arch': platform_info.get('machine', 'Unknown'),
            'hostname': platform_info.get('hostname', 'unknown'),
            'memory_total_gb': hardware_info.get('memory', {}).get('total_gb', 0),
            'memory_available_gb': hardware_info.get('memory', {}).get('available_gb', 0),
            'cpu_cores': hardware_info.get('cpu', {}).get('cores', 0),
            'cpu_model': hardware_info.get('cpu', {}).get('model', 'Unknown')
        }
    
    def _extract_network_metadata(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract network metadata for enhanced defaults."""
        basic_info = network_data.get('basic_info', {})
        port_analysis = network_data.get('port_analysis', {})
        
        return {
            'hostname': basic_info.get('hostname', 'unknown'),
            'interfaces': [iface.get('name', 'unknown') for iface in network_data.get('interfaces', [])],
            'available_ports': port_analysis.get('available_ports', []),
            'recommended_ports': port_analysis.get('recommended_ports', {}),
            'conflicts': len(network_data.get('conflicts', []))
        }
    
    def _extract_services_metadata(self, docker_data: Dict[str, Any], env_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract services metadata for enhanced defaults."""
        containers = docker_data.get('containers', [])
        
        return {
            'docker_available': docker_data.get('docker_available', False),
            'existing_containers': [c.get('name', 'unknown') for c in containers],
            'database_containers': len(docker_data.get('database_containers', [])),
            'postgresql_detected': any('postgres' in c.get('image', '').lower() for c in containers),
            'mysql_detected': any('mysql' in c.get('image', '').lower() for c in containers)
        }
    
    def _extract_storage_metadata(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract storage metadata for enhanced defaults."""
        storage_info = system_data.get('storage', {})
        
        return {
            'total_space_gb': storage_info.get('total_gb', 0),
            'available_space_gb': storage_info.get('free_gb', 0),
            'recommended_data_path': '/opt/openproject/data'
        }
    
    def _generate_domain_default(self, network_data: Dict[str, Any], system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent domain default."""
        basic_info = network_data.get('basic_info', {})
        fqdn = basic_info.get('fqdn')
        domain = basic_info.get('domain')
        hostname = basic_info.get('hostname')
        
        # Prefer FQDN if available and it's not localhost
        if fqdn and fqdn != 'localhost' and '.' in fqdn and not fqdn.endswith('.local'):
            domain_value = fqdn
            reason = f"Using detected FQDN '{fqdn}' from network configuration"
            confidence = "high"
        # Fall back to hostname + detected domain
        elif hostname and domain and hostname != 'localhost':
            domain_value = f"{hostname}.{domain}"
            reason = f"Using detected hostname '{hostname}' with domain '{domain}'"
            confidence = "high"
        # Fall back to hostname + .local for local development
        elif hostname and hostname != 'localhost':
            domain_value = f"{hostname}.local"
            reason = f"Using detected hostname '{hostname}' with .local suffix for local development"
            confidence = "medium"
        else:
            domain_value = "openproject.local"
            reason = "No reliable hostname detected, using default local domain"
            confidence = "low"
        
        return {
            'value': domain_value,
            'reason': reason,
            'probe_source': 'network.hostname_detection',
            'confidence': confidence
        }
    
    def _generate_port_default(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent port default."""
        recommended_ports = network_data.get('port_analysis', {}).get('recommended_ports', {})
        conflicts = network_data.get('conflicts', [])
        
        if 'web' in recommended_ports:
            port = str(recommended_ports['web'])
            reason = f"Port {port} is available and recommended by network analysis"
            confidence = "high"
        elif any(c.get('port') == 80 for c in conflicts):
            port = "8080"
            reason = "Port 80 is in use, using alternative port 8080"
            confidence = "medium"
        else:
            port = "80"
            reason = "Standard HTTP port 80 appears available"
            confidence = "medium"
        
        return {
            'value': port,
            'reason': reason,
            'probe_source': 'network.port_availability',
            'confidence': confidence
        }
    
    def _generate_memory_default(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent memory allocation default."""
        total_gb = system_data.get('hardware', {}).get('memory', {}).get('total_gb', 0)
        
        if total_gb >= 16:
            memory = "4GB"
            reason = f"Detected {total_gb:.1f}GB system RAM, recommending 25% allocation (4GB)"
            confidence = "high"
        elif total_gb >= 8:
            memory = "2GB"
            reason = f"Detected {total_gb:.1f}GB system RAM, recommending 25% allocation (2GB)"
            confidence = "high"
        elif total_gb >= 4:
            memory = "1GB"
            reason = f"Detected {total_gb:.1f}GB system RAM, recommending conservative allocation (1GB)"
            confidence = "medium"
        else:
            memory = "2GB"
            reason = "Could not detect system memory, using moderate default (2GB)"
            confidence = "low"
        
        return {
            'value': memory,
            'reason': reason,
            'probe_source': 'system.memory_analysis',
            'confidence': confidence
        }
    
    def _generate_database_default(self, docker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent database setup default."""
        database_containers = docker_data.get('database_containers', [])
        
        if database_containers:
            container_name = database_containers[0].get('name', 'existing-db')
            value = "existing"
            reason = f"Found existing database container '{container_name}', recommending reuse"
            confidence = "high"
        else:
            value = "container"
            reason = "No existing database detected, recommending containerized PostgreSQL"
            confidence = "high"
        
        return {
            'value': value,
            'reason': reason,
            'probe_source': 'docker.container_scan',
            'confidence': confidence
        }
    
    def _generate_ssl_default(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent SSL configuration default."""
        security_info = network_data.get('security', {})
        has_public_ip = network_data.get('basic_info', {}).get('public_ip') is not None
        
        if has_public_ip:
            value = "Generate Let's Encrypt certificate"
            reason = "Public IP detected, SSL certificate recommended for security"
            confidence = "high"
        else:
            value = "Self-signed certificate"
            reason = "Local deployment detected, self-signed certificate sufficient"
            confidence = "medium"
        
        return {
            'value': value,
            'reason': reason,
            'probe_source': 'network.ssl_analysis',
            'confidence': confidence
        }
    
    def _show_configuration_summary(self, configuration: Configuration):
        """Show a summary of the collected configuration."""
        self.ui.show_section_header("Configuration Summary")
        
        # Show key configuration details
        self.ui.show_info(f"Environment: {configuration.rails_env}")
        self.ui.show_info(f"Database: {configuration.database.adapter} on {configuration.database.host}:{configuration.database.port}")
        self.ui.show_info(f"Domain: {configuration.proxy.domain}")
        self.ui.show_info(f"SSL: {'Enabled' if configuration.proxy.ssl_enabled else 'Disabled'}")
        
        # Show URL configuration
        uri_namespace_enabled = getattr(configuration, 'uri_namespace_enabled', False)
        uri_namespace = getattr(configuration, 'uri_namespace', '')
        
        if uri_namespace_enabled and uri_namespace:
            self.ui.show_info(f"Namespace: Enabled ({uri_namespace})")
            self.ui.show_info(f"Access URL: https://{configuration.proxy.domain}{uri_namespace}")
        else:
            self.ui.show_info("Namespace: Disabled")
            self.ui.show_info(f"Access URL: https://{configuration.proxy.domain}")
        
        # Show any warnings
        warnings = []
        if not configuration.proxy.ssl_enabled:
            warnings.append("SSL is disabled - not recommended for production")
        if configuration.rails_env == 'development':
            warnings.append("Development environment selected")
        
        if warnings:
            self.ui.show_warning("Configuration Warnings:")
            for warning in warnings:
                self.ui.show_warning(f"  - {warning}")
        
        self.ui.show_success("Configuration summary complete")