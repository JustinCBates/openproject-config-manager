#!/usr/bin/env python3
"""
Test Control Flow Engine with Scaffolding
Demonstrates inserting discovery_prompt step into discovery phase.
"""

import sys
from pathlib import Path

# Add control-flow to path
control_flow_path = Path(__file__).parent.parent.parent / 'control-flow' / 'src'
sys.path.insert(0, str(control_flow_path))

from control_flow_engine.core.engine import ControlFlowManager
from control_flow_engine.core.scaffolder import (
    ScaffoldGenerator,
    StepInsertion,
    ImplementationStatus
)

import yaml
import json


def test_insert_discovery_prompt():
    """Test inserting discovery_prompt step with scaffolding."""
    
    print("🧪 Testing Control Flow Engine with Scaffolding")
    print("=" * 70)
    
    # Paths
    project_root = Path("/opt/openproject/external/config-manager")
    spec_file = project_root / "design_specs" / "control_flows.yml"
    
    # Load specification
    print(f"\n📖 Loading specification from {spec_file}")
    manager = ControlFlowManager(spec_file)
    
    # Load YAML directly since it's pure YAML, not markdown
    with open(spec_file, 'r') as f:
        spec_data = yaml.safe_load(f)
    
    # Populate manager's data structures
    manager.flows = spec_data.get('flows', {})
    manager.entry_points = spec_data.get('entry_points', {})
    manager.decision_points = spec_data.get('decision_points', {})
    manager.external_interfaces = spec_data.get('external_interfaces', {})
    
    print(f"✅ Loaded specification")
    print(f"   Flows: {list(manager.flows.keys())}")
    
    # Check discovery phase
    discovery_phase = manager.get_phase('main_config_flow', 'discovery')
    if not discovery_phase:
        print("❌ Discovery phase not found")
        return False
    
    print(f"\n📊 Discovery Phase")
    print(f"   Current steps: {len(discovery_phase.get('steps', []))}")
    for step in discovery_phase.get('steps', []):
        print(f"   - {step.get('step_id')}: {step.get('name')}")
    
    # Define new step
    print(f"\n🆕 Defining new step: discovery_prompt")
    new_step_insertion = StepInsertion(
        step_id="discovery_prompt",
        name="Discovery Configuration Prompt",
        sequence=0,
        description="Ask user whether to use automatic system discovery or manual configuration",
        status=ImplementationStatus.PLANNED,
        step_type="interactive",
        phase_id="discovery",
        phase_sequence=1,
        create_scaffolding=True,
        is_tui_form=True,
        layout_file_name="discovery_prompt.layout.yml",
        use_defaults_file=False,
        generate_mock_responses=True,
        mock_responses={
            "use_discovery": True,
            "discovery_method": "automatic"
        }
        # No insert_before - will append to end (or beginning since it's empty)
    )
    
    # Create step data for YAML
    step_data = {
        'step_id': new_step_insertion.step_id,
        'name': new_step_insertion.name,
        'type': new_step_insertion.step_type,
        'description': new_step_insertion.description,
        'status': new_step_insertion.status.value,
        'dependencies': [],
        'artifacts_produced': ['discovery_config']
    }
    
    # Insert into phase (YAML only, no scaffolding yet)
    print(f"\n🔄 Inserting step into control_flows.yml")
    success = manager.insert_step_into_phase(
        flow_name='main_config_flow',
        phase_id='discovery',
        step_data=step_data
        # No insert_before - will append
    )
    
    if not success:
        print("❌ Failed to insert step into YAML")
        return False
    
    # Show updated phase
    discovery_phase = manager.get_phase('main_config_flow', 'discovery')
    print(f"\n✅ Updated Discovery Phase")
    print(f"   Total steps: {len(discovery_phase.get('steps', []))}")
    for i, step in enumerate(discovery_phase.get('steps', [])):
        print(f"   {i}. {step.get('step_id')}: {step.get('name')}")
    
    # Save updated YAML
    print(f"\n💾 Saving updated specification")
    manager.save_specification()
    
    # Create scaffolding
    print(f"\n🏗️  Creating directory scaffolding")
    scaffolder = ScaffoldGenerator(project_root)
    
    phase_dir = project_root / "phases" / "phase_1_discovery"
    created_files = scaffolder.create_step_scaffolding(
        step=new_step_insertion,
        base_path=phase_dir
    )
    
    print(f"\n✅ Created files:")
    for file_type, file_path in created_files.items():
        print(f"   {file_type}: {file_path}")
    
    # Verify files exist
    print(f"\n🔍 Verifying created files...")
    all_exist = True
    for file_type, file_path in created_files.items():
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {file_type}: {file_path.name}")
        all_exist = all_exist and exists
    
    if all_exist:
        print(f"\n🎉 SUCCESS! All files created successfully")
        return True
    else:
        print(f"\n❌ FAILED: Some files were not created")
        return False


if __name__ == "__main__":
    success = test_insert_discovery_prompt()
    sys.exit(0 if success else 1)
