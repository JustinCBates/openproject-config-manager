# Dual-Mode Orchestration - Implementation Status

**Date:** October 15, 2025  
**Status:** ✅ Phase Orchestrators Complete, PathResolver Integration Pending

## Overview

All 5 phase orchestrators now support dual-mode execution:
- **Hardcoded Mode** (default): Traditional static step execution
- **Dynamic Mode** (--dynamic flag): YAML-driven execution with unit loading

## Completed Work

### 1. Phase Orchestrators (✅ Complete)

All 5 phase orchestrators have been updated with:

| Phase | File | Dual-Mode Support | --dynamic Flag | Helper Methods |
|-------|------|-------------------|----------------|----------------|
| Phase 1 | `orchestrator_discovery.py` | ✅ | ✅ | ✅ |
| Phase 2 | `orchestrator_tui_mapping.py` | ✅ | ✅ | ✅ |
| Phase 3 | `orchestrator_collection.py` | ✅ | ✅ | ✅ |
| Phase 4 | `orchestrator_validation.py` | ✅ | ✅ | ✅ |
| Phase 5 | `orchestrator_export.py` | ✅ | ✅ | ✅ |

### 2. Dual-Mode Infrastructure

Each orchestrator now has:

#### Constructor Parameters
```python
def __init__(
    self,
    project_root: Path,
    ui=None,
    mode: str = 'hardcoded',
    spec_file: Optional[Path] = None,
    phase_spec: Optional[Dict[str, Any]] = None
):
```

#### Mode Switching
```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    if self.mode == "dynamic":
        return self._execute_dynamic(context)
    else:
        return self._execute_hardcoded(context)
```

#### Helper Methods
- ✅ `_execute_dynamic()` - Read steps from YAML and execute
- ✅ `_execute_hardcoded()` - Original static execution
- ✅ `_execute_step_with_units()` - Dynamically load and execute units
- ✅ `_execute_step_traditional()` - Fall back to Step classes
- ✅ `_mock_unit_execution()` - Mock unimplemented units
- ✅ `_build_result()` - Build final result dictionary

#### CLI Support
```bash
python3 phases/phase_X_*/orchestrator_*.py --dynamic
```

### 3. Import Verification

All orchestrators import successfully:
```python
✅ phase_1_discovery: Import successful
✅ phase_2_tui_mapping: Import successful
✅ phase_3_collection: Import successful
✅ phase_4_validation: Import successful
✅ phase_5_export: Import successful
```

## Known Issues & Next Steps

### Issue #1: PathResolver Integration Missing

**Problem:** PathResolver was designed to handle dynamic loading and artifact resolution, but it's not currently being used in the dual-mode methods.

**Current State:**
- PathResolver exists and works (see `/opt/openproject/test_path_resolver.py`)
- Orchestrators initialize PathResolver in some cases (e.g., phase_3)
- But `_execute_dynamic()` and helper methods don't use it

**What PathResolver Should Do:**
1. Resolve artifact paths dynamically
2. Potentially: Load units dynamically (needs extension)
3. Resolve library paths for unit imports
4. Validate artifact accessibility

**Required Changes:**
1. Initialize PathResolver in all orchestrators' `__init__()`
2. Use `resolver.resolve_artifact_path()` in `_build_result()`
3. Consider: Extend PathResolver with `load_unit()` method
4. Use PathResolver in `_execute_step_with_units()` for dynamic imports

**Example of Needed Integration:**
```python
def __init__(self, ...):
    # Initialize PathResolver
    try:
        self.path_resolver = PathResolver.from_execution_context(__file__)
    except Exception as e:
        logger.warning(f"Could not initialize PathResolver: {e}")
        self.path_resolver = None

def _execute_step_with_units(self, step_spec, context):
    # Use PathResolver to find and load units
    for unit_spec in units:
        if self.path_resolver:
            # Let PathResolver handle the import
            unit_instance = self.path_resolver.load_unit(
                library=unit_spec['library'],
                class_name=unit_spec['class']
            )
        else:
            # Fallback to manual import
            module_path = f"phases.libraries.{library}"
            ...
```

### Issue #2: Global Orchestrator Not Updated

**Status:** ⏳ Pending

The global orchestrator (`phases/phases_orchestrator.py`) hasn't been updated with dual-mode support yet.

**Required:**
- Add mode parameter
- Add `--dynamic` flag
- Pass mode to phase orchestrators when calling them

### Issue #3: Phase 3 Units Pattern

**Status:** ⏳ Pending

Phase 3 (Interactive Collection) doesn't use the units pattern yet. It should have:
- `libraries/interactive/tui_caller.py` - Unit for TUI interactions
- Updated `control_flows.yml` with unit specifications

## Testing Status

### Unit Tests
- ❌ Not yet created for dual-mode functionality

### Integration Tests
- ⏳ Need to test:
  - Each phase in dynamic mode individually
  - Global orchestrator in dynamic mode (once updated)
  - Unit loading from YAML
  - Path resolver integration
  - Fallback to hardcoded mode

### Manual Testing
```bash
# Test individual phases in dynamic mode
cd /opt/openproject/external/config-manager
python3 phases/phase_1_discovery/orchestrator_discovery.py --dynamic

# Test hardcoded mode (default)
python3 phases/phase_1_discovery/orchestrator_discovery.py
```

## Design Decisions

### Why PathResolver Should Handle Loading

**Original Design:**
PathResolver was meant to be the single source of truth for:
- Where artifacts are located
- Where units are located
- How to dynamically import components

**Current Reality:**
- PathResolver only handles path resolution
- Unit loading is done manually with `importlib` in each orchestrator
- This violates DRY and makes it harder to refactor library structure

**Recommendation:**
Extend PathResolver with:
```python
class PathResolver:
    def load_unit(
        self,
        library: str,
        class_name: str,
        unit_id: Optional[str] = None
    ) -> object:
        """
        Dynamically load a unit class from a library.
        
        Uses control_flows.yml to find the library location,
        then imports and returns the class.
        """
        # Implementation here
```

## Files Modified

### Phase Orchestrators
- `/opt/openproject/external/config-manager/phases/phase_1_discovery/orchestrator_discovery.py`
- `/opt/openproject/external/config-manager/phases/phase_2_tui_mapping/orchestrator_tui_mapping.py`
- `/opt/openproject/external/config-manager/phases/phase_3_collection/orchestrator_collection.py`
- `/opt/openproject/external/config-manager/phases/phase_4_validation/orchestrator_validation.py`
- `/opt/openproject/external/config-manager/phases/phase_5_export/orchestrator_export.py`

### Templates
- `/opt/openproject/external/control-flow/templates/phase_orchestrator_dual_mode.py.j2`
- `/opt/openproject/external/control-flow/templates/global_orchestrator_dual_mode.py.j2`

### Tools
- `/opt/openproject/external/control-flow/src/control_flow_engine/core/orchestrator_regenerator.py`

### Scripts Used
- `/tmp/add_helper_methods.py` - Added missing helper methods to all orchestrators
- `/tmp/fix_orchestrators.py` - Fixed syntax errors from regenerator
- `/tmp/fix_all_orchestrators.py` - Comprehensive fix for all phases

## Next Actions

### Priority 1: PathResolver Integration
1. Add PathResolver initialization to all orchestrator `__init__()` methods
2. Update `_build_result()` to use `resolver.resolve_artifact_path()`
3. Consider extending PathResolver with `load_unit()` method
4. Update `_execute_step_with_units()` to use PathResolver

### Priority 2: Global Orchestrator
1. Apply dual-mode pattern to `phases_orchestrator.py`
2. Add `--dynamic` flag
3. Pass mode to phase orchestrators

### Priority 3: Phase 3 Refactoring
1. Create `libraries/interactive/` directory
2. Create `tui_caller.py` unit
3. Update `control_flows.yml` with unit specs
4. Test phase 3 in dynamic mode

### Priority 4: Testing
1. Create unit tests for dual-mode execution
2. Test each phase with `--dynamic` flag
3. Test global orchestrator end-to-end
4. Document test procedures

## Success Criteria

- [x] All 5 phase orchestrators support --dynamic flag
- [x] All orchestrators import successfully
- [x] Helper methods present in all orchestrators
- [ ] PathResolver properly integrated
- [ ] Global orchestrator supports dual-mode
- [ ] Phase 3 uses units pattern
- [ ] All tests pass
- [ ] Documentation complete

## References

- Control Flow System Documentation: `/opt/openproject/external/control-flow/docs/CONTROL_FLOW_SYSTEM_REFERENCE.md`
- PathResolver Test: `/opt/openproject/test_path_resolver.py`
- YAML Specification: `/opt/openproject/external/config-manager/design_specs/control_flows.yml`
