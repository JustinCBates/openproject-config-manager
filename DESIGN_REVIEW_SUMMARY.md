# Design Review Summary - Runtime YAML-Driven Execution

**Date:** October 15, 2025  
**Reviewed:** Control Flow System Documentation  
**Decision:** Design approach for runtime YAML execution

---

## Key Finding: The Functionality Was Partially Designed But Not Fully Implemented

### What Was Already Designed

✅ **Control Flow System** (`/opt/openproject/external/control-flow/`) has:
- Complete architecture for YAML-driven workflows
- `orchestrator_regenerator.py` tool for generating orchestrators
- Documentation of patterns and principles
- Marker system for generated vs handwritten code

✅ **Config Manager** (`control_flows.yml`) has:
- Complete YAML specification with flows → phases → steps → units
- Unit specifications (library.class.method)
- Artifact tracking and dependencies

### What Was Missing

❌ **Implementation Gap:**
- Orchestrator regenerator exists but **doesn't include runtime YAML reading**
- Generated orchestrators are **static** (hardcode step execution)
- No templates for **YAML-driven execution** at runtime
- Units specified in YAML but **not dynamically loaded**

---

## The Design Intent (From Control Flow Docs)

### Principle: YAML is Source of Truth

> "The control-flow system is **intentionally YAML-driven** because:
> 1. **Single source of truth** - Structure defined once, used everywhere
> 2. **Runtime flexibility** - Change workflow without code changes"

### The Reality

**Current State:** YAML is used for **generation** only (not runtime)

```
YAML → Generator → Static Code → Execute
```

**Intended State:** YAML should drive **runtime** execution

```
YAML → Runtime → Dynamic Execution
```

---

## Recommended Approach

### Option 1: Extend Orchestrator Regenerator (RECOMMENDED)

**Modify the generator to produce YAML-aware orchestrators:**

1. **Update Jinja2 templates** (create if missing):
   - Phase orchestrator template includes runtime YAML reading
   - Includes dynamic unit loading
   - Includes fallback to legacy execution

2. **Regenerate orchestrators** using updated templates:
   ```bash
   python3 orchestrator_regenerator.py \
       --spec control_flows.yml \
       --type phase \
       --orchestrator phases/phase_1_discovery/orchestrator_discovery.py \
       --phase-id discovery
   ```

3. **Result:** Generated orchestrators that:
   - Read `phase_spec` parameter from constructor
   - Execute steps from YAML dynamically
   - Load units using `importlib` based on YAML
   - Fall back to legacy execution if no YAML

**Pros:**
- ✅ Follows control-flow system "generate, don't handwrite" principle
- ✅ Consistent with existing architecture
- ✅ Maintains generated markers system
- ✅ Easy to regenerate when YAML changes

**Cons:**
- ⚠️ Need to create/update Jinja2 templates
- ⚠️ More upfront work to set up generator

### Option 2: Manual Base Class (ALTERNATIVE)

**Create base class manually:**

1. Create `YamlDrivenPhaseOrchestrator` base class
2. Update each phase to extend base class
3. Base class handles YAML reading and unit loading

**Pros:**
- ✅ Faster to implement initially
- ✅ Don't need to update generator

**Cons:**
- ❌ Violates "generate, don't handwrite" principle
- ❌ Manual updates needed for each phase
- ❌ No marker system for regeneration
- ❌ Inconsistent with control-flow architecture

---

## Proposed Architecture

### Structure

```
Global Orchestrator (PhasesOrchestrator)
    ├─ Loads control_flows.yml
    ├─ Gets flow['phases']
    └─ For each phase:
        ├─ Dynamically import phase class
        ├─ Pass spec_file and phase_spec to constructor
        └─ Call phase.execute(context)
                │
                └─> Phase Orchestrator (DiscoveryPhase)
                    ├─ Receives phase_spec in constructor
                    ├─ In execute(): Check if phase_spec exists
                    ├─ If yes: _execute_yaml_driven()
                    │   ├─ For each step in phase_spec['steps']:
                    │   │   ├─ Check step['status'] (skip if PLANNED)
                    │   │   ├─ If step has 'units':
                    │   │   │   └─ _execute_step_with_units()
                    │   │   │       └─ For each unit in step['units']:
                    │   │   │           ├─ importlib.import_module(f"phases.libraries.{library}")
                    │   │   │           ├─ getattr(module, class_name)
                    │   │   │           ├─ instance = unit_class()
                    │   │   │           └─ result = getattr(instance, method_name)()
                    │   │   └─ Else: _execute_step_traditional()
                    │   │       └─ Import and call Step class
                    │   └─ Return aggregated results
                    └─ If no: _execute_legacy()
                        └─ Hardcoded step execution (backward compat)
```

### Generated Orchestrator Example

```python
class DiscoveryPhase:
    def __init__(self, project_root: Path, ui=None, spec_file: Path = None, phase_spec: Dict[str, Any] = None):
        self.project_root = project_root
        self.ui = ui
        self.spec_file = spec_file
        self.phase_spec = phase_spec or self._load_phase_spec()
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Two execution modes: YAML-driven or legacy."""
        if self.phase_spec:
            return self._execute_yaml_driven(context)
        else:
            return self._execute_legacy(context)
    
    def _execute_yaml_driven(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Read steps from YAML, execute dynamically."""
        for step_spec in self.phase_spec.get('steps', []):
            if step_spec.get('status') in ['PLANNED', 'SKIPPED']:
                continue
            
            if 'units' in step_spec:
                step_result = self._execute_step_with_units(step_spec, context)
            else:
                step_result = self._execute_step_traditional(step_spec, context)
            
            context.update(step_result)
        return context
    
    def _execute_step_with_units(self, step_spec, context):
        """Dynamically load and execute units from YAML."""
        import importlib
        results = {}
        
        for unit in step_spec['units']:
            module = importlib.import_module(f"phases.libraries.{unit['library']}")
            unit_class = getattr(module, unit['class'])
            instance = unit_class()
            method = getattr(instance, unit['method'])
            results[unit['unit_id']] = method()
        
        return {'artifacts': results}
    
    # === GENERATED: STEP_EXECUTION - DO NOT EDIT ===
    def _execute_legacy(self, context):
        """Hardcoded step execution for backward compatibility."""
        # ... existing code preserved ...
    # === END GENERATED: STEP_EXECUTION ===
```

---

## Implementation Plan

### Phase 1: Verify Control Flow System (CURRENT)

- [x] Read control-flow system documentation
- [x] Understand orchestrator regenerator
- [x] Identify gap (generation-time vs runtime)
- [x] Design runtime YAML execution approach
- [x] Document design decision

### Phase 2: Create/Update Generator Templates

**Tasks:**
1. Check if Jinja2 templates exist in `/opt/openproject/external/control-flow/templates/`
2. If missing, create:
   - `phase_orchestrator_yaml_driven.py.j2`
   - `global_orchestrator_yaml_driven.py.j2`
3. Templates should include:
   - Constructor with `spec_file` and `phase_spec` parameters
   - `_execute_yaml_driven()` method
   - `_execute_step_with_units()` method
   - `_execute_legacy()` preserved in markers
   - Dynamic import logic

**Files to Create/Update:**
- `/opt/openproject/external/control-flow/templates/phase_orchestrator_yaml_driven.py.j2`
- `/opt/openproject/external/control-flow/src/control_flow_engine/core/orchestrator_regenerator.py` (update to use new template)

### Phase 3: Regenerate Config Manager Orchestrators

**Tasks:**
1. Test regenerator on discovery phase (dry-run first)
2. Review generated code
3. Apply regeneration
4. Test discovery phase execution
5. Repeat for remaining phases:
   - phase_2_tui_mapping
   - phase_3_collection
   - phase_4_validation
   - phase_5_export

**Commands:**
```bash
cd /opt/openproject/external/control-flow

# Test on discovery phase
python3 src/control_flow_engine/core/orchestrator_regenerator.py \
    --spec ../config-manager/design_specs/control_flows.yml \
    --type phase \
    --orchestrator ../config-manager/phases/phase_1_discovery/orchestrator_discovery.py \
    --phase-id discovery \
    --flow main_config_flow \
    --template yaml_driven \
    --dry-run

# Apply for real
python3 src/control_flow_engine/core/orchestrator_regenerator.py \
    --spec ../config-manager/design_specs/control_flows.yml \
    --type phase \
    --orchestrator ../config-manager/phases/phase_1_discovery/orchestrator_discovery.py \
    --phase-id discovery \
    --flow main_config_flow \
    --template yaml_driven
```

### Phase 4: Update Global Orchestrator

**Tasks:**
1. Update `phases/dynamic_orchestrator.py` or `phases/phases_orchestrator.py`
2. Ensure it passes `spec_file` and `phase_spec` to phase constructors
3. Test end-to-end execution

### Phase 5: Test & Validate

**Tasks:**
1. Test each phase individually
2. Test full pipeline execution
3. Verify YAML modifications work without code changes
4. Test backward compatibility (phases work without YAML)

---

## Open Questions for Discussion

### 1. Template Strategy

**Question:** Should we create new templates or modify existing ones?

**Options:**
- A) Create new templates (`*_yaml_driven.py.j2`) and keep old ones
- B) Update existing templates to include YAML-driven execution
- C) Make it configurable (--template flag)

**Recommendation:** Option A (create new templates)
- Safer - doesn't break existing generated code
- Clear separation - yaml_driven is opt-in
- Can test side-by-side

### 2. Generator Update Scope

**Question:** Should we update orchestrator_regenerator.py or create new tool?

**Options:**
- A) Update existing orchestrator_regenerator.py to support yaml_driven mode
- B) Create new tool (yaml_driven_generator.py)

**Recommendation:** Option A (update existing)
- Consistent with control-flow architecture
- Single tool, multiple modes
- Add `--runtime-yaml` flag

### 3. Migration Strategy

**Question:** Migrate all phases at once or incrementally?

**Options:**
- A) Migrate all phases simultaneously
- B) Migrate one phase at a time, test each
- C) Start with discovery, validate, then batch the rest

**Recommendation:** Option C
- Validate approach with discovery phase
- Iterate on template based on feedback
- Batch remaining phases once proven

### 4. Unit Loading Enhancement

**Question:** How to handle unit constructor parameters?

**Current:** Units instantiated with no args: `DockerDiscovery()`

**Future Need:** Some units may need parameters: `Validator(schema_file="...")`

**Options:**
- A) Leave for later (keep simple for now)
- B) Add `constructor_params` to unit spec in YAML
- C) Pass context to all units

**Recommendation:** Option A for initial implementation
- Add TODO for future enhancement
- Can extend YAML spec later

---

## Success Criteria

**Phase orchestrators should:**
- ✅ Read steps from `phase_spec` parameter (YAML-driven)
- ✅ Skip steps based on status (PLANNED/SKIPPED)
- ✅ Dynamically load units using importlib
- ✅ Execute units in sequence
- ✅ Fall back to legacy execution if no YAML
- ✅ Preserve handwritten code in markers
- ✅ Be regenerable from YAML changes

**System should enable:**
- ✅ Reorder steps by editing YAML (no code changes)
- ✅ Add new units by editing YAML
- ✅ Change step status to skip/enable steps
- ✅ Test with different YAML configurations

---

## Next Action

**DECISION NEEDED:** Should we proceed with Option 1 (extend generator)?

If yes, next steps:
1. Check existing templates in control-flow repo
2. Create phase_orchestrator_yaml_driven.py.j2 template
3. Update orchestrator_regenerator.py to use new template
4. Test on discovery phase

**Ready to proceed?**

