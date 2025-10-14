# Control Flow Engine: Migration Best Practices

**Date**: October 14, 2025  
**Status**: Design Specification

## 🎯 Overview

The Control Flow Engine should support **safe, automated migrations** when restructuring flows. This requires:

1. **Consistent naming conventions** that enable programmatic manipulation
2. **Migration file generation** that documents and executes changes
3. **Validation** to prevent breaking changes
4. **Rollback capabilities** for failed migrations

---

## Best Practices for Migration-Friendly Code

### 1. File Path Conventions

#### ✅ GOOD: Programmatic, Predictable Paths

```python
# Pattern: phases/phase_{sequence}_{phase_id}/step_{sequence}_{step_id}/{step_id}.py

# Examples:
phases/phase_1_discovery/step_0_env_discovery/env_discovery.py
phases/phase_2_validation/step_1_schema_check/schema_check.py
phases/phase_3_generation/step_0_render_config/render_config.py
```

**Why Good**:
- ✅ Easy to parse with regex: `phase_(\d+)_(\w+)`
- ✅ Sequence numbers allow reordering
- ✅ IDs allow renaming without breaking references
- ✅ Can extract metadata from path alone

#### ❌ BAD: Hardcoded, Inconsistent Paths

```python
# Examples of what NOT to do:
phases/discovery/env_check.py                    # No sequence numbers
phases/phase1/step1.py                           # No descriptive IDs
phases/discover_stuff/check_environment.py       # Inconsistent naming
phases/p1_discovery/s0_env/env.py               # Abbreviated, unclear
```

**Why Bad**:
- ❌ Hard to reorder (no sequence)
- ❌ Unclear purpose (no descriptive ID)
- ❌ Difficult to parse programmatically
- ❌ References will break when renaming

### 2. Import Path Conventions

#### ✅ GOOD: Relative to Project Root

```python
# Always import from project root
from phases.phase_1_discovery.step_0_env_discovery import env_discovery

# Or use dynamic imports based on spec
phase_module = f"phases.phase_{seq}_{phase_id}"
step_module = f"{phase_module}.step_{step_seq}_{step_id}.{step_id}"
module = importlib.import_module(step_module)
```

**Why Good**:
- ✅ Works from anywhere in project
- ✅ Can be programmatically updated
- ✅ Clear, absolute reference
- ✅ No path manipulation needed

#### ❌ BAD: Relative Imports with Path Manipulation

```python
# Don't do this:
import sys
sys.path.insert(0, '../../..')
from env_discovery import execute_env_discovery

# Or this:
from ...step_0_env_discovery import env_discovery
```

**Why Bad**:
- ❌ Breaks when file moves
- ❌ Different behavior depending on where run from
- ❌ Hard to update programmatically
- ❌ Difficult to track dependencies

### 3. Variable Naming in Code

#### ✅ GOOD: Use IDs, Not Display Names

```python
# In orchestrator
class DiscoveryPhase:
    def execute(self, context):
        # Reference by ID
        env_data = self.run_step('env_discovery', context)
        sys_data = self.run_step('system_discovery', context)
        
        # Not by display name
        # env_data = self.run_step('Environment Discovery', context)  # BAD
```

**Why Good**:
- ✅ IDs are stable (won't change)
- ✅ Can be used as dictionary keys
- ✅ Easy to search/replace
- ✅ No spaces/special characters

#### ✅ GOOD: Store Phase/Step Metadata

```python
# In orchestrator, store IDs as constants
class DiscoveryPhase:
    PHASE_ID = "discovery"
    PHASE_SEQUENCE = 1
    
    STEPS = [
        "env_discovery",
        "system_discovery",
        "defaults_generation"
    ]
    
    def execute(self, context):
        for step_id in self.STEPS:
            self.run_step(step_id, context)
```

**Why Good**:
- ✅ Easy to update during migration
- ✅ Self-documenting
- ✅ Can validate against spec
- ✅ Single source of truth

### 4. YAML Specification Practices

#### ✅ GOOD: Use Consistent IDs

```yaml
flows:
  main_config_flow:
    phases:
    - phase_id: discovery              # Stable ID
      sequence: 1                      # Can change during reorder
      name: Discovery Phase            # Can change during rename
      implementation:
        phase_directory: phases/phase_1_discovery/
        orchestrator_file: phases/phase_1_discovery/orchestrator_discovery.py
        class: DiscoveryPhase
        
      steps:
      - step_id: env_discovery         # Stable ID
        sequence: 0                    # Can change
        name: Environment Discovery    # Can change
        implementation:
          file: phases/phase_1_discovery/step_0_env_discovery/env_discovery.py
          function: execute_env_discovery
```

**Why Good**:
- ✅ Clear separation: ID (stable) vs Name (can change)
- ✅ Sequence allows reordering
- ✅ Implementation paths can be derived from IDs
- ✅ Easy to track renames (ID stays, name changes)

#### ❌ BAD: Mixing IDs and Names

```yaml
# Don't do this:
phases:
- name: Discovery Phase              # Used as both ID and display name
  steps:
  - name: Environment Discovery      # No way to rename safely
```

**Why Bad**:
- ❌ Can't rename without breaking references
- ❌ No way to track identity across renames
- ❌ Difficult to validate

---

## Migration File System

### Migration File Format

```python
# migrations/migration_001_rename_discovery_phase.py
"""
Migration: Rename Discovery Phase to System Detection Phase
Date: 2025-10-14
Author: Control Flow Engine

Changes:
- Rename phase: discovery → system_detection
- Rename step: env_discovery → environment_check
- Move step: system_discovery from discovery to new monitoring phase
- Delete step: deprecated_old_step
"""

from control_flow_engine.migration import Migration, Operation

migration = Migration(
    id="001_rename_discovery_phase",
    description="Rename Discovery Phase to System Detection Phase",
    operations=[
        # Rename operations
        Operation.rename_phase(
            old_id="discovery",
            new_id="system_detection",
            old_name="Discovery Phase",
            new_name="System Detection Phase",
            old_sequence=1,
            new_sequence=1  # Stays same
        ),
        
        Operation.rename_step(
            phase_id="system_detection",  # Uses new ID
            old_step_id="env_discovery",
            new_step_id="environment_check",
            old_name="Environment Discovery",
            new_name="Environment Check",
            old_sequence=0,
            new_sequence=0
        ),
        
        # Move operations
        Operation.move_step(
            from_phase="system_detection",
            to_phase="monitoring",
            step_id="system_discovery",
            old_sequence=1,
            new_sequence=0
        ),
        
        # Delete operations
        Operation.delete_step(
            phase_id="system_detection",
            step_id="deprecated_old_step",
            reason="No longer needed, replaced by environment_check"
        ),
        
        # Insert operations
        Operation.insert_step(
            phase_id="system_detection",
            step_id="new_validation_step",
            sequence=2,
            create_scaffolding=True
        ),
        
        # Reorder operations
        Operation.reorder_phases(
            new_order=["system_detection", "validation", "monitoring", "generation"]
        )
    ]
)

# Auto-generated implementation
def upgrade():
    """Apply migration."""
    migration.apply()

def downgrade():
    """Rollback migration."""
    migration.rollback()
```

### What Migration Does

```
1. VALIDATION PHASE
   ├─ Check no conflicts
   ├─ Verify all referenced files exist
   ├─ Detect circular dependencies
   └─ Validate naming conventions

2. DRY RUN (optional)
   ├─ Show what will change
   ├─ List all file operations
   ├─ Show YAML diffs
   └─ Estimate impact

3. BACKUP PHASE
   ├─ Create backup of control_flows.yml
   ├─ Git stash if changes present
   └─ Save state for rollback

4. EXECUTION PHASE
   ├─ Rename directories
   ├─ Rename files
   ├─ Update imports in code
   ├─ Update orchestrator references
   ├─ Update control_flows.yml
   └─ Update any config files

5. VERIFICATION PHASE
   ├─ Check all imports still work
   ├─ Validate YAML structure
   ├─ Run smoke tests
   └─ Report success/failure

6. CLEANUP PHASE
   ├─ Remove backups if successful
   ├─ Commit changes if requested
   └─ Generate migration report
```

---

## Migration Operations Detail

### 1. Rename Phase

**What It Does**:
- Renames directory: `phase_{seq}_{old_id}` → `phase_{seq}_{new_id}`
- Updates orchestrator filename: `orchestrator_{old_id}.py` → `orchestrator_{new_id}.py`
- Updates orchestrator class name: `{OldId}Phase` → `{NewId}Phase`
- Updates all imports referencing this phase
- Updates control_flows.yml

**Files Changed**:
```
phases/phase_1_discovery/ → phases/phase_1_system_detection/
├─ orchestrator_discovery.py → orchestrator_system_detection.py
│  └─ class DiscoveryPhase → class SystemDetectionPhase
└─ All step imports updated

control_flows.yml:
  phase_id: discovery → system_detection
  name: Discovery Phase → System Detection Phase
  implementation.phase_directory: updated
  implementation.orchestrator_file: updated
  implementation.class: updated

run_phases.py:
  from phases.phase_1_discovery import DiscoveryPhase
  → from phases.phase_1_system_detection import SystemDetectionPhase
```

**Migration Code**:
```python
Operation.rename_phase(
    old_id="discovery",
    new_id="system_detection",
    old_name="Discovery Phase",
    new_name="System Detection Phase",
    old_sequence=1,
    new_sequence=1,
    update_references=True  # Update all code references
)
```

### 2. Rename Step

**What It Does**:
- Renames directory: `step_{seq}_{old_id}` → `step_{seq}_{new_id}`
- Renames implementation file: `{old_id}.py` → `{new_id}.py`
- Renames function: `execute_{old_id}` → `execute_{new_id}`
- Renames layout file if TUI: `{old_id}.layout.yml` → `{new_id}.layout.yml`
- Updates imports in orchestrator
- Updates control_flows.yml

**Files Changed**:
```
phases/phase_1_discovery/step_0_env_discovery/
→ phases/phase_1_discovery/step_0_environment_check/
├─ env_discovery.py → environment_check.py
│  └─ def execute_env_discovery() → def execute_environment_check()
├─ env_discovery.layout.yml → environment_check.layout.yml (if exists)
└─ __init__.py: Updated exports

orchestrator_discovery.py:
  from .step_0_env_discovery import env_discovery
  → from .step_0_environment_check import environment_check
  
  result = env_discovery.execute_env_discovery(context)
  → result = environment_check.execute_environment_check(context)

control_flows.yml:
  step_id: env_discovery → environment_check
  name: Environment Discovery → Environment Check
  implementation.file: updated
  implementation.function: updated
```

**Migration Code**:
```python
Operation.rename_step(
    phase_id="discovery",
    old_step_id="env_discovery",
    new_step_id="environment_check",
    old_name="Environment Discovery",
    new_name="Environment Check",
    old_sequence=0,
    new_sequence=0,
    update_function_name=True,
    update_references=True
)
```

### 3. Move Step

**What It Does**:
- Moves directory to new phase
- Updates imports in both orchestrators (remove from old, add to new)
- Updates control_flows.yml
- May renumber sequences in both phases

**Files Changed**:
```
phases/phase_1_discovery/step_1_system_discovery/
→ phases/phase_3_monitoring/step_0_system_discovery/

orchestrator_discovery.py:
  # Remove import and call

orchestrator_monitoring.py:
  # Add import and call

control_flows.yml:
  flows.main_config_flow.phases[0].steps:
    - Remove system_discovery entry
  flows.main_config_flow.phases[2].steps:
    - Add system_discovery entry with new sequence
```

**Migration Code**:
```python
Operation.move_step(
    from_phase="discovery",
    to_phase="monitoring",
    step_id="system_discovery",
    old_sequence=1,
    new_sequence=0,
    renumber_remaining=True  # Renumber other steps
)
```

### 4. Delete Step

**What It Does**:
- Optionally archives directory (doesn't delete permanently)
- Removes imports from orchestrator
- Updates control_flows.yml
- Renumbers remaining steps

**Files Changed**:
```
phases/phase_1_discovery/step_2_deprecated_step/
→ .archived/step_2_deprecated_step_{timestamp}/  # Optional archive

orchestrator_discovery.py:
  # Remove import and call for deprecated_step

control_flows.yml:
  # Remove step entry
  # Renumber subsequent steps
```

**Migration Code**:
```python
Operation.delete_step(
    phase_id="discovery",
    step_id="deprecated_step",
    archive=True,  # Don't delete, just archive
    reason="Replaced by new validation logic"
)
```

### 5. Reorder Phases

**What It Does**:
- Renumbers phase directories
- Updates control_flows.yml sequence numbers
- Updates imports if needed

**Files Changed**:
```
phases/phase_1_discovery/ → phases/phase_1_discovery/ (stays)
phases/phase_2_validation/ → phases/phase_3_validation/ (was 2, now 3)
phases/phase_3_collection/ → phases/phase_2_collection/ (was 3, now 2)

control_flows.yml:
  phases[]:
    - sequence numbers updated to match new order
```

**Migration Code**:
```python
Operation.reorder_phases(
    new_order=["discovery", "collection", "validation", "generation"]
    # Old: discovery(1), validation(2), collection(3), generation(4)
    # New: discovery(1), collection(2), validation(3), generation(4)
)
```

### 6. Reorder Steps

**What It Does**:
- Renumbers step directories within a phase
- Updates orchestrator call order
- Updates control_flows.yml

**Files Changed**:
```
phases/phase_1_discovery/step_0_env/ → step_1_env/ (was 0, now 1)
phases/phase_1_discovery/step_1_sys/ → step_0_sys/ (was 1, now 0)

orchestrator_discovery.py:
  # Reorder step calls to match new sequence

control_flows.yml:
  steps[]:
    - sequence numbers updated
```

**Migration Code**:
```python
Operation.reorder_steps(
    phase_id="discovery",
    new_order=["system_discovery", "env_discovery", "defaults_generation"]
)
```

---

## Migration Generator Design

### Auto-Generate from Changes

```python
from control_flow_engine.migration import MigrationGenerator

# Detect changes between two states
generator = MigrationGenerator(
    old_spec="control_flows_v1.yml",
    new_spec="control_flows_v2.yml"
)

# Analyze differences
changes = generator.detect_changes()
# Returns:
# {
#   'renamed_phases': [{'old': 'discovery', 'new': 'system_detection'}],
#   'renamed_steps': [{'phase': 'discovery', 'old': 'env_discovery', 'new': 'environment_check'}],
#   'moved_steps': [{'step': 'system_discovery', 'from': 'discovery', 'to': 'monitoring'}],
#   'deleted_steps': [{'phase': 'discovery', 'step': 'deprecated_step'}],
#   'new_steps': [{'phase': 'validation', 'step': 'schema_check'}],
#   'reordered_phases': {'old': [1,2,3,4], 'new': [1,3,2,4]}
# }

# Generate migration file
migration_file = generator.generate_migration(
    id="002_restructure_discovery",
    description="Restructure discovery phase based on new requirements"
)

# migration_file is a Python file containing all operations
print(migration_file)
```

### Migration File Structure

```python
# migrations/migration_002_restructure_discovery.py
"""
AUTO-GENERATED MIGRATION
Generated: 2025-10-14 15:30:00
From: control_flows_v1.yml
To: control_flows_v2.yml

Summary:
- 1 phase renamed
- 2 steps renamed
- 1 step moved
- 1 step deleted
- 1 new step added
- Phases reordered
"""

from control_flow_engine.migration import Migration, Operation
from datetime import datetime

class Migration002(Migration):
    id = "002_restructure_discovery"
    timestamp = datetime(2025, 10, 14, 15, 30, 0)
    description = "Restructure discovery phase"
    
    # Dependencies (must run after these migrations)
    depends_on = ["001_initial_setup"]
    
    operations = [
        # Generated from detected changes
        Operation.rename_phase(
            old_id="discovery",
            new_id="system_detection",
            # ... full details
        ),
        # ... more operations
    ]
    
    def validate(self):
        """Pre-flight checks."""
        # Check files exist
        # Verify no conflicts
        # Validate naming
        pass
    
    def upgrade(self):
        """Apply migration."""
        self.execute_operations()
    
    def downgrade(self):
        """Rollback migration."""
        self.reverse_operations()
```

---

## Best Practices Summary

### DO's ✅

1. **File Paths**:
   - Use pattern: `phase_{seq}_{id}/step_{seq}_{id}/{id}.py`
   - Include both sequence (for order) and ID (for identity)
   - Make IDs descriptive but stable

2. **Variable Naming**:
   - Use IDs in code, not display names
   - Store IDs as constants
   - Use dictionaries with ID keys

3. **Imports**:
   - Import from project root
   - Use absolute imports
   - Generate imports programmatically when possible

4. **YAML Spec**:
   - Separate ID (stable) from name (can change)
   - Include sequence numbers
   - Store implementation paths

5. **Migration**:
   - Generate migration files automatically
   - Include validation and rollback
   - Archive deleted files, don't delete
   - Test in dry-run mode first

### DON'Ts ❌

1. **File Paths**:
   - Don't hardcode paths
   - Don't use display names in paths
   - Don't abbreviate (use `discovery` not `disc`)
   - Don't skip sequence numbers

2. **Variable Naming**:
   - Don't use display names as keys
   - Don't hardcode file paths
   - Don't use relative paths

3. **Imports**:
   - Don't use relative imports with path manipulation
   - Don't insert paths with `sys.path.insert()`
   - Don't mix import styles

4. **Migration**:
   - Don't delete files (archive instead)
   - Don't skip validation
   - Don't commit without testing
   - Don't manually edit multiple files

---

## Example: Complete Migration Workflow

### Scenario: Restructure Discovery Phase

**Current State** (control_flows_v1.yml):
```yaml
phases:
- phase_id: discovery
  sequence: 1
  steps:
  - step_id: env_discovery
    sequence: 0
  - step_id: system_discovery
    sequence: 1
  - step_id: deprecated_check
    sequence: 2
```

**Desired State** (control_flows_v2.yml):
```yaml
phases:
- phase_id: system_detection
  sequence: 1
  steps:
  - step_id: environment_check
    sequence: 0
  # system_discovery moved to monitoring phase
  # deprecated_check deleted
```

### Step 1: Generate Migration

```bash
$ python -m control_flow_engine.migration generate \
    --from control_flows_v1.yml \
    --to control_flows_v2.yml \
    --output migrations/migration_002.py

✅ Detected changes:
   - Rename phase: discovery → system_detection
   - Rename step: env_discovery → environment_check
   - Move step: system_discovery (discovery → monitoring)
   - Delete step: deprecated_check
   
📝 Generated: migrations/migration_002.py
```

### Step 2: Review Migration

```bash
$ python -m control_flow_engine.migration show migrations/migration_002.py

Migration 002: Restructure discovery phase
===========================================

Operations:
1. RENAME PHASE
   From: discovery
   To:   system_detection
   Files: 15 files will be updated
   
2. RENAME STEP
   Phase: system_detection
   From: env_discovery
   To:   environment_check
   Files: 8 files will be updated
   
3. MOVE STEP
   Step: system_discovery
   From: system_detection (seq 1)
   To:   monitoring (seq 0)
   Files: 5 files will be updated
   
4. DELETE STEP
   Phase: system_detection
   Step: deprecated_check
   Action: Archive to .archived/
```

### Step 3: Dry Run

```bash
$ python -m control_flow_engine.migration apply migrations/migration_002.py --dry-run

🔍 DRY RUN MODE - No changes will be made
=============================================

VALIDATION:
✅ All source files exist
✅ No naming conflicts
✅ No circular dependencies
✅ All imports are valid

CHANGES:
📁 Directory renames: 2
📝 File renames: 12
🔄 Import updates: 18
📋 YAML updates: 1

FILES TO CHANGE:
  phases/phase_1_discovery/ → phases/phase_1_system_detection/
  phases/phase_1_discovery/orchestrator_discovery.py → orchestrator_system_detection.py
  phases/phase_1_discovery/step_0_env_discovery/ → step_0_environment_check/
  ... (15 more)

✅ Dry run successful - safe to apply
```

### Step 4: Apply Migration

```bash
$ python -m control_flow_engine.migration apply migrations/migration_002.py

🚀 Applying migration 002...
============================

[1/6] Validation... ✅
[2/6] Creating backup... ✅
[3/6] Renaming directories... ✅
[4/6] Updating imports... ✅
[5/6] Updating YAML... ✅
[6/6] Verification... ✅

✨ Migration completed successfully!

Changed files: 15
Git status: uncommitted changes
Next: Review changes and commit

📊 Migration Report: migration_002_report.json
```

### Step 5: Verify and Commit

```bash
$ git status
# Shows all renamed/modified files

$ git diff control_flows.yml
# Review YAML changes

$ python test_control_flow.py
# Run tests to verify everything works

$ git add -A
$ git commit -m "Apply migration 002: Restructure discovery phase"
```

### Step 6: Rollback (If Needed)

```bash
$ python -m control_flow_engine.migration rollback migrations/migration_002.py

⏮️  Rolling back migration 002...
===================================

[1/4] Loading backup... ✅
[2/4] Reversing operations... ✅
[3/4] Restoring files... ✅
[4/4] Verification... ✅

✅ Rollback completed successfully!
```

---

## Implementation Checklist

### Phase 1: Migration Foundation ✅
- [x] File path conventions documented
- [x] Variable naming best practices documented
- [x] Migration file format designed

### Phase 2: Migration Operations (NEW)
- [ ] Implement Operation.rename_phase()
- [ ] Implement Operation.rename_step()
- [ ] Implement Operation.move_step()
- [ ] Implement Operation.delete_step()
- [ ] Implement Operation.reorder_phases()
- [ ] Implement Operation.reorder_steps()

### Phase 3: Migration Generator (NEW)
- [ ] Implement MigrationGenerator.detect_changes()
- [ ] Implement MigrationGenerator.generate_migration()
- [ ] Add validation logic
- [ ] Add dry-run mode

### Phase 4: Migration Executor (NEW)
- [ ] Implement backup/restore
- [ ] Implement file operations
- [ ] Implement import updates
- [ ] Implement YAML updates
- [ ] Add verification
- [ ] Add rollback

### Phase 5: CLI Interface (NEW)
- [ ] `migration generate` command
- [ ] `migration show` command
- [ ] `migration apply` command
- [ ] `migration rollback` command
- [ ] `migration list` command

**Estimated Effort**: 20-24 hours for complete migration system

---

## Conclusion

Migration-friendly design requires:

1. **Consistent Patterns**: Predictable file paths and naming
2. **Stable Identifiers**: IDs that don't change when renaming
3. **Automated Tools**: Generate migrations, don't write manually
4. **Safety Mechanisms**: Validation, dry-run, backup, rollback
5. **Complete Tracking**: Know exactly what changed and why

With this system, restructuring flows becomes safe, automated, and reversible.

---

**Status**: 📋 DESIGN COMPLETE  
**Next**: Implement Phase 2 (Migration Operations)
