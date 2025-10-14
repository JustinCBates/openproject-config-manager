"""
Step: Environment Validation
Validate environment compatibility and resource requirements

Migrated from src/openproject_config_manager/validator/
"""

from pathlib import Path
from typing import Dict, List, Any
import logging
import yaml
import socket
from dataclasses import dataclass
import sys

# Conditional imports to handle both module context and standalone execution
if __name__ == '__main__':
    # When running as standalone script, add parent to path for absolute imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    # No step-specific modules to import for standalone mode

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentValidationResult:
    """Result of environment validation."""
    warnings: List[str]
    recommendations: List[str]
    passed: bool
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def add_recommendation(self, message: str):
        """Add a recommendation."""
        self.recommendations.append(message)


class EnvironmentValidator:
    """Validates environment compatibility and system resources."""
    
    def __init__(self):
        """Initialize the environment validator."""
        pass
    
    def validate(self, configuration: Dict[str, Any]) -> EnvironmentValidationResult:
        """
        Validate environment compatibility and resources.
        
        Args:
            configuration: Configuration dictionary to validate
            
        Returns:
            EnvironmentValidationResult with validation details
        """
        logger.info("Starting environment validation")
        
        result = EnvironmentValidationResult(warnings=[], recommendations=[], passed=True)
        
        # Extract user responses
        user_responses = configuration.get('user_responses', {})
        
        # Validate port availability
        self._validate_port_availability(user_responses, result)
        
        # Validate disk space (if possible)
        self._validate_disk_space(user_responses, result)
        
        # Validate network connectivity
        self._validate_network_connectivity(user_responses, result)
        
        # Validate external service connectivity
        self._validate_external_services(user_responses, result)
        
        logger.info(f"Environment validation completed: {'PASSED' if result.passed else 'FAILED'}")
        logger.info(f"Warnings: {len(result.warnings)}, Recommendations: {len(result.recommendations)}")
        
        return result
    
    def _validate_port_availability(self, user_responses: Dict[str, Any], result: EnvironmentValidationResult):
        """Validate that required ports are available."""
        network = user_responses.get('network', {})
        
        # Default ports to check
        ports_to_check = [80, 443]  # HTTP and HTTPS
        
        if network.get('port'):
            custom_port = network['port']
            if custom_port not in ports_to_check:
                ports_to_check.append(custom_port)
        
        # Database port
        database = user_responses.get('database', {})
        if database.get('setup') == 'container':
            if database.get('type') == 'postgresql':
                ports_to_check.append(5432)
            elif database.get('type') == 'mysql':
                ports_to_check.append(3306)
        
        # Check port availability
        unavailable_ports = []
        for port in ports_to_check:
            if not self._is_port_available(port):
                unavailable_ports.append(port)
        
        if unavailable_ports:
            result.add_warning(f"Ports already in use: {', '.join(map(str, unavailable_ports))} - ensure these can be released")
    
    def _validate_disk_space(self, user_responses: Dict[str, Any], result: EnvironmentValidationResult):
        """Validate available disk space."""
        try:
            import shutil
            
            # Check root filesystem
            stat = shutil.disk_usage('/')
            free_gb = stat.free / (1024**3)
            
            # OpenProject minimum requirements
            if free_gb < 10:
                result.add_warning(f"Low disk space: {free_gb:.1f}GB free - OpenProject requires at least 10GB")
            elif free_gb < 20:
                result.add_recommendation(f"Disk space: {free_gb:.1f}GB free - consider allocating more space for production")
            else:
                result.add_recommendation(f"Disk space: {free_gb:.1f}GB free - sufficient for deployment")
                
        except Exception as e:
            logger.debug(f"Could not check disk space: {e}")
            result.add_recommendation("Could not verify disk space - ensure sufficient storage is available")
    
    def _validate_network_connectivity(self, user_responses: Dict[str, Any], result: EnvironmentValidationResult):
        """Validate network connectivity."""
        network = user_responses.get('network', {})
        domain = network.get('domain', '')
        
        # Skip localhost
        if domain in ['localhost', '127.0.0.1'] or domain.endswith('.local'):
            return
        
        # Try to resolve domain
        try:
            socket.gethostbyname(domain)
            result.add_recommendation(f"Domain {domain} resolves successfully")
        except socket.gaierror:
            result.add_warning(f"Cannot resolve domain {domain} - ensure DNS is configured")
        except Exception as e:
            logger.debug(f"Network check failed: {e}")
    
    def _validate_external_services(self, user_responses: Dict[str, Any], result: EnvironmentValidationResult):
        """Validate connectivity to external services."""
        # Check external database connectivity
        database = user_responses.get('database', {})
        if database.get('setup') == 'external' and database.get('host'):
            host = database['host']
            port = database.get('port', 5432)
            
            if not self._test_host_connectivity(host, port):
                result.add_warning(f"Cannot reach external database at {host}:{port} - ensure it's accessible")
        
        # Check SMTP server connectivity
        email = user_responses.get('email', {})
        if email.get('delivery_method') == 'smtp':
            smtp = email.get('smtp', {})
            if smtp.get('host'):
                host = smtp['host']
                port = smtp.get('port', 587)
                
                if not self._test_host_connectivity(host, port):
                    result.add_warning(f"Cannot reach SMTP server at {host}:{port} - email notifications may fail")
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False
    
    def _test_host_connectivity(self, host: str, port: int, timeout: int = 3) -> bool:
        """Test if a host is reachable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False


def execute_environment_validation(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Environment Validation
    Status: IMPLEMENTED
    
    Validate against current environment constraints
    
    Args:
        context: Execution context containing user_configuration_file
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results including warnings and recommendations
    """
    logger.info("Executing step: Environment Validation")
    
    # Load collected configuration from Phase 3
    user_config_file = context.get('user_configuration_file')
    if not user_config_file:
        raise ValueError("user_configuration_file not found in context")
    
    with open(user_config_file, 'r') as f:
        configuration = yaml.safe_load(f)
    
    # Run environment validation
    validator = EnvironmentValidator()
    validation_result = validator.validate(configuration)
    
    result = {
        'step': 'environment_validation',
        'status': 'completed',
        'warnings': validation_result.warnings,
        'recommendations': validation_result.recommendations,
        'passed': validation_result.passed
    }
    
    logger.info(f"Environment validation completed: {'PASSED' if validation_result.passed else 'FAILED'}")
    logger.info(f"Warnings: {len(validation_result.warnings)}, Recommendations: {len(validation_result.recommendations)}")
    
    return result


def main():
    """Standalone entry point for testing this step."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Environment Validation")
    parser.add_argument('--user-config', required=True, help='Path to user_configuration.yml')
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
        # Build context
        context = {
            'user_configuration_file': args.user_config
        }
        
        # Execute step
        result = execute_environment_validation(context, phase_dir)
        
        print("\n" + "=" * 70)
        if result.get('passed', False):
            print("✅ Environment Validation PASSED")
        else:
            print("⚠️  Environment Validation has warnings")
        print("=" * 70)
        print(f"\n📊 Validation Results:")
        print(f"  • Warnings: {len(result.get('warnings', []))}")
        print(f"  • Recommendations: {len(result.get('recommendations', []))}")
        
        if result.get('warnings'):
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"    - {warning}")
        
        if result.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"    - {rec}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Step failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
