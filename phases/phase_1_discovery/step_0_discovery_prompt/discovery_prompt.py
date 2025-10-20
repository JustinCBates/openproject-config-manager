#!/usr/bin/env python3
"""
Discovery Configuration Prompt
Status: PLANNED

Ask user whether to use automatic system discovery or manual configuration

This step uses TUI Form Engine for interactive user input.
"""


from pathlib import Path
from typing import Dict, Any
import logging
from src.openproject_config_manager.tui_adapter import FormRenderer

logger = logging.getLogger(__name__)


def execute_discovery_prompt(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Discovery Configuration Prompt
    
    This step uses TUI Form Engine for interactive user input.
    
    Args:
        context: Execution context (may contain mock_responses)
        phase_dir: Phase directory path
        
    Returns:
        Dict containing:
        - User responses from the form
        - Any derived configuration
    """
    logger.info("=" * 70)
    logger.info("Discovery Configuration Prompt")
    logger.info("=" * 70)
    
    # Path to TUI form layout
    layout_path = phase_dir / "step_0_discovery_prompt" / "discovery_prompt.layout.yml"
    
    if not layout_path.exists():
        logger.error(f"❌ Layout file not found: {layout_path}")
        return _get_default_config()
    
    # Create TUI renderer
    renderer = FormRenderer()
    
    # Check for mock mode
    mock_responses = None
    if 'mock_responses' in context and 'discovery_prompt' in context['mock_responses']:
        mock_responses = context['mock_responses']['discovery_prompt']
        logger.info("🤖 Running in MOCK mode")
    
    # Render the form
    try:
        response = renderer.render_flow(
            flow_path=str(layout_path),
            mock_responses=mock_responses,
            quiet=context.get('quiet', False)
        )
        
        responses = response.get('responses', {})
        
        logger.info(f"✅ Collected {len(responses)} responses")
        
        return {
            'step': 'discovery_prompt',
            'responses': responses,
            'status': 'completed'
        }
        
    except KeyboardInterrupt:
        logger.warning("⚠️  User cancelled")
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return _get_default_config()


def _get_default_config() -> Dict[str, Any]:
    """Fallback configuration when form cannot be rendered."""
    return {
        'step': 'discovery_prompt',
        'status': 'fallback',
        'responses': {}
    }


if __name__ == "__main__":
    # Test standalone
    import json
    logging.basicConfig(level=logging.INFO)
    
    # Load mock responses
    mock_file = Path(__file__).parent / "mock_responses.json"
    mock_data = {}
    if mock_file.exists():
        with open(mock_file) as f:
            mock_data = json.load(f)
    
    test_context = {
        'test_mode': True,
        'mock_responses': {'discovery_prompt': mock_data}
    }
    test_phase_dir = Path(__file__).parent.parent
    
    result = execute_discovery_prompt(test_context, test_phase_dir)
    print(f"\nResult: {json.dumps(result, indent=2)}")


class DiscoveryPromptStep:
    """Wrapper class for discovery_prompt step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_1_discovery"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute discovery_prompt step.
        
        Args:
            context: Execution context
            
        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_discovery_prompt(context, self.phase_dir)
        
        # Return in expected format
        return {
            "artifacts": result_data if isinstance(result_data, dict) else {"data": result_data}
        }
