# Control Flow Engine: Scaffolding & Restructuring Proposal

## 🎯 Executive Summary

The Control Flow Engine currently has basic step insertion capability but lacks **automatic scaffolding generation**. This proposal defines a complete implementation for:

1. **Phase Insertion** - Add new phases to flows with automatic directory creation
2. **Step Insertion** - Add steps to existing phases with file/directory scaffolding  
3. **Automatic Restructuring** - Rename/reorder phases and steps with file system updates
4. **Path Management** - Update all references when moving/renaming components

## 📋 Current State Analysis

### What EXISTS in Control Flow Engine
```python
class ControlFlowManager:
    ✅ load_specification()           # Loads YAML spec
    ✅ insert_flow_step()             # Inserts step into flow_steps array
    ✅ apply_planned_insertions()     # Applies planned insertions
    ✅ generate_mock_code()           # Generates stub code
    ✅ generate_unit_test()           # Generates test code
    ❌ save_specification()           # Only prints, doesn't actually save!
    ❌ create_scaffolding()           # MISSING
    ❌ rename_phase()                 # MISSING
    ❌ rename_step()                  # MISSING
    ❌ update_file_references()       # MISSING
```

### What's MISSING
1. **No YAML saving** - `save_specification()` only prints, doesn't write
2. **No file/directory creation** - Can't create actual step directories
3. **No path updates** - Can't update imports/references when moving things
4. **Wrong data structure** - Expects `flow_steps` but config-manager uses `phases` with nested `steps`

## 🏗️ Proposed Architecture

### 1. Data Structure Support

**Current**: Assumes markdown with YAML blocks
```yaml
flows:
  main_flow:
    flow_steps:  # ← Engine expects this
      - step_id: step1
```

**Needed**: Support pure YAML files
```yaml
flows:
  main_config_flow:
    phases:      # ← Config-manager uses this
      - phase_id: discovery
        steps:   # ← Steps are nested in phases
          - step_id: discovery_prompt
```

### 2. Core Operations Matrix

| Operation | Input | Creates | Updates | Complexity |
|-----------|-------|---------|---------|------------|
| **Insert Phase** | Phase definition | • Directory tree<br>• `__init__.py`<br>• `orchestrator_*.py`<br>• `outputs/` dir | • `control_flows.yml`<br>• Sequence numbers | Medium |
| **Insert Step** | Step definition | • Step directory<br>• `__init__.py`<br>• Implementation file<br>• Layout file (if TUI)<br>• Mock responses | • `control_flows.yml`<br>• Phase orchestrator<br>• Sequence numbers | High |
| **Rename Phase** | Old/new names | Nothing | • Directory name<br>• All file imports<br>• Orchestrator class<br>• `control_flows.yml` | High |
| **Rename Step** | Old/new names | Nothing | • Directory name<br>• Function names<br>• File names<br>• All imports<br>• `control_flows.yml` | Very High |
| **Reorder Phases** | New sequence | Nothing | • Directory names<br>• `control_flows.yml`<br>• Sequence numbers | Medium |
| **Reorder Steps** | New sequence | Nothing | • Directory names<br>• `control_flows.yml`<br>• Sequence numbers | Medium |

## 📐 Implementation Plan

### Phase 1: YAML Save Capability (CRITICAL)

**Problem**: `save_specification()` doesn't actually save

**Solution**:
```python
def save_specification(self, spec_data: Dict[str, Any], output_path: Path):
    """
    Save specification to YAML file.
    
    Args:
        spec_data: Complete specification dictionary
        output_path: Path to save YAML file
    """
    with open(output_path, 'w') as f:
        yaml.dump(
            spec_data, 
            f, 
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            allow_unicode=True
        )
    print(f"✅ Saved specification to {output_path}")
```

### Phase 2: Phase Insertion with Scaffolding

**Input Structure**:
```python
@dataclass
class PhaseInsertion:
    phase_id: str                    # e.g., "discovery"
    name: str                        # e.g., "Discovery Phase"
    sequence: int                    # e.g., 1
    description: str
    status: ImplementationStatus     # PLANNED, IN_PROGRESS, IMPLEMENTED
    
    # Optional scaffolding details
    create_scaffolding: bool = True
    orchestrator_class_name: Optional[str] = None  # e.g., "DiscoveryPhase"
    base_path: Optional[Path] = None               # e.g., phases/
    
    # Steps to create within this phase
    initial_steps: List['StepInsertion'] = field(default_factory=list)
```

**Generated Structure**:
```
phases/phase_{sequence}_{phase_id}/
├── __init__.py                                    # Empty or with exports
├── orchestrator_{phase_id}.py                     # Phase orchestrator
├── outputs/                                       # Output directory
└── README.md                                      # Phase documentation
```

**Orchestrator Template**:
```python
# Generated: orchestrator_{phase_id}.py
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class {OrchestratorClassName}:
    """
    Phase: {Phase Name}
    Status: {Status}
    
    {Description}
    
    Artifacts Consumed: {artifacts_consumed}
    Artifacts Produced: {artifacts_produced}
    """
    
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_{sequence}_{phase_id}"
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute {Phase Name}.
        
        Args:
            context: Execution context with consumed artifacts
            
        Returns:
            Dict with produced artifacts
        """
        if self.ui:
            self.ui.show_phase_header("{Phase Name}", "{Description}")
        
        logger.info("Executing {Phase Name}")
        
        # TODO: Implement phase logic
        
        return {
            # TODO: Return produced artifacts
        }
```

### Phase 3: Step Insertion with Scaffolding

**Input Structure**:
```python
@dataclass
class StepInsertion:
    step_id: str                     # e.g., "discovery_prompt"
    name: str                        # e.g., "Discovery Configuration Prompt"
    sequence: int                    # e.g., 0
    description: str
    status: ImplementationStatus
    step_type: str                   # 'interactive', 'processing', 'io', 'validation'
    
    # Scaffolding options
    create_scaffolding: bool = True
    phase_id: str                    # Parent phase
    phase_sequence: int              # Parent phase sequence number
    
    # TUI-specific (if step_type == 'interactive')
    is_tui_form: bool = False
    layout_file_name: Optional[str] = None  # e.g., "discovery_prompt.layout.yml"
    use_defaults_file: bool = False
    defaults_file_name: Optional[str] = None
    
    # Mock responses
    generate_mock_responses: bool = True
    
    # Insert position
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None
```

**Generated Structure (Regular Step)**:
```
phases/phase_{phase_seq}_{phase_id}/step_{step_seq}_{step_id}/
├── __init__.py                    # Exports execute function
├── {step_id}.py                   # Implementation
├── README.md                      # Step documentation
└── test_{step_id}.py              # Unit tests (optional)
```

**Generated Structure (TUI Form Step)**:
```
phases/phase_{phase_seq}_{phase_id}/step_{step_seq}_{step_id}/
├── __init__.py                    # Exports execute function
├── {step_id}.py                   # TUI integration logic
├── {step_id}.layout.yml           # TUI form layout
├── {step_id}.defaults.yml         # TUI defaults (optional)
├── mock_responses.json            # Mock data for testing
├── README.md                      # Step documentation
└── test_{step_id}.py              # Unit tests (optional)
```

**Implementation Template (Regular)**:
```python
# Generated: {step_id}.py
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def execute_{step_id}(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    {Step Name}
    Status: {Status}
    
    {Description}
    
    Args:
        context: Execution context
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results
    """
    logger.info("Executing: {Step Name}")
    
    # TODO: Implement step logic
    
    return {
        'step': '{step_id}',
        'status': 'completed',
        # TODO: Add step-specific results
    }
```

**Implementation Template (TUI Form)**:
```python
# Generated: {step_id}.py
from pathlib import Path
from typing import Dict, Any
import logging
import sys

# Import TUI Form Engine
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'tui-form-designer' / 'src'))
from tui_form_engine.renderer import FormRenderer

logger = logging.getLogger(__name__)


def execute_{step_id}(context: Dict[str, Any], phase_dir: Path) -> Dict[str, Any]:
    """
    {Step Name}
    Status: {Status}
    
    {Description}
    
    This step uses TUI Form Engine for interactive user input.
    
    Args:
        context: Execution context (may contain mock_responses)
        phase_dir: Phase directory path
        
    Returns:
        Dict containing:
        - User responses from the form
        - Any derived configuration
    """
    logger.info("=" * 70)
    logger.info("{Step Name}")
    logger.info("=" * 70)
    
    # Path to TUI form layout
    layout_path = phase_dir / "step_{step_seq}_{step_id}" / "{step_id}.layout.yml"
    
    if not layout_path.exists():
        logger.error(f"❌ Layout file not found: {layout_path}")
        return _get_default_config()
    
    # Create TUI renderer
    renderer = FormRenderer()
    
    # Check for mock mode
    mock_responses = None
    if 'mock_responses' in context and '{step_id}' in context['mock_responses']:
        mock_responses = context['mock_responses']['{step_id}']
        logger.info("🤖 Running in MOCK mode")
    
    # Render the form
    try:
        response = renderer.render_flow(
            flow_path=str(layout_path),
            mock_responses=mock_responses,
            quiet=context.get('quiet', False)
        )
        
        responses = response.get('responses', {})
        
        logger.info(f"✅ Collected {len(responses)} responses")
        
        return {
            'step': '{step_id}',
            'responses': responses,
            'status': 'completed'
        }
        
    except KeyboardInterrupt:
        logger.warning("⚠️  User cancelled")
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return _get_default_config()


def _get_default_config() -> Dict[str, Any]:
    """Fallback configuration when form cannot be rendered."""
    return {
        'step': '{step_id}',
        'status': 'fallback',
        'responses': {}
    }
```

**Layout Template (TUI)**:
```yaml
# Generated: {step_id}.layout.yml
flow_id: {step_id}
title: "{Step Name}"
icon: "🔧"  # TODO: Choose appropriate icon
description: "{Description}"

metadata:
  id: {step_id}
  version: "1.0.0"
  estimated_time: "30 seconds"

# TODO: Add defaults_file if needed
# defaults_file: {step_id}.defaults.yml

steps:
  # TODO: Define form steps
  - id: example_input
    type: text
    message: "Enter a value:"
    instruction: "Provide configuration input"
    default: ""
```

### Phase 4: Rename Operations

**Challenge**: Renaming requires updating:
1. Directory names
2. File names
3. Class names in code
4. Function names in code
5. Import statements
6. control_flows.yml references

**Approach**: Multi-pass update with validation

```python
def rename_phase(
    self,
    old_phase_id: str,
    new_phase_id: str,
    old_sequence: int,
    new_sequence: Optional[int] = None,
    base_path: Path = Path("phases"),
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Rename a phase and update all references.
    
    Args:
        old_phase_id: Current phase ID
        new_phase_id: New phase ID
        old_sequence: Current sequence number
        new_sequence: New sequence number (if changing)
        base_path: Base path for phases directory
        dry_run: If True, only show what would change
        
    Returns:
        Dict with summary of changes made or planned
    """
    new_seq = new_sequence if new_sequence is not None else old_sequence
    
    old_dir = base_path / f"phase_{old_sequence}_{old_phase_id}"
    new_dir = base_path / f"phase_{new_seq}_{new_phase_id}"
    
    changes = {
        'directory_rename': {
            'from': str(old_dir),
            'to': str(new_dir)
        },
        'files_to_update': [],
        'imports_to_update': [],
        'yaml_updates': []
    }
    
    # 1. Find all files that import from this phase
    # 2. Update import statements
    # 3. Rename orchestrator class if needed
    # 4. Update control_flows.yml
    # 5. Rename directory
    
    if dry_run:
        print("🔍 DRY RUN - No changes will be made")
        print(json.dumps(changes, indent=2))
        return changes
    else:
        # Execute changes
        self._execute_rename_changes(changes)
        return changes
```

### Phase 5: Orchestrator Integration

**Problem**: After inserting a step, the phase orchestrator needs to call it

**Solution**: Automatic orchestrator update

```python
def integrate_step_into_orchestrator(
    self,
    phase_id: str,
    phase_sequence: int,
    step: StepInsertion,
    base_path: Path = Path("phases")
) -> bool:
    """
    Add step execution call to phase orchestrator.
    
    Updates the execute() method to call the new step.
    """
    orchestrator_file = base_path / f"phase_{phase_sequence}_{phase_id}" / f"orchestrator_{phase_id}.py"
    
    if not orchestrator_file.exists():
        print(f"❌ Orchestrator not found: {orchestrator_file}")
        return False
    
    # Read current orchestrator
    with open(orchestrator_file, 'r') as f:
        content = f.read()
    
    # Add import at top
    import_line = f"from .step_{step.sequence}_{step.step_id} import {step.step_id}\n"
    
    # Find import section and add
    if "# Handle both relative" in content:
        # Insert after imports section
        insert_point = content.find("logger = logging.getLogger")
        content = content[:insert_point] + import_line + "\n" + content[insert_point:]
    
    # Add step execution in execute() method
    step_call = f'''
        # Step {step.sequence}: {step.name}
        logger.info("Step {step.sequence}/{total_steps}: {step.name}")
        step_result = {step.step_id}.execute_{step.step_id}(context, self.phase_dir)
        context.update(step_result)
        
'''
    
    # Insert step call in execute() method
    # (This requires AST parsing for reliability)
    
    # Write updated orchestrator
    with open(orchestrator_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Integrated {step.step_id} into {orchestrator_file}")
    return True
```

## 🎯 Usage Examples

### Example 1: Insert New Phase

```python
from control_flow_engine.scaffolding import ControlFlowScaffolder

scaffolder = ControlFlowScaffolder(
    spec_file=Path("design_specs/control_flows.yml"),
    project_root=Path("/opt/openproject/external/config-manager")
)

# Define new phase
new_phase = PhaseInsertion(
    phase_id="pre_validation",
    name="Pre-Validation Phase",
    sequence=4,  # Insert as phase 4
    description="Validate configuration before deployment",
    status=ImplementationStatus.PLANNED,
    create_scaffolding=True,
    orchestrator_class_name="PreValidationPhase"
)

# Execute insertion
result = scaffolder.insert_phase(
    flow_name="main_config_flow",
    phase=new_phase,
    dry_run=False  # Actually create files
)

print(result.summary())
```

### Example 2: Insert Step with TUI Form

```python
# Define new step
new_step = StepInsertion(
    step_id="discovery_prompt",
    name="Discovery Configuration Prompt",
    sequence=0,
    description="Ask user whether to use automatic system discovery",
    status=ImplementationStatus.PLANNED,
    step_type="interactive",
    phase_id="discovery",
    phase_sequence=1,
    create_scaffolding=True,
    is_tui_form=True,
    layout_file_name="discovery_prompt.layout.yml",
    use_defaults_file=False,  # Hardcoded defaults
    generate_mock_responses=True,
    insert_before="env_discovery"  # Insert as first step
)

# Execute insertion
result = scaffolder.insert_step(
    flow_name="main_config_flow",
    phase_id="discovery",
    step=new_step,
    update_orchestrator=True,  # Automatically add to orchestrator
    dry_run=False
)
```

### Example 3: Rename Phase

```python
result = scaffolder.rename_phase(
    old_phase_id="tui_mapping",
    new_phase_id="defaults_mapping",
    old_sequence=2,
    new_sequence=2,  # Keep same position
    dry_run=True  # Check what would change first
)

# Review changes
print("Changes that would be made:")
for change in result['changes']:
    print(f"  - {change}")

# Apply if looks good
if input("Apply changes? (y/n): ") == 'y':
    scaffolder.rename_phase(
        old_phase_id="tui_mapping",
        new_phase_id="defaults_mapping",
        old_sequence=2,
        dry_run=False
    )
```

## 📊 Implementation Priority

| Priority | Feature | Complexity | Impact | Effort |
|----------|---------|------------|--------|--------|
| **P0** | YAML save functionality | Low | Critical | 2h |
| **P0** | Phase-based navigation (not flow_steps) | Medium | Critical | 4h |
| **P1** | Step insertion with scaffolding | High | High | 8h |
| **P1** | TUI form template generation | Medium | High | 4h |
| **P2** | Phase insertion with scaffolding | Medium | Medium | 6h |
| **P2** | Orchestrator auto-update | High | High | 8h |
| **P3** | Rename operations | Very High | Medium | 12h |
| **P3** | Reorder operations | High | Low | 6h |

**Total Estimated Effort**: 50 hours for full implementation

## 🚀 Recommended Approach

### Phase 1: Foundation (P0 - 6 hours)
1. Fix `save_specification()` to actually write YAML
2. Add support for `phases` with nested `steps` structure
3. Update `insert_flow_step()` to navigate phase hierarchy

### Phase 2: Step Scaffolding (P1 - 12 hours)
1. Implement `StepInsertion` dataclass
2. Create directory/file scaffolding logic
3. Generate implementation templates
4. Generate TUI layout templates
5. Generate mock responses

### Phase 3: Integration (P2 - 14 hours)
1. Implement phase scaffolding
2. Auto-update orchestrator with new steps
3. Sequence number management
4. Validation and dry-run mode

### Phase 4: Advanced (P3 - 18 hours)
1. Rename operations with file updates
2. Reorder operations
3. Import statement updates
4. Comprehensive testing

## ✅ Acceptance Criteria

A successful implementation should allow:

```python
# Single command to add a fully functional step
scaffolder.insert_step(
    StepInsertion(
        step_id="user_confirmation",
        name="Confirm Settings",
        sequence=5,
        description="Ask user to confirm configuration",
        phase_id="validation",
        phase_sequence=4,
        is_tui_form=True
    )
)

# Result:
# ✅ Created phases/phase_4_validation/step_5_user_confirmation/
# ✅ Generated user_confirmation.py with TUI integration
# ✅ Generated user_confirmation.layout.yml with template
# ✅ Generated mock_responses.json
# ✅ Updated orchestrator_validation.py to call new step
# ✅ Updated control_flows.yml with step definition
# ✅ All sequence numbers adjusted automatically
```

---

**Status**: 📝 PROPOSAL
**Author**: Control Flow Team
**Date**: October 14, 2025
**Next Step**: Get approval and start Phase 1 implementation
