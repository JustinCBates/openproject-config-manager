"""
Step: Dependency Validation
Check configuration dependencies and compatibility

Migrated from src/openproject_config_manager/validator/
"""

from pathlib import Path
from typing import Dict, List, Any
import logging
import yaml
from dataclasses import dataclass
import sys

# Conditional imports to handle both module context and standalone execution
if __name__ == '__main__':
    # When running as standalone script, add parent to path for absolute imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    # No step-specific modules to import for standalone mode

logger = logging.getLogger(__name__)


@dataclass
class DependencyValidationResult:
    """Result of dependency validation."""
    warnings: List[str]
    recommendations: List[str]
    passed: bool
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def add_recommendation(self, message: str):
        """Add a recommendation."""
        self.recommendations.append(message)


class DependencyValidator:
    """Validates service and configuration dependencies."""
    
    def __init__(self):
        """Initialize the dependency validator."""
        pass
    
    def validate(self, configuration: Dict[str, Any]) -> DependencyValidationResult:
        """
        Validate dependencies between services and configuration options.
        
        Args:
            configuration: Configuration dictionary to validate
            
        Returns:
            DependencyValidationResult with validation details
        """
        logger.info("Starting dependency validation")
        
        result = DependencyValidationResult(warnings=[], recommendations=[], passed=True)
        
        # Extract user responses
        user_responses = configuration.get('user_responses', {})
        
        # Validate service dependencies
        self._validate_database_dependencies(user_responses, result)
        self._validate_email_dependencies(user_responses, result)
        self._validate_storage_dependencies(user_responses, result)
        self._validate_network_dependencies(user_responses, result)
        
        # Validate configuration consistency
        self._validate_configuration_consistency(user_responses, result)
        
        logger.info(f"Dependency validation completed: {'PASSED' if result.passed else 'FAILED'}")
        logger.info(f"Warnings: {len(result.warnings)}, Recommendations: {len(result.recommendations)}")
        
        return result
    
    def _validate_database_dependencies(self, user_responses: Dict[str, Any], result: DependencyValidationResult):
        """Validate database-related dependencies."""
        database = user_responses.get('database', {})
        
        # Container database warnings
        if database.get('setup') == 'container':
            result.add_recommendation("Container database will be created - ensure Docker has sufficient resources")
        
        # PostgreSQL vs MySQL
        if database.get('type') == 'postgresql':
            result.add_recommendation("PostgreSQL selected - ensure version 12+ for best compatibility")
        elif database.get('type') == 'mysql':
            result.add_warning("MySQL is supported but PostgreSQL is recommended for OpenProject")
    
    def _validate_email_dependencies(self, user_responses: Dict[str, Any], result: DependencyValidationResult):
        """Validate email service dependencies."""
        email = user_responses.get('email', {})
        
        if not email:
            result.add_warning("Email configuration not provided - email notifications will not work")
            return
        
        delivery_method = email.get('delivery_method')
        
        if delivery_method == 'smtp':
            smtp = email.get('smtp', {})
            
            if not smtp.get('host'):
                result.add_warning("SMTP host not configured - email notifications will fail")
            
            # Check for common SMTP ports
            port = smtp.get('port', 25)
            if port == 25:
                result.add_warning("Port 25 is commonly blocked - consider using port 587 (TLS) or 465 (SSL)")
            
            # Encryption recommendations
            encryption = smtp.get('encryption')
            if not encryption or encryption == 'none':
                result.add_warning("SMTP encryption not enabled - consider enabling TLS/SSL for security")
        
        elif delivery_method == 'sendmail':
            result.add_recommendation("Using sendmail - ensure sendmail is installed on the host system")
    
    def _validate_storage_dependencies(self, user_responses: Dict[str, Any], result: DependencyValidationResult):
        """Validate storage and backup dependencies."""
        storage = user_responses.get('storage', {})
        
        if not storage:
            result.add_warning("Storage configuration not provided - using defaults")
            return
        
        # Backup configuration
        backup = user_responses.get('backup', {})
        if backup and backup.get('enabled'):
            retention_days = backup.get('retention_days', 30)
            
            if retention_days > 90:
                result.add_warning(f"Backup retention of {retention_days} days may consume significant storage")
            
            result.add_recommendation("Regular backups enabled - ensure backup location has sufficient space")
    
    def _validate_network_dependencies(self, user_responses: Dict[str, Any], result: DependencyValidationResult):
        """Validate network-related dependencies."""
        network = user_responses.get('network', {})
        
        if not network:
            result.add_warning("Network configuration not provided - using defaults")
            return
        
        domain = network.get('domain')
        
        # SSL/Let's Encrypt dependencies
        if domain and not (domain in ['localhost', '127.0.0.1'] or domain.endswith('.local')):
            result.add_recommendation("Public domain detected - consider enabling SSL/Let's Encrypt")
        
        # Port configuration
        if network.get('port'):
            port = network.get('port')
            if port != 80 and port != 443:
                result.add_warning(f"Non-standard port {port} configured - ensure firewall allows this port")
    
    def _validate_configuration_consistency(self, user_responses: Dict[str, Any], result: DependencyValidationResult):
        """Validate configuration consistency across sections."""
        project = user_responses.get('project', {})
        network = user_responses.get('network', {})
        
        # Production environment checks
        if project.get('environment') == 'production':
            domain = network.get('domain', '')
            
            if domain in ['localhost', '127.0.0.1'] or domain.endswith('.local'):
                result.add_warning("Production environment with localhost/local domain is not recommended")
            
            # Check for development-only settings in production
            result.add_recommendation("Production environment - ensure all security settings are properly configured")
        
        # Resource allocation consistency
        resources = user_responses.get('resources', {})
        if resources:
            worker_processes = resources.get('worker_processes', 2)
            
            if worker_processes > 8:
                result.add_warning(f"High worker process count ({worker_processes}) - ensure system has sufficient CPU cores")
            elif worker_processes == 1:
                result.add_recommendation("Single worker process - consider increasing for better performance")


def execute_dependency_validation(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Dependency Validation
    Status: IMPLEMENTED
    
    Check for conflicts and dependencies
    
    Args:
        context: Execution context containing user_configuration_file
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results including warnings and recommendations
    """
    logger.info("Executing step: Dependency Validation")
    
    # Load collected configuration from Phase 3
    user_config_file = context.get('user_configuration_file')
    if not user_config_file:
        raise ValueError("user_configuration_file not found in context")
    
    with open(user_config_file, 'r') as f:
        configuration = yaml.safe_load(f)
    
    # Run dependency validation
    validator = DependencyValidator()
    validation_result = validator.validate(configuration)
    
    result = {
        'step': 'dependency_validation',
        'status': 'completed',
        'warnings': validation_result.warnings,
        'recommendations': validation_result.recommendations,
        'passed': validation_result.passed
    }
    
    logger.info(f"Dependency validation completed: {'PASSED' if validation_result.passed else 'FAILED'}")
    logger.info(f"Warnings: {len(validation_result.warnings)}, Recommendations: {len(validation_result.recommendations)}")
    
    return result


def main():
    """Standalone entry point for testing this step."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dependency Validation")
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
        result = execute_dependency_validation(context, phase_dir)
        
        print("\n" + "=" * 70)
        if result.get('passed', False):
            print("✅ Dependency Validation PASSED")
        else:
            print("⚠️  Dependency Validation has warnings")
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
