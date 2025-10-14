"""
Step: Collect User Configuration
Load TUI layout and defaults, render interactive form, collect user input, save configuration

Migrated from src/openproject_config_manager/collector/tui_collector.py
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import json
import yaml
from datetime import datetime
import sys

# =============================================================================
# PATH CONFIGURATION
# =============================================================================
# These constants define the step's location in the project structure.

# PHASE_SEQUENCE: Physical position in phases directory (changeable during reordering)
PHASE_SEQUENCE = int(os.getenv('PHASE_SEQUENCE', '3'))

# PHASE_ID: Logical phase identifier (stable, never changes)
PHASE_ID = 'collection'

# Computed paths
PHASE_DIR_NAME = f"phase_{PHASE_SEQUENCE}_{PHASE_ID}"
PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent)).resolve()
PHASE_DIR = PROJECT_ROOT / "phases" / PHASE_DIR_NAME
OUTPUT_DIR = PHASE_DIR / "outputs"

# =============================================================================

# Conditional imports to handle both module context and standalone execution
if __name__ == '__main__':
    # When running as standalone script, add parent to path for absolute imports
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT.parent / "control-flow/src"))
    from control_flow_engine.runtime import PathResolver, PathResolutionError
else:
    # When imported as module
    try:
        from control_flow_engine.runtime import PathResolver, PathResolutionError
    except ImportError:
        PathResolver = None
        PathResolutionError = Exception

# Import the lightweight TUI Form Engine renderer (end-user interface)
try:
    from tui_form_engine.renderer import FormRenderer
    from tui_form_engine.core.exceptions import FlowValidationError, FlowExecutionError
    from tui_form_engine.preprocessing import LayoutPreprocessor, DefaultsPreprocessor
    TUI_ENGINE_AVAILABLE = True
except ImportError:
    TUI_ENGINE_AVAILABLE = False
    FormRenderer = None
    FlowValidationError = Exception
    FlowExecutionError = Exception
    LayoutPreprocessor = None
    DefaultsPreprocessor = None

logger = logging.getLogger(__name__)


class TUIConfigCollector:
    """
    Collects OpenProject configuration using TUI Form Engine flows.
    
    Phase 3 Workflow:
    1. Load TUI defaults from Phase 2 output (tui_defaults.yml)
    2. Load YAML flow definition from layouts/
    3. Execute flow with TUI Form Engine (collect user input)
    4. Save user responses
    5. Output collected configuration for Phase 4 validation
    
    Note: This is a simplified version that focuses on collection only.
    Validation is handled by Phase 4.
    """
    
    def __init__(self, 
                 layouts_dir: Optional[Path] = None,
                 output_dir: Optional[Path] = None,
                 tui_defaults_file: Optional[Path] = None):
        """
        Initialize the TUI Configuration Collector.
        
        Args:
            layouts_dir: Directory containing layout YAML files
            output_dir: Directory for output files
            tui_defaults_file: Path to Phase 2 TUI defaults file
        """
        # Use layouts directory relative to this file if not specified
        if layouts_dir is None:
            layouts_dir = Path(__file__).parent / "layouts"
        
        self.layouts_dir = Path(layouts_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.tui_defaults_file = Path(tui_defaults_file) if tui_defaults_file else None
        
        # Initialize TUI Form Renderer (end-user interface)
        if TUI_ENGINE_AVAILABLE:
            self.renderer = FormRenderer()
        else:
            self.renderer = None
            logger.warning("TUI Form Engine not available - interactive collection disabled")
        
        # Load TUI defaults from Phase 2 if provided
        self.tui_defaults = {}
        if self.tui_defaults_file and self.tui_defaults_file.exists():
            self._load_tui_defaults()
    
    def _load_tui_defaults(self):
        """Load TUI defaults from Phase 2 output."""
        try:
            with open(self.tui_defaults_file, 'r') as f:
                self.tui_defaults = yaml.safe_load(f) or {}
            logger.info(f"Loaded TUI defaults from {self.tui_defaults_file}")
        except Exception as e:
            logger.warning(f"Failed to load TUI defaults: {e}")
            self.tui_defaults = {}
    
    def _expand_sublayouts(self, flow_data: Dict[str, Any], flow_path: Path) -> Dict[str, Any]:
        """
        Expand sublayout references AND merge hierarchical defaults using TUI Engine preprocessors.
        
        This method uses the TUI Form Engine's LayoutPreprocessor and DefaultsPreprocessor
        to implement the Virtual Layout Reconstruction and Virtual Defaults Merging systems.
        
        Args:
            flow_data: The main flow definition (with sublayout references)
            flow_path: Path to the main flow file (for resolving relative paths)
            
        Returns:
            Flow data with sublayouts expanded and unified defaults merged
        """
        logger.info(f"🔄 Preprocessing layout with TUI Engine preprocessors...")
        
        # Use LayoutPreprocessor for virtual layout reconstruction
        layout_preprocessor = LayoutPreprocessor(layouts_dir=flow_path.parent)
        virtual_layout = layout_preprocessor.reconstruct_virtual_layout(
            layout_path=flow_path,
            save_virtual=True,  # Save for debugging
            output_path=self.output_dir / f"{flow_path.stem}_virtual.yml"
        )
        
        # Use DefaultsPreprocessor for hierarchical defaults merging
        defaults_preprocessor = DefaultsPreprocessor(layouts_dir=flow_path.parent)
        unified_defaults = defaults_preprocessor.merge_defaults(
            layout_path=flow_path,
            layout_data=flow_data,  # Pass original data for sublayout discovery
            save_unified=True,
            output_path=self.output_dir / "unified_defaults.yml"
        )
        
        # Update virtual layout to reference the unified defaults file
        if unified_defaults:
            virtual_layout['defaults_file'] = str((self.output_dir / "unified_defaults.yml").absolute())
        
        return virtual_layout
    
    def collect_configuration(
        self, 
        flow_name: str = "config_tui.layout",
    ) -> Dict[str, Any]:
        """
        Execute the configuration collection workflow.
        
        This runs the interactive TUI to collect configuration from the user.
        The flow definition is preprocessed to expand any sublayout references
        before being rendered.
        
        Args:
            flow_name: Name of the flow YAML file (without .yml extension)
            
        Returns:
            Dict containing the collected user configuration
            
        Raises:
            FlowValidationError: If flow definition is invalid
            FlowExecutionError: If flow execution fails
            RuntimeError: If TUI engine is not available
        """
        if not TUI_ENGINE_AVAILABLE:
            raise RuntimeError(
                "TUI Form Engine not available. Install tui-form-designer: pip install -e external/tui-form-designer/"
            )
        
        if not self.renderer:
            raise RuntimeError("TUI renderer not initialized")
        
        logger.info(f"🎯 Starting OpenProject configuration collection...")
        
        # Step 1: Load and preprocess the flow definition
        logger.info(f"📋 Executing flow: {flow_name}")
        try:
            flow_path = self.layouts_dir / f"{flow_name}.yml"
            
            if not flow_path.exists():
                raise FileNotFoundError(f"Flow file not found: {flow_path}")
            
            # Load the flow definition
            with open(flow_path, 'r') as f:
                flow_data = yaml.safe_load(f)
            
            # Expand sublayouts and merge hierarchical defaults
            logger.info(f"🔄 Preprocessing flow definition...")
            flow_data = self._expand_sublayouts(flow_data, flow_path)
            
            # Create a temporary expanded flow file in the layouts directory (not outputs)
            # This ensures relative paths still work correctly
            expanded_flow_path = self.layouts_dir / f"{flow_name}_expanded.yml"
            with open(expanded_flow_path, 'w') as f:
                yaml.safe_dump(flow_data, f, default_flow_style=False, sort_keys=False)
            logger.info(f"✅ Expanded flow saved to: {expanded_flow_path}")
            
            # Run interactive TUI to collect user responses
            logger.info(f"🎨 Starting interactive configuration...")
            logger.info(f"📄 Flow path: {expanded_flow_path}")
            logger.info(f"📊 Flow has {len(flow_data.get('steps', []))} steps")
            
            flow_response = self.renderer.render_flow(
                flow_path=str(expanded_flow_path),
                mock_responses=None,
                quiet=False
            )
            user_responses = flow_response["responses"]
                
        except (FlowValidationError, FlowExecutionError) as e:
            logger.error(f"❌ Flow execution failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during flow execution: {e}")
            raise
        
        # Step 2: Save raw user responses
        responses_file = self.output_dir / f"{flow_name}_responses.json"
        with open(responses_file, 'w') as f:
            json.dump(user_responses, f, indent=2)
        logger.info(f"💾 User responses saved: {responses_file}")
        
        # Step 3: Generate collected configuration for Phase 4
        collected_config = self._generate_collected_config(user_responses, flow_name)
        
        # Step 4: Save collected configuration as YAML
        config_file = self.output_dir / "collected_configuration.yml"
        with open(config_file, 'w') as f:
            yaml.dump(collected_config, f, default_flow_style=False, sort_keys=False)
        logger.info(f"✅ Collected configuration saved: {config_file}")
        
        logger.info(f"🎉 Configuration collection complete!")
        return collected_config
    
    def _generate_collected_config(self, responses: Dict[str, Any], flow_name: str) -> Dict[str, Any]:
        """
        Generate collected configuration from user responses.
        
        This is a simple pass-through for Phase 3. Phase 4 will handle
        validation and transformation.
        
        Args:
            responses: User responses from TUI flow
            flow_name: Name of the flow that was executed
            
        Returns:
            Dict with collected configuration structure
        """
        return {
            'metadata': {
                'collected_by': 'config-manager-phase-3',
                'timestamp': datetime.now().isoformat(),
                'flow_name': flow_name,
                'flow_version': '1.0.0',
            },
            'user_responses': responses,
            'tui_defaults_applied': bool(self.tui_defaults),
            'collection_method': 'tui_form_engine' if TUI_ENGINE_AVAILABLE else 'mock',
        }
    
    def test_flow(self, flow_name: str, mock_responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test flow execution with mock responses (for development/CI).
        
        Args:
            flow_name: Name of the flow to test
            mock_responses: Mock responses for testing
            
        Returns:
            Collected configuration dict
        """
        logger.info(f"🧪 Testing flow: {flow_name}")
        
        try:
            result = self.collect_configuration(
                flow_name=flow_name,
                mock_responses=mock_responses
            )
            
            logger.info(f"✅ Flow test successful")
            return result
            
        except Exception as e:
            logger.error(f"❌ Flow test failed: {e}")
            raise


def execute_collect_user_configuration(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    Collect User Configuration
    Status: IMPLEMENTED
    
    Load TUI layout and defaults, render interactive form, collect user input, save configuration
    
    Args:
        context: Execution context containing:
            - tui_defaults_file: Path to Phase 2 TUI defaults
            - flow_name: Optional flow name (default: config_tui.layout)
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results including collected configuration
    """
    logger.info("Executing step: Collect User Configuration")
    
    # Get input from context
    tui_defaults_file = context.get('tui_defaults_file')
    flow_name = context.get('flow_name', 'config_tui.layout')
    
    # Setup paths
    step_dir = phase_dir / "step_1_collect_user_configuration"
    layouts_dir = step_dir / "layouts"
    output_dir = phase_dir / "outputs"
    
    logger.info(f"Layouts directory: {layouts_dir}")
    logger.info(f"Output directory: {output_dir}")
    if tui_defaults_file:
        logger.info(f"TUI defaults file: {tui_defaults_file}")
    
    # Initialize collector
    collector = TUIConfigCollector(
        layouts_dir=layouts_dir,
        output_dir=output_dir,
        tui_defaults_file=Path(tui_defaults_file) if tui_defaults_file else None
    )
    
    # Execute collection
    try:
        collected_config = collector.collect_configuration(flow_name=flow_name)
        
        result = {
            'step': 'collect_user_configuration',
            'status': 'completed',
            'collected_config': collected_config,
            'output_file': str(output_dir / "collected_configuration.yml"),
            'responses_file': str(output_dir / f"{flow_name}_responses.json")
        }
        
        logger.info("Step Collect User Configuration completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to collect user configuration: {e}")
        raise


def main():
    """Main entry point for standalone testing."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Phase 3 - TUI Configuration Collector"
    )
    parser.add_argument(
        "flow_name", 
        nargs="?", 
        default="config_tui.layout", 
        help="Name of the flow to execute (default: config_tui.layout)"
    )
    parser.add_argument(
        "--tui-defaults",
        help="Path to Phase 2 TUI defaults file"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: use PathResolver to determine phase output dir)"
    )
    parser.add_argument(
        "--layouts-dir",
        help="Layouts directory (default: ./layouts)"
    )
    parser.add_argument(
        "--show-paths",
        action='store_true',
        help="Display path configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Show path configuration if requested
    if args.show_paths:
        print("\n" + "=" * 70)
        print("PATH CONFIGURATION")
        print("=" * 70)
        print(f"\n📍 Phase Identity:")
        print(f"   PHASE_SEQUENCE: {PHASE_SEQUENCE}")
        print(f"   PHASE_ID: {PHASE_ID}")
        print(f"   PHASE_DIR_NAME: {PHASE_DIR_NAME}")
        print(f"\n📂 Computed Paths:")
        print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
        print(f"   PHASE_DIR: {PHASE_DIR}")
        print(f"   OUTPUT_DIR: {OUTPUT_DIR}")
        
        # Validate against PathResolver
        if PathResolver:
            try:
                path_resolver = PathResolver.from_execution_context(__file__)
                resolver_phase_dir = path_resolver.resolve_phase_directory(PHASE_ID)
                resolver_output_dir = path_resolver.resolve_phase_output_dir(PHASE_ID)
                
                print(f"\n✅ PathResolver Validation:")
                
                if Path(resolver_phase_dir) == PHASE_DIR:
                    print(f"   Phase directory: MATCHES")
                else:
                    print(f"   Phase directory: MISMATCH")
                    print(f"     Computed: {PHASE_DIR}")
                    print(f"     Resolver: {resolver_phase_dir}")
                
                if Path(resolver_output_dir) == OUTPUT_DIR:
                    print(f"   Output directory: MATCHES")
                else:
                    print(f"   Output directory: MISMATCH")
                    print(f"     Computed: {OUTPUT_DIR}")
                    print(f"     Resolver: {resolver_output_dir}")
            except Exception as e:
                print(f"\n⚠️  PathResolver validation failed: {e}")
        else:
            print(f"\n⚠️  PathResolver not available")
        
        print("\n" + "=" * 70)
        return 0
    
    # Setup paths using PathResolver
    step_dir = Path(__file__).parent
    layouts_dir = Path(args.layouts_dir) if args.layouts_dir else (step_dir / "layouts")
    
    # Try to use PathResolver for output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    elif PathResolver:
        try:
            path_resolver = PathResolver.from_execution_context(__file__)
            output_dir = path_resolver.resolve_phase_output_dir('collection', create=True)
            print(f"📍 Using PathResolver: output_dir = {output_dir}")
        except Exception as e:
            print(f"⚠️  PathResolver failed ({e}), falling back to relative path")
            output_dir = step_dir.parent / "outputs"
    else:
        # Fallback to old behavior if PathResolver not available
        output_dir = step_dir.parent / "outputs"
    
    # Initialize collector
    collector = TUIConfigCollector(
        layouts_dir=layouts_dir,
        output_dir=output_dir,
        tui_defaults_file=Path(args.tui_defaults) if args.tui_defaults else None
    )
    
    try:
        # Interactive configuration collection
        config = collector.collect_configuration(args.flow_name)
        
        print(f"\n🎉 Configuration collection complete!")
        print(f"📁 Files generated:")
        print(f"  - User responses: {output_dir}/{args.flow_name}_responses.json")
        print(f"  - Collected config: {output_dir}/collected_configuration.yml")
        print(f"\n✅ Ready for Phase 4 validation!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Configuration collection failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
