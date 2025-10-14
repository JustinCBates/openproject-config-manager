#!/usr/bin/env python3
"""
Batch refactor all remaining phases in config-manager.
"""

from pathlib import Path
import sys
import yaml

# Add control-flow to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'control-flow' / 'src'))

from control_flow_engine.core.orchestrator_regenerator import OrchestratorRegenerator


# Phase configurations
PHASE_CONFIGS = {
    'collection': {
        'phase_sequence': 3,
        'steps': [
            {
                'step_id': 'collect_user_configuration',
                'name': 'Collect User Configuration',
                'type': 'interactive',
                'description': 'Collect configuration from user via TUI forms',
                'status': 'IMPLEMENTED',
                'sequence': 1,
                'function_name': 'execute_collect_user_configuration'
            }
        ]
    },
    'validation': {
        'phase_sequence': 4,
        'steps': [
            {
                'step_id': 'schema_validation',
                'name': 'Schema Validation',
                'type': 'validation',
                'description': 'Validate configuration against JSON schema',
                'status': 'IMPLEMENTED',
                'sequence': 1,
                'function_name': 'execute_schema_validation'
            },
            {
                'step_id': 'dependency_validation',
                'name': 'Dependency Validation',
                'type': 'validation',
                'description': 'Validate service dependencies and compatibility',
                'status': 'IMPLEMENTED',
                'sequence': 2,
                'function_name': 'execute_dependency_validation'
            },
            {
                'step_id': 'environment_validation',
                'name': 'Environment Validation',
                'type': 'validation',
                'description': 'Validate environment-specific requirements',
                'status': 'IMPLEMENTED',
                'sequence': 3,
                'function_name': 'execute_environment_validation'
            }
        ]
    },
    'export': {
        'phase_sequence': 5,
        'steps': []  # Will check implementation
    }
}


def add_steps_to_yaml(spec_file: Path, phase_id: str, steps: list):
    """Add steps to phase in YAML."""
    print(f"\n{'='*70}")
    print(f"Adding steps to {phase_id} phase in YAML")
    print(f"{'='*70}")
    
    with open(spec_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Find the phase
    phases = spec['flows']['main_config_flow']['phases']
    phase = None
    for p in phases:
        if p['phase_id'] == phase_id:
            phase = p
            break
    
    if not phase:
        print(f"❌ Phase '{phase_id}' not found in YAML")
        return False
    
    # Add steps if not present
    if 'steps' not in phase or not phase['steps']:
        phase['steps'] = steps
        
        # Write back
        with open(spec_file, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print(f"✅ Added {len(steps)} steps to {phase_id} phase")
        for step in steps:
            print(f"   - {step['step_id']}: {step['name']}")
        return True
    else:
        print(f"⚠️  Phase '{phase_id}' already has steps, skipping")
        return False


def create_step_wrapper(step_dir: Path, step_id: str, function_name: str):
    """Create Step class wrapper."""
    class_name = f"{step_id.title().replace('_', '')}Step"
    
    impl_file = step_dir / f"{step_id}.py"
    if not impl_file.exists():
        # Try other common patterns
        for pattern in [step_dir / f"{step_id}.py", step_dir / "*.py"]:
            matches = list(step_dir.glob(pattern.name)) if '*' in pattern.name else [pattern]
            if matches and matches[0].exists():
                impl_file = matches[0]
                break
    
    if not impl_file.exists():
        print(f"⚠️  Implementation file not found for {step_id}")
        return False
    
    # Check if wrapper already exists
    content = impl_file.read_text()
    if class_name in content:
        print(f"   ✓ {class_name} already exists")
        return True
    
    # Add wrapper
    wrapper = f'''


class {class_name}:
    """Wrapper class for {step_id} step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_{PHASE_CONFIGS[phase_id]['phase_sequence']}_{phase_id}"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute {step_id} step."""
        result_data = {function_name}(context, self.phase_dir)
        return {{
            "artifacts": result_data if isinstance(result_data, dict) else {{"data": result_data}}
        }}
'''
    
    with open(impl_file, 'a') as f:
        f.write(wrapper)
    
    print(f"   ✓ Added {class_name}")
    return True


def main():
    """Batch refactor remaining phases."""
    
    project_root = Path(__file__).parent
    spec_file = project_root / 'design_specs' / 'control_flows.yml'
    
    print("=" * 70)
    print("BATCH REFACTORING: Remaining Config-Manager Phases")
    print("=" * 70)
    
    for phase_id, config in PHASE_CONFIGS.items():
        print(f"\n{'#'*70}")
        print(f"# Phase: {phase_id}")
        print(f"{'#'*70}")
        
        # Skip if no steps defined
        if not config['steps']:
            print(f"⚠️  No steps configured for {phase_id}, skipping")
            continue
        
        # 1. Add steps to YAML
        add_steps_to_yaml(spec_file, phase_id, config['steps'])
        
        # 2. Create Step class wrappers
        print(f"\nAdding Step class wrappers...")
        phase_dir = project_root / 'phases' / f"phase_{config['phase_sequence']}_{phase_id}"
        
        for step in config['steps']:
            step_id = step['step_id']
            step_dir = phase_dir / f"step_{step['sequence']}_{step_id}"
            
            if step_dir.exists():
                create_step_wrapper(
                    step_dir=step_dir,
                    step_id=step_id,
                    function_name=step['function_name']
                )
            else:
                print(f"   ⚠️  Step directory not found: {step_dir}")
        
        # 3. Regenerate orchestrator
        print(f"\nRegenerating orchestrator...")
        orchestrator_file = phase_dir / f"orchestrator_{phase_id}.py"
        
        if orchestrator_file.exists():
            regenerator = OrchestratorRegenerator(spec_file)
            success = regenerator.regenerate_phase_orchestrator(
                orchestrator_file=orchestrator_file,
                phase_id=phase_id,
                flow_name='main_config_flow'
            )
            
            if success:
                print(f"✅ {phase_id} phase refactored successfully!")
            else:
                print(f"❌ Failed to regenerate {phase_id} orchestrator")
        else:
            print(f"⚠️  Orchestrator not found: {orchestrator_file}")
    
    print("\n" + "=" * 70)
    print("✅ BATCH REFACTORING COMPLETE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
