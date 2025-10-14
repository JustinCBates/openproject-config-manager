# Quick Start: Using Control Flow Engine Scaffolding

## 🚀 Quick Example

```python
from pathlib import Path
from control_flow_engine.core.scaffolder import ScaffoldGenerator, StepInsertion, ImplementationStatus

# Initialize
scaffolder = ScaffoldGenerator(Path("/opt/openproject/external/config-manager"))

# Define your step
new_step = StepInsertion(
    step_id="my_step",
    name="My Interactive Step",
    sequence=0,
    description="This step does something useful",
    status=ImplementationStatus.PLANNED,
    step_type="interactive",
    phase_id="discovery",
    phase_sequence=1,
    is_tui_form=True,  # Use TUI Form Engine
    generate_mock_responses=True
)

# Generate everything
scaffolder.create_step_scaffolding(
    step=new_step,
    base_path=Path("phases/phase_1_discovery")
)
```

**Result**: Complete working step with:
- ✅ `__init__.py`
- ✅ `my_step.py` (with TUI integration)
- ✅ `my_step.layout.yml`
- ✅ `mock_responses.json`
- ✅ `README.md`

## 📖 Complete Workflow

### 1. Setup

```python
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
```

### 2. Load Specification

```python
spec_file = Path("design_specs/control_flows.yml")
manager = ControlFlowManager(spec_file)

# Load YAML
with open(spec_file, 'r') as f:
    spec_data = yaml.safe_load(f)

manager.flows = spec_data.get('flows', {})
```

### 3. Define Step

```python
new_step = StepInsertion(
    # Basic info
    step_id="user_confirmation",
    name="User Confirmation Step",
    sequence=2,
    description="Ask user to confirm settings before proceeding",
    status=ImplementationStatus.PLANNED,
    step_type="interactive",
    
    # Parent phase
    phase_id="validation",
    phase_sequence=4,
    
    # TUI options
    is_tui_form=True,
    layout_file_name="user_confirmation.layout.yml",
    
    # Testing
    generate_mock_responses=True,
    mock_responses={
        "confirmed": True,
        "notes": "Looks good!"
    }
)
```

### 4. Insert into YAML

```python
# Create step data
step_data = {
    'step_id': new_step.step_id,
    'name': new_step.name,
    'type': new_step.step_type,
    'description': new_step.description,
    'status': new_step.status.value,
    'dependencies': [],
    'artifacts_produced': ['confirmation_status']
}

# Insert
manager.insert_step_into_phase(
    flow_name='main_config_flow',
    phase_id='validation',
    step_data=step_data
)

# Save
manager.save_specification()
```

### 5. Generate Scaffolding

```python
scaffolder = ScaffoldGenerator(Path("/opt/openproject/external/config-manager"))

phase_dir = Path("phases/phase_4_validation")
created_files = scaffolder.create_step_scaffolding(
    step=new_step,
    base_path=phase_dir
)

print(f"Created {len(created_files)} files!")
```

## 🎨 Step Types

### Interactive Step (TUI Form)

```python
StepInsertion(
    step_id="interactive_config",
    step_type="interactive",
    is_tui_form=True,
    layout_file_name="interactive_config.layout.yml",
    generate_mock_responses=True,
    mock_responses={"field1": "value1"}
)
```

**Generated**: Full TUI integration with FormRenderer

### Processing Step (No UI)

```python
StepInsertion(
    step_id="data_processor",
    step_type="processing",
    is_tui_form=False,
    generate_mock_responses=False
)
```

**Generated**: Simple implementation template with logging

### Validation Step

```python
StepInsertion(
    step_id="validate_config",
    step_type="validation",
    is_tui_form=False
)
```

**Generated**: Validation-focused template

## 🔧 Customization

### Custom Mock Responses

```python
StepInsertion(
    ...
    mock_responses={
        "database_host": "localhost",
        "database_port": 5432,
        "use_ssl": True,
        "credentials": {
            "username": "admin",
            "password": "test123"
        }
    }
)
```

### With Defaults File

```python
StepInsertion(
    ...
    use_defaults_file=True,
    defaults_file_name="my_step.defaults.yml"
)
```

## 📝 After Generation

### 1. Customize Layout

Edit `{step_id}.layout.yml`:

```yaml
steps:
  - id: database_host
    type: text
    message: "Enter database host:"
    default: "localhost"
    
  - id: database_port
    type: number
    message: "Enter database port:"
    default: 5432
```

### 2. Implement Logic

Edit `{step_id}.py` - find the TODO:

```python
def execute_{step_id}(context, phase_dir):
    # ... TUI rendering code ...
    
    # TODO: Implement step logic  ← ADD YOUR CODE HERE
    
    return {
        'step': 'my_step',
        'responses': responses,
        'status': 'completed'
    }
```

### 3. Test Standalone

```bash
cd phases/phase_1_discovery/step_0_my_step
python my_step.py
```

## 🐛 Troubleshooting

### Import Error

```python
# Add TUI path if needed
import sys
from pathlib import Path
tui_path = Path(__file__).parent.parent.parent.parent / 'tui-form-designer' / 'src'
sys.path.insert(0, str(tui_path))
```

### Layout Not Found

Check path in generated code:
```python
layout_path = phase_dir / "step_{sequence}_{step_id}" / "{step_id}.layout.yml"
```

### Mock Responses Not Working

Ensure context has correct structure:
```python
context = {
    'mock_responses': {
        'my_step': {  # ← Must match step_id
            'field1': 'value1'
        }
    }
}
```

## 📚 Reference

**Files Generated**:
- `__init__.py` - Module exports
- `{step_id}.py` - Implementation
- `{step_id}.layout.yml` - TUI layout (if TUI)
- `mock_responses.json` - Test data
- `README.md` - Documentation

**StepInsertion Parameters**:
- `step_id` (required) - Unique identifier
- `name` (required) - Display name
- `sequence` (required) - Order in phase
- `description` (required) - What this step does
- `status` (required) - ImplementationStatus enum
- `step_type` (required) - 'interactive', 'processing', 'io', 'validation'
- `phase_id` (required) - Parent phase
- `phase_sequence` (required) - Parent phase number
- `is_tui_form` - Use TUI Form Engine
- `layout_file_name` - Custom layout filename
- `generate_mock_responses` - Create mock data
- `mock_responses` - Custom mock data dict

**ImplementationStatus Values**:
- `PLANNED` - Not started
- `IN_PROGRESS` - Currently developing
- `IMPLEMENTED` - Complete and working
- `TODO` - Needs implementation

## 🎯 Best Practices

1. **Start with PLANNED status** - Mark IMPLEMENTED when done
2. **Use descriptive step_ids** - e.g., `user_confirmation` not `step1`
3. **Provide good descriptions** - Used in docs and UI
4. **Test with mocks first** - Validate logic before manual testing
5. **Update README** - Document any special behavior
6. **Add proper error handling** - Customize the fallback behavior

## ✅ Quick Test

```bash
# Run the demo
cd /opt/openproject/external/config-manager
python test_control_flow_scaffolding.py

# Should see:
# ✅ Inserted step into YAML
# ✅ Created step scaffolding
# ✅ All files verified
# 🎉 SUCCESS!
```

---

**Ready to create your first step?** Copy the Quick Example and customize it!
