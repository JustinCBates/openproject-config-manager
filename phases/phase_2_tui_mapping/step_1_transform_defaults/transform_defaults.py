"""
Step: Transform Defaults to TUI Format
Load enhanced defaults and mapping config, apply transformations, write TUI defaults file

Migrated from src/openproject_config_manager/transformer/
"""

from pathlib import Path
from typing import Dict, Any
import logging
import yaml
import json
import sys

# Import DefaultsTransformer from libraries
from phases.libraries.transformation import DefaultsTransformer

# Conditional imports to handle both module context and standalone execution
if __name__ == '__main__':
    # When running as standalone script, add parent to path for absolute imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


def execute_transform_defaults(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Transform Defaults to TUI Format
    Status: IMPLEMENTED
    
    Load enhanced defaults and mapping config, apply transformations, write TUI defaults file
    
    Args:
        context: Execution context containing:
            - enhanced_defaults_file: Path to enhanced defaults from Phase 1
            - enhanced_defaults: Enhanced defaults structure (optional)
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results including:
            - tui_defaults_file: Path to transformed defaults file
            - tui_defaults: Transformed defaults structure
            - transformation_summary: Summary of transformation
    """
    logger.info("Executing step: Transform Defaults to TUI Format")
    
    # Get enhanced defaults from context
    enhanced_defaults_file = context.get('enhanced_defaults_file')
    enhanced_defaults = context.get('enhanced_defaults')
    
    # Load enhanced defaults if not in context
    if not enhanced_defaults and enhanced_defaults_file:
        logger.info(f"Loading enhanced defaults from {enhanced_defaults_file}")
        with open(enhanced_defaults_file, 'r') as f:
            enhanced_defaults = yaml.safe_load(f)
    
    if not enhanced_defaults:
        raise ValueError("No enhanced defaults found in context or file")
    
    # Get project root (5 levels up from phase step directory)
    project_root = phase_dir.parent.parent
    
    # Transform defaults using the transformer
    transformer = DefaultsTransformer(project_root)
    tui_defaults = transformer.transform_enhanced_defaults(enhanced_defaults)
    
    # Write to output file
    output_dir = phase_dir / 'outputs' / 'tui'
    output_file = output_dir / 'tui_defaults.yml'
    transformer.write_tui_defaults_file(tui_defaults, output_file)
    
    # Create transformation summary
    transformation_summary = {
        'source_defaults_count': len(enhanced_defaults.get('defaults', {})),
        'transformed_defaults_count': len(tui_defaults.get('defaults', {})),
        'metadata_preserved': 'metadata' in tui_defaults,
        'transformation_successful': True
    }
    
    logger.info(f"Transformation complete: {transformation_summary['transformed_defaults_count']} defaults mapped")
    
    result = {
        'step': 'transform_defaults',
        'status': 'completed',
        'tui_defaults_file': str(output_file),
        'tui_defaults': tui_defaults,
        'transformation_summary': transformation_summary
    }
    
    logger.info("Step Transform Defaults to TUI Format completed")
    return result


def main():
    """Standalone entry point for testing this step."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Transform Defaults to TUI Format")
    parser.add_argument('--enhanced-defaults', required=True, help='Path to enhanced_defaults.yml')
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
            'enhanced_defaults_file': args.enhanced_defaults
        }
        
        # Execute step
        result = execute_transform_defaults(context, phase_dir)
        
        print("\n" + "=" * 70)
        print(f"✅ Step completed: {result.get('status', 'unknown')}")
        print("=" * 70)
        print(f"\n📊 Transformation Results:")
        
        if 'transformation_summary' in result:
            summary = result['transformation_summary']
            print(f"  • Source defaults: {summary.get('source_defaults_count', 0)}")
            print(f"  • Transformed defaults: {summary.get('transformed_defaults_count', 0)}")
            print(f"  • TUI defaults file: {result.get('tui_defaults_file', 'N/A')}")
        
        return 0 if result.get('status') == 'completed' else 1
        
    except Exception as e:
        print(f"\n❌ Step failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())


class TransformDefaultsStep:
    """Wrapper class for transform_defaults step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_2_tui_mapping"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute transform_defaults step.
        
        Args:
            context: Execution context
            
        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_transform_defaults(context, self.phase_dir)
        
        # Return in expected format
        return {
            "artifacts": result_data if isinstance(result_data, dict) else {"data": result_data}
        }
