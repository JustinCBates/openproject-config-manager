#!/usr/bin/env python3
"""
Add Step class wrappers to old-style steps.
This allows the regenerated orchestrator to work with existing implementation.
"""

from pathlib import Path


def create_step_class_wrapper(step_dir: Path, step_id: str, function_name: str, module_name: str):
    """
    Create a Step class wrapper around existing function.
    
    Args:
        step_dir: Directory containing the step
        step_id: ID of the step
        function_name: Name of the execute function
        module_name: Name of the module containing the function
    """
    # Class name from step_id
    class_name = f"{step_id.title().replace('_', '')}Step"
    
    # Create wrapper content
    wrapper_content = f'''"""
{class_name} - Wrapper for existing {function_name} implementation
"""

from pathlib import Path
from typing import Dict, Any
from .{module_name} import {function_name}


class {class_name}:
    """Wrapper class for {step_id} step."""
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_1_discovery"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute {step_id} step.
        
        Args:
            context: Execution context
            
        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = {function_name}(context, self.phase_dir)
        
        # Return in expected format
        return {{
            "artifacts": result_data if isinstance(result_data, dict) else {{"data": result_data}}
        }}
'''
    
    # Find the main implementation file (e.g., env_discovery.py)
    impl_file = step_dir / f"{step_id}.py"
    
    if impl_file.exists():
        # Append wrapper class to existing file
        content = impl_file.read_text()
        
        # Check if class already exists
        if class_name not in content:
            content += "\n\n" + wrapper_content
            impl_file.write_text(content)
            print(f"✅ Added {class_name} to {impl_file.name}")
        else:
            print(f"⚠️  {class_name} already exists in {impl_file.name}")
    else:
        print(f"❌ Implementation file not found: {impl_file}")


def main():
    """Add Step class wrappers to all old-style steps."""
    
    base_dir = Path(__file__).parent / 'phases' / 'phase_1_discovery'
    
    print("=" * 70)
    print("Adding Step class wrappers to old-style steps")
    print("=" * 70)
    print()
    
    # Step 1: env_discovery
    create_step_class_wrapper(
        step_dir=base_dir / 'step_1_env_discovery',
        step_id='env_discovery',
        function_name='execute_env_discovery',
        module_name='env_discovery'
    )
    
    # Step 2: system_discovery
    create_step_class_wrapper(
        step_dir=base_dir / 'step_2_system_discovery',
        step_id='system_discovery',
        function_name='execute_system_discovery',
        module_name='system_discovery'
    )
    
    # Step 3: defaults_generation
    create_step_class_wrapper(
        step_dir=base_dir / 'step_3_defaults_generation',
        step_id='defaults_generation',
        function_name='execute_defaults_generation',
        module_name='defaults_generation'
    )
    
    print()
    print("=" * 70)
    print("✅ Step class wrappers added!")
    print("=" * 70)
    print()
    print("The regenerated orchestrator can now use these steps.")
    print()


if __name__ == '__main__':
    main()
