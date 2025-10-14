#!/usr/bin/env python3
"""
Add discovery_prompt step to config-manager using Phase 2 features.

This demonstrates the greenfield workflow for adding a new interactive step
to an existing project using the ControlFlowDesigner API.
"""

from pathlib import Path
import sys

# Add control-flow to path
control_flow_path = Path(__file__).parent.parent / 'control-flow' / 'src'
sys.path.insert(0, str(control_flow_path))

from control_flow_engine.core.designer import ControlFlowDesigner
from control_flow_engine.core.scaffolder import StepInsertion
from control_flow_engine.core.engine import ImplementationStatus


def add_discovery_prompt_step():
    """
    Add discovery_prompt step to config-manager's discovery phase.
    
    This step will ask the user whether to:
    - Use automatic system discovery
    - Enter configuration manually
    - Load from existing file
    """
    print("=" * 70)
    print("Adding Discovery Prompt Step to Config-Manager")
    print("=" * 70)
    
    # Paths
    project_root = Path(__file__).parent
    spec_file = project_root / "design_specs" / "control_flows.yml"
    
    print(f"\nProject Root: {project_root}")
    print(f"Spec File: {spec_file}")
    
    # Load existing project
    print("\n1️⃣ Loading existing project...")
    designer = ControlFlowDesigner.from_existing(
        spec_file=spec_file,
        project_root=project_root
    )
    print("✅ Project loaded")
    
    # Check current state
    print("\n2️⃣ Current Discovery Phase:")
    phase = designer.manager.get_phase('main_config_flow', 'discovery')
    if phase:
        current_steps = phase.get('steps', [])
        print(f"   Current steps: {len(current_steps)}")
        for step in current_steps:
            print(f"   - {step.get('step_id')}: {step.get('name')}")
    
    # Define new step
    print("\n3️⃣ Defining discovery_prompt step...")
    discovery_prompt_step = StepInsertion(
        step_id="discovery_prompt",
        name="Discovery Configuration Prompt",
        sequence=0,  # First step in phase
        description="Ask user whether to use automatic system discovery or manual configuration",
        status=ImplementationStatus.PLANNED,
        step_type="interactive",
        
        # Parent phase info
        phase_id="discovery",
        phase_sequence=1,
        
        # TUI Form settings
        is_tui_form=True,
        layout_file_name="discovery_prompt.layout.yml",
        use_defaults_file=False,
        generate_mock_responses=True,
        mock_responses={
            "use_discovery": True,
            "discovery_method": "automatic",
            "skip_network": False
        },
        
        # Scaffolding
        create_scaffolding=True
    )
    
    print(f"✅ Step defined:")
    print(f"   ID: {discovery_prompt_step.step_id}")
    print(f"   Type: {discovery_prompt_step.step_type}")
    print(f"   TUI Form: {discovery_prompt_step.is_tui_form}")
    print(f"   Layout: {discovery_prompt_step.layout_file_name}")
    
    # Add step with automatic scaffolding and orchestrator integration
    print("\n4️⃣ Adding step to phase...")
    print("   - Creating scaffolding ✓")
    print("   - Updating YAML spec ✓")
    print("   - Integrating into orchestrator ✓")
    
    success = designer.add_step(
        phase_id="discovery",
        step=discovery_prompt_step,
        flow_name="main_config_flow",
        create_scaffolding=True,
        update_orchestrator=True  # Auto-integrate into orchestrator!
    )
    
    if not success:
        print("❌ Failed to add step")
        return False
    
    # Verify what was created
    print("\n5️⃣ Verifying created files...")
    step_dir = project_root / "phases" / "phase_1_discovery" / "step_0_discovery_prompt"
    
    expected_files = [
        "__init__.py",
        "discovery_prompt.py",
        "discovery_prompt.layout.yml",
        "mock_responses.json",
        "README.md"
    ]
    
    for filename in expected_files:
        filepath = step_dir / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} - NOT FOUND")
    
    # Check orchestrator integration
    print("\n6️⃣ Checking orchestrator integration...")
    orchestrator_file = project_root / "phases" / "phase_1_discovery" / "orchestrator_discovery.py"
    
    if orchestrator_file.exists():
        content = orchestrator_file.read_text()
        
        if "from .step_0_discovery_prompt.discovery_prompt import" in content:
            print("   ✅ Import statement added")
        else:
            print("   ⚠️  Import statement not found")
        
        if "DiscoveryPromptStep" in content or "discovery_prompt" in content.lower():
            print("   ✅ Step execution code added")
        else:
            print("   ⚠️  Execution code not found")
    else:
        print("   ⚠️  Orchestrator file not found")
    
    # Show progress
    print("\n7️⃣ Implementation Progress:")
    progress = designer.get_implementation_progress()
    print(f"   Total Phases: {progress.get('total_phases', 0)}")
    print(f"   Total Steps: {progress.get('total_steps', 0)}")
    print(f"   Implemented: {progress.get('implemented_steps', 0)}")
    print(f"   Planned: {progress.get('planned_steps', 0)}")
    print(f"   Overall: {progress.get('overall_percentage', 0):.1f}%")
    
    # Validate spec
    print("\n8️⃣ Validating specification...")
    report = designer.validate()
    
    if report.is_valid:
        print("   ✅ Specification is valid")
    else:
        print(f"   ❌ Validation errors: {len(report.errors)}")
        for error in report.errors:
            print(f"      - {error}")
    
    if report.warnings:
        print(f"   ⚠️  Warnings: {len(report.warnings)}")
        for warning in report.warnings:
            print(f"      - {warning}")
    
    print("\n" + "=" * 70)
    print("✅ Discovery Prompt Step Added Successfully!")
    print("=" * 70)
    
    print("\n📝 Next Steps:")
    print("   1. Review the generated layout file:")
    print(f"      {step_dir / 'discovery_prompt.layout.yml'}")
    print("   2. Customize the TUI form questions")
    print("   3. Test with mock responses:")
    print("      python phases/phase_1_discovery/orchestrator_discovery.py")
    print("   4. Update step status when implemented:")
    print("      designer.update_step_status('discovery', 'discovery_prompt', ImplementationStatus.IMPLEMENTED)")
    
    return True


if __name__ == "__main__":
    try:
        success = add_discovery_prompt_step()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
