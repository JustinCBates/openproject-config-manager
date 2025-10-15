# YAML-Driven Phase Orchestration

## Overview

The configuration manager can now be executed **dynamically** based on the `control_flows.yml` specification file. This means you can modify the phase execution order, add new phases, or skip phases by simply editing the YAML file - no code changes required!

## Key Benefits

✅ **Design-First Development** - Define workflows in YAML before implementing  
✅ **Runtime Flexibility** - Change execution order without code changes  
✅ **Clear Documentation** - YAML file serves as executable documentation  
✅ **Easy Testing** - Test individual flows or phases  
✅ **Status Tracking** - Track implementation progress (IMPLEMENTED/PLANNED/SKIPPED)  

## Quick Start

### 1. View Available Flows

```bash
python3 run_dynamic.py --list-flows
```

### 2. Inspect a Flow

```bash
python3 run_dynamic.py --info
```

### 3. Execute the Full Pipeline

```bash
python3 run_dynamic.py
```

Or specify a particular flow:

```bash
python3 run_dynamic.py --flow main_config_flow
```

## How It Works

### The Control Flow Specification

The system reads `design_specs/control_flows.yml` at runtime:

```yaml
flows:
  main_config_flow:
    description: Primary Configuration Process
    phases:
      - phase_id: discovery
        name: Discovery Phase
        status: IMPLEMENTED
        sequence: 1
        artifacts_produced:
          - discovery_data
          - enhanced_defaults_file
        
      - phase_id: tui_mapping
        name: TUI Defaults Mapping
        status: IMPLEMENTED
        sequence: 2
        artifacts_consumed:
          - enhanced_defaults_file
        artifacts_produced:
          - tui_defaults_file
```

### Dynamic Phase Loading

The `DynamicOrchestrator`:

1. **Reads** `control_flows.yml` at runtime
2. **Validates** that required artifacts are available
3. **Loads** phase orchestrators dynamically using Python's `importlib`
4. **Executes** phases in the order specified in the YAML
5. **Tracks** artifacts flow between phases

### Phase Status Handling

Phases can have different statuses:

- `IMPLEMENTED` - Phase is ready and will be executed
- `PLANNED` - Phase is designed but not yet coded (skipped)
- `SKIPPED` - Phase is intentionally skipped
- `IN_PROGRESS` - Phase is under development

The orchestrator automatically **skips** phases with `PLANNED` or `SKIPPED` status.

## Command-Line Interface

### Options

```
usage: run_dynamic.py [-h] [--flow FLOW] [--spec SPEC] [--list-flows] 
                      [--info] [--verbose] [--project-root PROJECT_ROOT]

Options:
  -h, --help            Show help message
  -f, --flow FLOW       Flow ID to execute (default: main_config_flow)
  -s, --spec SPEC       Path to control_flows.yml (default: auto-detect)
  -l, --list-flows      List available flows and exit
  -i, --info            Show flow information without executing
  -v, --verbose         Enable verbose logging
  -p, --project-root    Project root directory
```

### Examples

**List all flows:**
```bash
python3 run_dynamic.py --list-flows
```

**Show detailed flow info:**
```bash
python3 run_dynamic.py --info --flow main_config_flow
```

**Execute with verbose logging:**
```bash
python3 run_dynamic.py --verbose
```

**Use custom spec file:**
```bash
python3 run_dynamic.py --spec /path/to/custom_flows.yml
```

## Modifying the Workflow

### Example: Change Phase Order

Edit `design_specs/control_flows.yml`:

```yaml
phases:
  - phase_id: discovery
    sequence: 1    # Discovery first
  
  - phase_id: validation
    sequence: 2    # Validate before collection!
  
  - phase_id: collection
    sequence: 3    # Then collect
```

No code changes needed - just update the `sequence` numbers!

### Example: Skip a Phase

```yaml
- phase_id: validation
  status: SKIPPED    # Temporarily skip validation
```

### Example: Add a New Phase

1. Add to `control_flows.yml`:
```yaml
- phase_id: backup
  name: Backup Phase
  status: PLANNED    # Not implemented yet
  sequence: 0         # Run before discovery
  description: Backup existing configuration
```

2. Implement when ready:
```python
# phases/phase_0_backup/orchestrator_backup.py
class BackupPhase:
    def execute(self, context):
        # Implementation here
        pass
```

3. Update status:
```yaml
status: IMPLEMENTED
```

## Architecture

### Components

```
config-manager/
├── run_dynamic.py                    # CLI entry point
├── phases/
│   ├── dynamic_orchestrator.py       # YAML-driven orchestrator
│   ├── phase_1_discovery/
│   ├── phase_2_tui_mapping/
│   ├── phase_3_collection/
│   ├── phase_4_validation/
│   └── phase_5_export/
└── design_specs/
    └── control_flows.yml             # Flow specification
```

### Data Flow

```
control_flows.yml
       ↓
DynamicOrchestrator.load_spec()
       ↓
For each phase in flow:
  1. Check status (IMPLEMENTED/PLANNED/SKIPPED)
  2. Verify artifacts_consumed are available
  3. Load phase class dynamically
  4. Execute phase.execute(context)
  5. Update context with phase results
  6. Log artifacts_produced
       ↓
Return combined results
```

## Comparison: Static vs Dynamic

### Old Way (Static Orchestrator)

```python
# phases_orchestrator.py
from phase_1_discovery import DiscoveryPhase
from phase_2_tui_mapping import TuiMappingPhase
# ... hardcoded imports

class PhasesOrchestrator:
    def execute_all_phases(self):
        # Hardcoded execution order
        phase1 = DiscoveryPhase()
        result1 = phase1.execute()
        
        phase2 = TuiMappingPhase()
        result2 = phase2.execute()
        # ... etc
```

**Problems:**
- ❌ Changing order requires code changes
- ❌ Adding phases requires imports + code
- ❌ Can't skip phases without commenting code
- ❌ Hard to test different workflows

### New Way (Dynamic Orchestrator)

```python
# run_dynamic.py
orchestrator = DynamicOrchestrator()
orchestrator.execute_all_phases()  # Reads YAML!
```

**Benefits:**
- ✅ Change order in YAML only
- ✅ Add phases without code changes
- ✅ Skip phases by changing status
- ✅ Multiple workflows in same file

## Integration with Existing Code

The dynamic orchestrator is **fully compatible** with existing phase implementations. Each phase just needs an `execute(context)` method:

```python
class MyPhase:
    def __init__(self, project_root, ui):
        self.project_root = project_root
        self.ui = ui
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Do work here
        return {
            'my_output': 'result',
            'my_artifact': '/path/to/file'
        }
```

The orchestrator handles:
- Loading the phase class
- Passing the context
- Collecting results
- Artifact tracking

## Advanced Usage

### Custom Context

```python
orchestrator = DynamicOrchestrator(project_root)

custom_context = {
    'user_email': 'admin@example.com',
    'deployment_type': 'production',
    'skip_validation': False
}

result = orchestrator.execute_all_phases(context=custom_context)
```

### Programmatic Flow Info

```python
orchestrator = DynamicOrchestrator(project_root)

# Get flow metadata
info = orchestrator.get_flow_info('main_config_flow')

print(f"Total phases: {info['total_phases']}")
for phase in info['phases']:
    print(f"{phase['sequence']}. {phase['name']} - {phase['status']}")
```

### Multiple Flows

Define different workflows for different scenarios:

```yaml
flows:
  quick_config_flow:
    description: Quick configuration (minimal questions)
    phases:
      - phase_id: discovery
      - phase_id: export    # Skip collection!
  
  full_config_flow:
    description: Full interactive configuration
    phases:
      - phase_id: discovery
      - phase_id: tui_mapping
      - phase_id: collection
      - phase_id: validation
      - phase_id: export
```

Then run:
```bash
python3 run_dynamic.py --flow quick_config_flow
```

## Testing

### Test Flow Info

```bash
python3 run_dynamic.py --info --flow main_config_flow
```

### Dry Run (Just Load, Don't Execute)

```python
from phases.dynamic_orchestrator import DynamicOrchestrator

orchestrator = DynamicOrchestrator(project_root)
info = orchestrator.get_flow_info()
# Inspect without executing
```

### Test Individual Phases

Mark all other phases as `SKIPPED`:

```yaml
- phase_id: discovery
  status: IMPLEMENTED
  
- phase_id: tui_mapping
  status: SKIPPED    # Skip
  
- phase_id: collection
  status: SKIPPED    # Skip
```

## Troubleshooting

### "Flow not found"

Make sure `control_flows.yml` has your flow defined:
```yaml
flows:
  my_flow:
    phases: [...]
```

### "Phase class not found"

Check the `implementation` section:
```yaml
implementation:
  module: phases.phase_1_discovery
  class: DiscoveryPhase
```

### "Missing required artifact"

A phase needs an artifact that wasn't produced:
```yaml
# Phase 2 needs 'foo' but Phase 1 didn't produce it
- phase_id: phase2
  artifacts_consumed: [foo]  # ERROR if 'foo' not in context
```

Fix: Ensure earlier phases produce required artifacts.

## Migration Guide

### From Static to Dynamic

1. **Keep existing code** - No changes needed to phase implementations

2. **Add control_flows.yml** - Define your current workflow:
```yaml
flows:
  main_config_flow:
    phases:
      - phase_id: discovery
        sequence: 1
        # ... etc
```

3. **Use dynamic runner**:
```bash
python3 run_dynamic.py
```

4. **Test** that it produces same results

5. **Enhance** - Now you can easily add/remove/reorder phases!

## See Also

- `control_flows.yml` - Full flow specification
- `DynamicOrchestrator` class - Implementation details
- Control Flow Engine docs - Advanced control flow patterns

---

**Last Updated:** 2025-10-15  
**Status:** ✅ Fully Functional
