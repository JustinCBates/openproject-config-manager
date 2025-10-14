"""
Step: Intelligent Defaults Generation
Generate enhanced defaults based on discovery data

Migrated from src/openproject_config_manager/prober/
"""

from pathlib import Path
from typing import Dict, Any
import logging
import yaml
from datetime import datetime
import sys

# Conditional imports to handle both module context and standalone execution
if __name__ == '__main__':
    # When running as standalone script, add parent to path for absolute imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    # No step-specific modules to import for standalone mode

logger = logging.getLogger(__name__)


class DefaultsGenerator:
    """Generates intelligent defaults from discovery data."""
    
    def generate_enhanced_defaults(self, 
                                  environment_data: Dict[str, Any],
                                  system_data: Dict[str, Any],
                                  docker_data: Dict[str, Any],
                                  network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate enhanced defaults structure from discovery data.
        
        Args:
            environment_data: Environment variable discovery data
            system_data: System resources discovery data
            docker_data: Docker environment discovery data
            network_data: Network configuration discovery data
            
        Returns:
            Enhanced defaults structure with metadata and intelligent defaults
        """
        logger.info("Generating enhanced defaults from discovery data")
        
        # Build metadata section
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'probe_version': '1.0.0',
            'layout_file': 'config_tui.layout.yml',
            'system_info': self._extract_system_metadata(system_data),
            'network_info': self._extract_network_metadata(network_data),
            'services_info': self._extract_services_metadata(docker_data, environment_data),
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
        
        logger.info(f"Generated {len(defaults)} intelligent defaults with metadata")
        
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


def execute_defaults_generation(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Intelligent Defaults Generation
    Status: IMPLEMENTED
    
    Generate enhanced defaults based on discovery data
    
    Args:
        context: Execution context containing:
            - environment_data: Environment variable discovery
            - system_data: System resources discovery
            - docker_data: Docker environment discovery
            - network_data: Network configuration discovery
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results including:
            - enhanced_defaults_file: Path to generated defaults file
            - defaults_summary: Summary of generated defaults
            - enhanced_defaults: Full defaults structure
    """
    logger.info("Executing step: Intelligent Defaults Generation")
    
    # Extract discovery data from context
    environment_data = context.get('environment_data', {})
    system_data = context.get('system_data', {})
    docker_data = context.get('docker_data', {})
    network_data = context.get('network_data', {})
    
    # Generate enhanced defaults
    generator = DefaultsGenerator()
    enhanced_defaults = generator.generate_enhanced_defaults(
        environment_data=environment_data,
        system_data=system_data,
        docker_data=docker_data,
        network_data=network_data
    )
    
    # Write to output file
    output_dir = phase_dir / 'outputs' / 'discovery'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'enhanced_defaults.yml'
    
    with open(output_file, 'w') as f:
        yaml.dump(enhanced_defaults, f, default_flow_style=False, sort_keys=False)
    
    logger.info(f"Enhanced defaults written to {output_file}")
    
    # Create summary
    defaults_count = len(enhanced_defaults.get('defaults', {}))
    defaults_summary = {
        'total_defaults_generated': defaults_count,
        'metadata_included': True,
        'confidence_levels': {
            k: v.get('confidence', 'unknown') 
            for k, v in enhanced_defaults.get('defaults', {}).items()
        }
    }
    
    result = {
        'step': 'defaults_generation',
        'status': 'completed',
        'enhanced_defaults_file': str(output_file),
        'defaults_summary': defaults_summary,
        'enhanced_defaults': enhanced_defaults
    }
    
    logger.info(f"Step Intelligent Defaults Generation completed: {defaults_count} defaults generated")
    return result


def main():
    """Standalone entry point for testing this step."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Defaults Generation")
    parser.add_argument('--output-dir', help='Output directory', default=None)
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup paths
    phase_dir = Path(__file__).parent.parent
    
    try:
        # Build context with mock discovery data
        context = {
            'environment_data': {},
            'system_data': {},
            'docker_data': {},
            'network_data': {}
        }
        
        # Execute step
        result = execute_defaults_generation(context, phase_dir)
        
        print("\n" + "=" * 70)
        print(f"✅ Step completed: {result.get('status', 'unknown')}")
        print("=" * 70)
        print(f"\n📊 Defaults Generation Results:")
        
        if 'defaults_summary' in result:
            summary = result['defaults_summary']
            print(f"  • Total defaults generated: {summary.get('total_defaults_generated', 0)}")
            print(f"  • Enhanced defaults file: {result.get('enhanced_defaults_file', 'N/A')}")
        
        return 0 if result.get('status') == 'completed' else 1
        
    except Exception as e:
        print(f"\n❌ Step failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())


"""
DefaultsGenerationStep - Wrapper for existing execute_defaults_generation implementation
"""

from pathlib import Path
from typing import Dict, Any
from .defaults_generation import execute_defaults_generation


class DefaultsGenerationStep:
    """Wrapper class for defaults_generation step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_1_discovery"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute defaults_generation step.
        
        Args:
            context: Execution context
            
        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_defaults_generation(context, self.phase_dir)
        
        # Return in expected format
        return {
            "artifacts": result_data if isinstance(result_data, dict) else {"data": result_data}
        }
