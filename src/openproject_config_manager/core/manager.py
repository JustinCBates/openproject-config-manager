"""Core configuration manager implementation."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from ..core.config import Configuration
from ..discovery.environment import EnvironmentDiscovery
from ..discovery.system import SystemDiscovery
from ..discovery.docker import DockerDiscovery
from ..collector.interactive import InteractiveCollector
from ..validation.validator import ConfigurationValidator
from ..export.cfg_writer import CfgWriter
from ..ui.console import ConsoleUI


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
        self.ui = ConsoleUI()
        self.env_discovery = EnvironmentDiscovery()
        self.system_discovery = SystemDiscovery()
        self.docker_discovery = DockerDiscovery()
        self.collector = InteractiveCollector(ui=self.ui)
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
            
            # Run interactive collection
            self.configuration = self.collector.collect_configuration(
                initial_config=initial_config,
                discovered_data=self.discovered_data
            )
            
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
                proxy={"domain": "openproject.local"}
            )
        except Exception:
            # Fallback to minimal configuration
            return Configuration(
                secret_key_base="",
                proxy={"domain": "openproject.local"}
            )