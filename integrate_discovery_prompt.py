#!/usr/bin/env python3
"""
Integrate existing discovery_prompt step into orchestrator.
The step already exists in YAML and has scaffolding, but needs orchestrator integration.
"""

from pathlib import Path
import sys

# Add control-flow to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'control-flow' / 'src'))

from control_flow_engine.core.orchestrator_updater import update_orchestrator_with_step


def main():
    """Integrate discovery_prompt into orchestrator_discovery.py."""
    
    orchestrator_file = Path(__file__).parent / 'phases' / 'phase_1_discovery' / 'orchestrator_discovery.py'
    
    print("=" * 70)
    print("Integrating discovery_prompt step into orchestrator")
    print("=" * 70)
    print(f"Orchestrator: {orchestrator_file}")
    print()
    
    if not orchestrator_file.exists():
        print(f"❌ Orchestrator file not found: {orchestrator_file}")
        return 1
    
    # Integrate step
    success = update_orchestrator_with_step(
        orchestrator_path=orchestrator_file,
        step_id="discovery_prompt",
        step_sequence=0,  # First step
        step_class_name="DiscoveryPromptStep",
        description="Ask user whether to use automatic system discovery or manual configuration"
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS - discovery_prompt integrated!")
        print("=" * 70)
        print("\nUpdates made:")
        print("  ✅ Added import: from .step_0_discovery_prompt.discovery_prompt import DiscoveryPromptStep")
        print("  ✅ Added step execution in execute() method")
        print()
        print("Next steps:")
        print("  1. Review: phases/phase_1_discovery/orchestrator_discovery.py")
        print("  2. Test: python phases/phase_1_discovery/orchestrator_discovery.py")
        print()
    else:
        print("\n❌ Failed to integrate discovery_prompt")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
