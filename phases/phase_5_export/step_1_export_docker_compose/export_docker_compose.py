"""
Step: Export Docker Compose
Export docker-compose.yml file for deployment

Migrated from orchestrator_export.py::_export_docker_compose()
"""

from pathlib import Path
from typing import Dict, Any
import logging
import yaml

logger = logging.getLogger(__name__)


def execute_export_docker_compose(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Export docker-compose.yml file based on validated configuration.
    
    Args:
        context: Execution context containing:
            - validated_configuration: Validated config from Phase 4
            - user_configuration: User config from Phase 3
            - export_dir: Target directory for exports
            
    Returns:
        Dict with artifacts:
            - docker_compose_file: Path to generated docker-compose.yml
    """
    logger.info("Executing Export Docker Compose")
    
    # Get export directory from context or use default
    project_root = phase_dir.parent.parent
    export_dir = context.get('export_dir', project_root / "phases/outputs")
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = export_dir / 'docker-compose.yml'
    
    # Get configuration from context
    validated_config = context.get('validated_configuration', {})
    user_config = context.get('user_configuration', validated_config)
    
    # If user_config is a file path string, we need to handle it differently
    # For now, assume it's already loaded
    if isinstance(user_config, str):
        logger.warning(f"user_configuration is a path: {user_config}, using validated_config")
        user_config = validated_config
    
    # Extract configuration sections
    project = user_config.get('project', {})
    admin = user_config.get('admin', {})
    database = user_config.get('database', {})
    email = user_config.get('email', {})
    network = user_config.get('network', {})
    storage = user_config.get('storage', {})
    
    # Build docker-compose structure
    docker_compose = {
        'version': '3.8',
        'services': {
            'openproject': {
                'image': 'openproject/community:latest',
                'container_name': project.get('identifier', 'openproject'),
                'ports': [f"{network.get('port', 80)}:8080"],
                'environment': {
                    'OPENPROJECT_HOST__NAME': network.get('domain', 'openproject.local'),
                    'OPENPROJECT_HTTPS': str(network.get('ssl_enabled', False)).lower(),
                    'OPENPROJECT_DEFAULT__LANGUAGE': project.get('language', 'en'),
                    'DATABASE_URL': f"postgres://{database.get('username', 'openproject')}:{database.get('password', 'password')}@db:5432/{database.get('database_name', 'openproject')}"
                },
                'volumes': [
                    'openproject-data:/var/openproject/assets'
                ],
                'depends_on': ['db'],
                'restart': 'unless-stopped'
            },
            'db': {
                'image': 'postgres:13',
                'container_name': f"{project.get('identifier', 'openproject')}-db",
                'environment': {
                    'POSTGRES_DB': database.get('database_name', 'openproject'),
                    'POSTGRES_USER': database.get('username', 'openproject'),
                    'POSTGRES_PASSWORD': database.get('password', 'password')
                },
                'volumes': [
                    'postgres-data:/var/lib/postgresql/data'
                ],
                'restart': 'unless-stopped'
            }
        },
        'volumes': {
            'openproject-data': {},
            'postgres-data': {}
        },
        'networks': {
            'default': {
                'name': f"{project.get('identifier', 'openproject')}-network"
            }
        }
    }
    
    # Add email service if configured
    if email.get('enabled'):
        docker_compose['services']['mailhog'] = {
            'image': 'mailhog/mailhog',
            'container_name': f"{project.get('identifier', 'openproject')}-mail",
            'ports': ['8025:8025', '1025:1025'],
            'restart': 'unless-stopped'
        }
    
    # Write docker-compose.yml
    with open(output_file, 'w') as f:
        yaml.dump(docker_compose, f, default_flow_style=False, sort_keys=False)
    
    logger.info(f"Exported docker-compose.yml to {output_file}")
    
    return {
        'docker_compose_file': str(output_file)
    }


class ExportDockerComposeStep:
    """Wrapper class for export_docker_compose step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_5_export"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute export_docker_compose step.
        
        Args:
            context: Execution context
            
        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_export_docker_compose(context, self.phase_dir)
        
        # Return in expected format
        return {
            "artifacts": result_data if isinstance(result_data, dict) else {"data": result_data}
        }
