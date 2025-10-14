#!/usr/bin/env python3
"""
Generate scaffolding for the existing discovery_prompt step in config-manager.

The step already exists in the YAML spec (status: PLANNED), but the scaffolding
hasn't been generated yet. This script creates all the necessary files.
"""

from pathlib import Path
import sys

# Add control-flow to path
control_flow_path = Path(__file__).parent.parent / 'control-flow' / 'src'
sys.path.insert(0, str(control_flow_path))

from control_flow_engine.core.scaffolder import ScaffoldGenerator, StepInsertion
from control_flow_engine.core.engine import ImplementationStatus


def generate_discovery_prompt_scaffolding():
    """
    Generate scaffolding for discovery_prompt step.
    
    The step is already defined in control_flows.yml, we just need to
    create the directory structure and files.
    """
    print("=" * 70)
    print("Generating Discovery Prompt Step Scaffolding")
    print("=" * 70)
    
    # Paths
    project_root = Path(__file__).parent
    phase_dir = project_root / "phases" / "phase_1_discovery"
    
    print(f"\nProject Root: {project_root}")
    print(f"Phase Directory: {phase_dir}")
    
    # Define step (matching what's in YAML)
    print("\n1️⃣ Defining discovery_prompt step...")
    discovery_prompt_step = StepInsertion(
        step_id="discovery_prompt",
        name="Discovery Configuration Prompt",
        sequence=0,  # First step in phase (before existing steps)
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
    
    # Generate scaffolding
    print("\n2️⃣ Creating scaffolding...")
    scaffolder = ScaffoldGenerator(project_root)
    
    created_files = scaffolder.create_step_scaffolding(
        step=discovery_prompt_step,
        base_path=phase_dir
    )
    
    # Show created files
    print("\n3️⃣ Created files:")
    for file_type, filepath in created_files.items():
        print(f"   ✅ {file_type}: {filepath.relative_to(project_root)}")
    
    # Verify all files exist
    print("\n4️⃣ Verifying files...")
    all_exist = True
    for file_type, filepath in created_files.items():
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"   ✅ {filepath.name} ({size} bytes)")
        else:
            print(f"   ❌ {filepath.name} - NOT FOUND")
            all_exist = False
    
    if not all_exist:
        print("\n❌ Some files were not created")
        return False
    
    # Show the layout file for customization
    print("\n5️⃣ Generated TUI Layout:")
    print("   " + "─" * 66)
    layout_file = created_files['layout']
    layout_content = layout_file.read_text()
    for line in layout_content.split('\n')[:20]:  # First 20 lines
        print(f"   {line}")
    print("   " + "─" * 66)
    print(f"   (Full file: {layout_file.relative_to(project_root)})")
    
    print("\n" + "=" * 70)
    print("✅ Scaffolding Generated Successfully!")
    print("=" * 70)
    
    print("\n📝 Next Steps:")
    print(f"\n1. Customize the TUI form layout:")
    print(f"   Edit: {layout_file.relative_to(project_root)}")
    print(f"\n   Example questions to add:")
    print(f"   - Use automatic discovery? (yes/no)")
    print(f"   - Discovery method: (full/quick/manual)")
    print(f"   - Skip network discovery? (yes/no)")
    
    print(f"\n2. Test the step in isolation:")
    impl_file = created_files['implementation']
    print(f"   python {impl_file.relative_to(project_root)}")
    
    print(f"\n3. Integrate into phase orchestrator:")
    orchestrator = phase_dir / "orchestrator_discovery.py"
    print(f"   Edit: {orchestrator.relative_to(project_root)}")
    print(f"   Add import: from .step_0_discovery_prompt.discovery_prompt import execute_discovery_prompt")
    print(f"   Call in execute(): result = execute_discovery_prompt(context, self.phase_dir)")
    
    print(f"\n4. Update status in YAML when complete:")
    print(f"   design_specs/control_flows.yml")
    print(f"   Change: status: PLANNED → status: IMPLEMENTED")
    
    return True


if __name__ == "__main__":
    try:
        success = generate_discovery_prompt_scaffolding()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
