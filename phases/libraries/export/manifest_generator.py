"""
Step: Export Manifest
Export configuration manifest for deploy-manager

Migrated from orchestrator_export.py::_export_manifest()
"""

from pathlib import Path
from typing import Dict, Any
import logging
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)


def execute_export_manifest(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Export configuration manifest for deploy-manager.
    
    Args:
        context: Execution context containing:
            - generated_at: Timestamp of generation
            - discovery_summary: Summary from Phase 1
            - validation_passed: Status from Phase 4
            - export_dir: Target directory for exports
            
    Returns:
        Dict with artifacts:
            - manifest_file: Path to generated configuration_manifest.yml
    """
    logger.info("Executing Export Manifest")
    
    # Get export directory from context or use default
    project_root = phase_dir.parent.parent
    export_dir = context.get('export_dir', project_root / "phases/outputs")
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = export_dir / 'configuration_manifest.yml'
    
    # Build manifest
    manifest = {
        'component': 'config-manager',
        'version': '1.0.0',
        'generated_at': context.get('generated_at', datetime.now().isoformat()),
        'pipeline_status': 'complete',
        'phases_completed': [
            'discovery',
            'tui_mapping',
            'collection',
            'validation',
            'export'
        ],
        'artifacts': {
            'docker_compose': 'docker-compose.yml',
            'environment': '.env',
            'manifest': 'configuration_manifest.yml'
        },
        'ready_for_deployment': True,
        'metadata': {
            'discovery_summary': context.get('discovery_summary', {}),
            'validation_status': context.get('validation_passed', False),
            'docker_compose_file': context.get('docker_compose_file', 'docker-compose.yml'),
            'env_file': context.get('env_file', '.env')
        }
    }
    
    # Write manifest
    with open(output_file, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
    
    logger.info(f"Exported manifest to {output_file}")
    
    return {
        'manifest_file': str(output_file),
        'export_summary': {
            'files_exported': 3,
            'export_directory': str(export_dir),
            'ready_for_deployment': True
        }
    }


class ExportManifestStep:
    """Wrapper class for export_manifest step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_5_export"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute export_manifest step.
        
        Args:
            context: Execution context
            
        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_export_manifest(context, self.phase_dir)
        
        # Return in expected format
        return {
            "artifacts": result_data if isinstance(result_data, dict) else {"data": result_data}
        }
