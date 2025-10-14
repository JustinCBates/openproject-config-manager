#!/usr/bin/env python3
"""
Add regeneration markers to orchestrator_discovery.py and regenerate from spec.
"""

from pathlib import Path
import sys

# Add control-flow to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'control-flow' / 'src'))

from control_flow_engine.core.orchestrator_regenerator import OrchestratorRegenerator


def add_markers_to_orchestrator():
    """Add GENERATED markers to existing orchestrator."""
    
    orchestrator_file = Path(__file__).parent / 'phases' / 'phase_1_discovery' / 'orchestrator_discovery.py'
    
    print("=" * 70)
    print("Adding regeneration markers to orchestrator_discovery.py")
    print("=" * 70)
    
    content = orchestrator_file.read_text()
    
    # Split into sections
    lines = content.split('\n')
    new_lines = []
    
    in_imports = False
    in_execute = False
    found_step_execution_start = False
    
    for i, line in enumerate(lines):
        # Check if we're at the step imports
        if line.startswith('from .step_') and not in_imports:
            # Add marker before first step import
            new_lines.append("# === GENERATED: STEP_IMPORTS - DO NOT EDIT ===")
            in_imports = True
            new_lines.append(line)
        elif in_imports and not line.startswith('from .step_') and not line.strip().startswith('#'):
            # End of imports section
            new_lines.append("# === END GENERATED: STEP_IMPORTS ===")
            in_imports = False
            new_lines.append(line)
        elif 'def execute(self, context:' in line:
            new_lines.append(line)
            in_execute = True
        elif in_execute and line.strip().startswith('# Step 1:') and not found_step_execution_start:
            # Found start of step execution
            new_lines.append("")
            new_lines.append("        result = {'artifacts': {}}")
            new_lines.append("")
            new_lines.append("        # === GENERATED: STEP_EXECUTION - DO NOT EDIT ===")
            found_step_execution_start = True
            new_lines.append(line)
        elif in_execute and line.strip().startswith('return {'):
            # End of step execution
            if found_step_execution_start:
                new_lines.append("        # === END GENERATED: STEP_EXECUTION ===")
                new_lines.append("")
            new_lines.append(line)
            in_execute = False
        else:
            new_lines.append(line)
    
    # Write back
    new_content = '\n'.join(new_lines)
    orchestrator_file.write_text(new_content)
    
    print(f"✅ Added markers to {orchestrator_file.name}")
    print()
    
    return orchestrator_file


def main():
    """Add markers and regenerate."""
    
    # Paths
    spec_file = Path(__file__).parent / 'design_specs' / 'control_flows.yml'
    
    print("Step 1: Adding regeneration markers...")
    orchestrator_file = add_markers_to_orchestrator()
    
    print("Step 2: Regenerating from spec...")
    print()
    
    # Regenerate
    regenerator = OrchestratorRegenerator(spec_file)
    
    success = regenerator.regenerate_phase_orchestrator(
        orchestrator_file=orchestrator_file,
        phase_id='discovery',
        flow_name='main_config_flow'
    )
    
    if success:
        print()
        print("=" * 70)
        print("✅ SUCCESS - Orchestrator regenerated from spec!")
        print("=" * 70)
        print()
        print("What changed:")
        print("  ✅ Step imports updated from control_flows.yml")
        print("  ✅ Step execution sequence regenerated")
        print("  ✅ Custom code preserved (logging, __init__, main(), etc.)")
        print()
        print("Next steps:")
        print("  1. Review: phases/phase_1_discovery/orchestrator_discovery.py")
        print("  2. Test: python phases/phase_1_discovery/orchestrator_discovery.py")
        print()
        return 0
    else:
        print("\n❌ Regeneration failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
