# Phase and Step Refactoring Strategy

## Problem Statement

The current control flow system has **hardcoded numbering** in directory names, file imports, and orchestrator logic:
- Directories: `phase_1_discovery`, `phase_2_tui_mapping`, etc.
- Imports: `from phases.phase_1_discovery.orchestrator_discovery import DiscoveryPhase`
- Step references: `step_1_env_discovery`, `step_2_system_discovery`, etc.

**This creates brittleness when:**
1. **Deleting** a phase (e.g., removing phase_3 leaves a gap: phase_1, phase_2, phase_4, phase_5)
2. **Inserting** a phase (e.g., adding a new phase between 2 and 3 requires renumbering all subsequent phases)
3. **Reordering** phases (e.g., swapping phase_2 and phase_3 requires renaming directories and updating imports)
4. **Deleting/Moving Steps** within a phase (same numbering issues at step level)

## Current Architecture Analysis

### Hardcoded Dependencies

#### 1. Directory Structure
```
phases/
├── phase_1_discovery/
│   ├── step_1_env_discovery/
│   ├── step_2_system_discovery/
│   └── step_3_defaults_generation/
├── phase_2_tui_mapping/
├── phase_3_collection/
├── phase_4_validation/
└── phase_5_export/
```

**Issues:**
- Directory names contain sequence numbers
- Filesystem doesn't allow gaps in numbering logically
- Renaming directories breaks imports

#### 2. Python Imports (Hardcoded Paths)

**Main Orchestrator** (`phases_orchestrator.py`):
```python
from phases.phase_1_discovery.orchestrator_discovery import DiscoveryPhase
from phases.phase_2_tui_mapping.orchestrator_tui_mapping import TuiMappingPhase
from phases.phase_3_collection.orchestrator_collection import CollectionPhase
# ... etc
```

**Phase Orchestrators** (e.g., `orchestrator_discovery.py`):
```python
from .step_1_env_discovery import env_discovery
from .step_2_system_discovery import system_discovery
from .step_3_defaults_generation import defaults_generation
```

**Issues:**
- Import paths hardcoded with sequence numbers
- Changing order requires updating all import statements
- No dynamic import mechanism

#### 3. Orchestrator Logic (Hardcoded References)

```python
class PhasesOrchestrator:
    def __init__(self, project_root: Path, ui=None):
        self.discovery_phase = DiscoveryPhase(project_root, ui)
        self.tui_mapping_phase = TuiMappingPhase(project_root, ui)
        # ... hardcoded for each phase
        
    def execute_phase(self, phase_number: int, context: Dict[str, Any]):
        if phase_number == 1:
            return self.discovery_phase.execute(context)
        elif phase_number == 2:
            return self.tui_mapping_phase.execute(context)
        # ... hardcoded if-elif chain
```

**Issues:**
- Phase number directly mapped to phase object
- Adding/removing phases requires code changes
- No registry or discovery mechanism

#### 4. control_flows.yml (Mixed Numbering)

```yaml
flows:
  main_config_flow:
    phases:
      - phase_id: "discovery"  # ✅ Good: semantic ID
        implementation:
          phase_directory: "phases/phase_1_discovery/"  # ❌ Bad: numbered path
          module: "phases.phase_1_discovery"  # ❌ Bad: numbered import
```

**Issues:**
- `phase_id` is semantic (good!)
- But `phase_directory` and `module` are numbered (bad!)
- Disconnect between logical ID and physical structure

## Proposed Solutions

### Solution 1: Semantic Directory Names (Recommended)

**Replace numbered directories with semantic names:**

```
phases/
├── discovery/              # was phase_1_discovery
│   ├── env_discovery/      # was step_1_env_discovery
│   ├── system_discovery/   # was step_2_system_discovery
│   └── defaults_generation/ # was step_3_defaults_generation
├── tui_mapping/            # was phase_2_tui_mapping
├── collection/             # was phase_3_collection
├── validation/             # was phase_4_validation
└── export/                 # was phase_5_export
```

**Advantages:**
✅ No renumbering needed when reordering
✅ More readable and self-documenting
✅ Aligns with `phase_id` in control_flows.yml
✅ Deletion doesn't create gaps
✅ Insertion doesn't require renaming

**Disadvantages:**
⚠️ Loses explicit ordering in filesystem (but order defined in control_flows.yml)
⚠️ Requires migration of existing code
⚠️ Breaks existing imports temporarily

**Implementation Impact:**
- **control_flows.yml**: Update all `phase_directory` and `module` paths
- **Orchestrator imports**: Change from `phase_1_discovery` to `discovery`
- **Test imports**: Update all test file imports
- **Documentation**: Update all path references

---

### Solution 2: Manifest-Based Ordering

**Keep numbered directories but add a phase registry:**

Create `phases/phases_manifest.yml`:
```yaml
phases:
  - phase_number: 1
    phase_id: "discovery"
    directory: "phase_1_discovery"
    module: "phases.phase_1_discovery"
    orchestrator_class: "DiscoveryPhase"
    
  - phase_number: 2
    phase_id: "tui_mapping"
    directory: "phase_2_tui_mapping"
    module: "phases.phase_2_tui_mapping"
    orchestrator_class: "TuiMappingPhase"
```

**Dynamic orchestrator:**
```python
class PhasesOrchestrator:
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phases = self._load_phases_from_manifest()
        
    def _load_phases_from_manifest(self):
        manifest_file = self.project_root / "phases/phases_manifest.yml"
        with open(manifest_file) as f:
            manifest = yaml.safe_load(f)
        
        phases = {}
        for phase_config in manifest['phases']:
            # Dynamic import
            module = importlib.import_module(phase_config['module'])
            class_obj = getattr(module, phase_config['orchestrator_class'])
            phases[phase_config['phase_number']] = class_obj(self.project_root, self.ui)
        
        return phases
    
    def execute_phase(self, phase_number: int, context: Dict[str, Any]):
        return self.phases[phase_number].execute(context)
```

**Advantages:**
✅ Centralized phase configuration
✅ Easy to reorder (just change `phase_number` in manifest)
✅ Dynamic loading eliminates hardcoded imports
✅ Can keep numbered directories

**Disadvantages:**
⚠️ Still requires renaming directories to reorder
⚠️ Adds complexity with dynamic imports
⚠️ Manifest can get out of sync with filesystem

---

### Solution 3: Hybrid Approach (Best of Both)

**Use semantic names + execution order in control_flows.yml:**

**Directory structure:**
```
phases/
├── discovery/
├── tui_mapping/
├── collection/
├── validation/
├── export/
└── phases_orchestrator.py
```

**control_flows.yml already defines order:**
```yaml
flows:
  main_config_flow:
    description: "Primary Configuration Process"
    phases:
      - phase_id: "discovery"       # Order = position in list (1st)
      - phase_id: "tui_mapping"     # Order = position in list (2nd)
      - phase_id: "collection"      # Order = position in list (3rd)
      - phase_id: "validation"      # Order = position in list (4th)
      - phase_id: "export"          # Order = position in list (5th)
```

**Dynamic orchestrator using control_flows.yml:**
```python
class PhasesOrchestrator:
    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phases_dir = project_root / "phases"
        
        # Load phases from control_flows.yml
        self.phase_configs = self._load_phase_configs()
        self.phases = self._initialize_phases()
        
    def _load_phase_configs(self):
        """Load phase configuration from control_flows.yml"""
        spec_file = self.project_root / "design_specs/control_flows.yml"
        with open(spec_file) as f:
            spec = yaml.safe_load(f)
        
        # Extract phase list (order preserved)
        main_flow = spec['flows']['main_config_flow']
        return main_flow['phases']
    
    def _initialize_phases(self):
        """Dynamically initialize phases based on config"""
        phases = {}
        
        for idx, phase_config in enumerate(self.phase_configs, start=1):
            phase_id = phase_config['phase_id']
            impl = phase_config['implementation']
            
            # Dynamic import using semantic name
            module_path = impl['module']  # e.g., "phases.discovery"
            class_name = impl['class']     # e.g., "DiscoveryPhase"
            
            module = importlib.import_module(module_path)
            phase_class = getattr(module, class_name)
            phases[idx] = {
                'id': phase_id,
                'instance': phase_class(self.project_root, self.ui),
                'config': phase_config
            }
        
        return phases
    
    def execute_phase(self, phase_number: int, context: Dict[str, Any]):
        """Execute phase by number (based on order in control_flows.yml)"""
        if phase_number not in self.phases:
            raise ValueError(f"Phase {phase_number} not found")
        
        phase_info = self.phases[phase_number]
        logger.info(f"Executing Phase {phase_number}: {phase_info['id']}")
        
        return phase_info['instance'].execute(context)
```

**Advantages:**
✅ Semantic directory names (readable, no numbers)
✅ Order defined in control_flows.yml (single source of truth)
✅ Dynamic loading eliminates hardcoded imports
✅ Reordering = just rearrange in control_flows.yml
✅ Deletion = remove from control_flows.yml
✅ Insertion = add anywhere in control_flows.yml list
✅ No separate manifest file needed

**Disadvantages:**
⚠️ More complex initialization logic
⚠️ Requires migration from current structure

---

## Recommended Approach: Solution 3 (Hybrid)

### Migration Path

#### Phase 1: Rename Directories (Semantic Names)

1. **Rename phase directories:**
   ```bash
   mv phases/phase_1_discovery phases/discovery
   mv phases/phase_2_tui_mapping phases/tui_mapping
   mv phases/phase_3_collection phases/collection
   mv phases/phase_4_validation phases/validation
   mv phases/phase_5_export phases/export
   ```

2. **Rename step directories within each phase:**
   ```bash
   cd phases/discovery
   mv step_1_env_discovery env_discovery
   mv step_2_system_discovery system_discovery
   mv step_3_defaults_generation defaults_generation
   ```

3. **Update control_flows.yml:**
   ```yaml
   implementation:
     phase_directory: "phases/discovery/"  # was phase_1_discovery
     module: "phases.discovery"             # was phases.phase_1_discovery
   ```

4. **Update all imports:**
   - Main orchestrator
   - Phase orchestrators
   - Step entry points
   - Test files

#### Phase 2: Implement Dynamic Loading

1. **Refactor phases_orchestrator.py:**
   - Remove hardcoded imports
   - Add `_load_phase_configs()` method
   - Add `_initialize_phases()` method
   - Update `execute_phase()` to use dynamic registry

2. **Add importlib support:**
   ```python
   import importlib
   import yaml
   ```

3. **Update control_flows.yml if needed:**
   - Ensure each phase has correct `module` and `class` fields
   - Verify order matches desired execution sequence

#### Phase 3: Implement Refactoring Tools

Create utility scripts to automate common operations:

**1. `scripts/reorder_phases.py`:**
```python
#!/usr/bin/env python3
"""Reorder phases by updating control_flows.yml"""
import yaml
from pathlib import Path

def reorder_phases(control_flows_file, new_order):
    """
    new_order = ['discovery', 'collection', 'tui_mapping', 'validation', 'export']
    """
    with open(control_flows_file) as f:
        spec = yaml.safe_load(f)
    
    phases = spec['flows']['main_config_flow']['phases']
    phase_dict = {p['phase_id']: p for p in phases}
    
    # Reorder
    spec['flows']['main_config_flow']['phases'] = [
        phase_dict[phase_id] for phase_id in new_order
    ]
    
    with open(control_flows_file, 'w') as f:
        yaml.dump(spec, f, sort_keys=False)
```

**2. `scripts/delete_phase.py`:**
```python
#!/usr/bin/env python3
"""Delete a phase gracefully"""
import yaml
import shutil
from pathlib import Path

def delete_phase(control_flows_file, phase_id):
    # 1. Remove from control_flows.yml
    with open(control_flows_file) as f:
        spec = yaml.safe_load(f)
    
    phases = spec['flows']['main_config_flow']['phases']
    spec['flows']['main_config_flow']['phases'] = [
        p for p in phases if p['phase_id'] != phase_id
    ]
    
    with open(control_flows_file, 'w') as f:
        yaml.dump(spec, f, sort_keys=False)
    
    # 2. Remove directory (with backup)
    phase_dir = Path(f"phases/{phase_id}")
    if phase_dir.exists():
        backup_dir = Path(f"phases/.deleted/{phase_id}")
        backup_dir.parent.mkdir(exist_ok=True)
        shutil.move(str(phase_dir), str(backup_dir))
        print(f"Phase directory moved to {backup_dir}")
    
    # 3. Update main orchestrator (if not using dynamic loading)
    # ... or skip if dynamic loading is implemented
```

**3. `scripts/insert_phase.py`:**
```python
#!/usr/bin/env python3
"""Insert a new phase at a specific position"""
import yaml
from pathlib import Path

def insert_phase(control_flows_file, new_phase_config, position):
    with open(control_flows_file) as f:
        spec = yaml.safe_load(f)
    
    phases = spec['flows']['main_config_flow']['phases']
    phases.insert(position, new_phase_config)
    
    with open(control_flows_file, 'w') as f:
        yaml.dump(spec, f, sort_keys=False)
```

---

## Step-Level Refactoring

The same principles apply to steps within phases:

### Current Structure
```
phases/discovery/
├── step_1_env_discovery/
├── step_2_system_discovery/
└── step_3_defaults_generation/
```

### Proposed Structure
```
phases/discovery/
├── env_discovery/
├── system_discovery/
└── defaults_generation/
```

### Step Order Definition

**Option A: In control_flows.yml (Recommended)**
```yaml
phases:
  - phase_id: "discovery"
    sub_flows: ["discovery_flow"]

sub_flows:
  discovery_flow:
    steps:
      - step_id: "env_discovery"
      - step_id: "system_discovery"
      - step_id: "defaults_generation"
```

**Option B: In phase orchestrator**
```python
class DiscoveryPhase:
    def __init__(self, project_root: Path, ui=None):
        self.step_order = [
            'env_discovery',
            'system_discovery',
            'defaults_generation'
        ]
        self.steps = self._load_steps()
    
    def _load_steps(self):
        steps = {}
        for step_id in self.step_order:
            module = importlib.import_module(f'.{step_id}', package='phases.discovery')
            steps[step_id] = module
        return steps
```

---

## Impact Analysis

### Files Requiring Updates

1. **control_flows.yml**
   - All `phase_directory` paths
   - All `module` import paths
   - All `dependencies` file paths

2. **phases_orchestrator.py**
   - Remove hardcoded imports
   - Add dynamic loading logic
   - Update execute_phase logic

3. **Each phase orchestrator**
   - Update step imports (if using semantic names)
   - Update self.phase_dir paths

4. **All test files**
   - Update import statements
   - Update path references

5. **Documentation**
   - README.md files
   - Design specs
   - AI context

### Estimated Migration Effort

- **Small project** (5 phases, 15 steps): 2-4 hours
- **Medium project** (10 phases, 30 steps): 4-8 hours
- **Large project** (20+ phases, 60+ steps): 8-16 hours

Automation scripts can reduce this significantly.

---

## Rollback Strategy

1. **Git branches:**
   ```bash
   git checkout -b feature/semantic-phase-names
   # Do migration
   # Test thoroughly
   git merge feature/semantic-phase-names
   ```

2. **Backup before renaming:**
   ```bash
   tar -czf phases_backup_$(date +%Y%m%d).tar.gz phases/
   ```

3. **Incremental migration:**
   - Migrate one phase at a time
   - Test after each phase
   - Commit after successful test

---

## Future-Proofing

Once dynamic loading is implemented:

1. **Adding a phase:** Just add to control_flows.yml
2. **Removing a phase:** Just remove from control_flows.yml
3. **Reordering phases:** Just rearrange in control_flows.yml
4. **Renaming a phase:** Rename directory + update control_flows.yml

**No code changes required in orchestrator!**

---

## Recommendation Summary

**Short term (Next sprint):**
1. ✅ Implement Solution 3 (Hybrid Approach)
2. ✅ Migrate config-manager to semantic names
3. ✅ Create migration scripts for future use

**Long term (Within quarter):**
1. ✅ Apply same pattern to all components
2. ✅ Document in control flow system guide
3. ✅ Add validation in control flow generator

**Priority: HIGH**  
**Risk: MEDIUM** (requires careful testing)  
**Benefit: HIGH** (eliminates entire class of refactoring issues)

---

## Questions for Discussion

1. Should we migrate all components at once or incrementally?
2. Should step ordering be in control_flows.yml or phase orchestrator?
3. Should we auto-generate migration scripts from control_flows.yml?
4. Should the control flow generator enforce semantic naming for new projects?

