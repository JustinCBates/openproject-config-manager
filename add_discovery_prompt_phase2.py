#!/usr/bin/env python3
"""
Add discovery_prompt step using Phase 2 ControlFlowDesigner (dict format).
This demonstrates the complete automation: YAML update + scaffolding + orchestrator integration.
"""

from pathlib import Path
import sys

# Add control-flow to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'control-flow' / 'src'))

from control_flow_engine.core.designer import ControlFlowDesigner, ImplementationStatus
from control_flow_engine.core.scaffolder import StepInsertion


def main():
    """Add discovery_prompt step to config-manager."""
    
    # Paths
    project_root = Path(__file__).parent
    spec_file = project_root / 'design_specs' / 'control_flows.yml'
    
    print("=" * 70)
    print("Adding discovery_prompt step using Phase 2 (Dict Format)")
    print("=" * 70)
    print(f"Project: {project_root}")
    print(f"Spec: {spec_file}")
    print()
    
    # Load existing spec
    designer = ControlFlowDesigner.from_existing(
        spec_file=spec_file,
        project_root=project_root
    )
    
    # Define discovery_prompt step
    discovery_prompt_step = StepInsertion(
        step_id="discovery_prompt",
        name="Discovery Configuration Prompt",
        sequence=0,  # First step in phase
        description="Ask user whether to use automatic system discovery or manual configuration",
        status=ImplementationStatus.PLANNED,
        step_type="interactive",
        phase_id="discovery",
        phase_sequence=1,  # Phase 1
        is_tui_form=True,  # This is a TUI form
        create_scaffolding=True
        # No insert_before/after - will append to end, then we can renumber
    )
    
    # Add step with complete automation
    print("\nAdding step with full Phase 2 automation...")
    print("  - Updating YAML specification")
    print("  - Creating step scaffolding")
    print("  - Updating orchestrator imports and execution")
    print()
    
    success = designer.add_step(
        phase_id="discovery",
        step=discovery_prompt_step,
        flow_name="main_config_flow",
        create_scaffolding=True,
        update_orchestrator=True
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS - discovery_prompt step added!")
        print("=" * 70)
        print("\nWhat was created:")
        print("  ✅ YAML: design_specs/control_flows.yml updated")
        print("  ✅ Directory: phases/phase_1_discovery/step_0_discovery_prompt/")
        print("  ✅ Files:")
        print("     - __init__.py")
        print("     - discovery_prompt.py (implementation)")
        print("     - discovery_prompt.layout.yml (TUI form)")
        print("     - mock_responses.json (test data)")
        print("     - README.md (documentation)")
        print("  ✅ Orchestrator: orchestrator_discovery.py updated with:")
        print("     - Import statement")
        print("     - Step execution code")
        print()
        print("Next steps:")
        print("  1. Review generated files")
        print("  2. Customize discovery_prompt.layout.yml for your needs")
        print("  3. Implement logic in discovery_prompt.py")
        print("  4. Test: python phases/phase_1_discovery/orchestrator_discovery.py")
        print()
    else:
        print("\n❌ Failed to add discovery_prompt step")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
