# Control Flow Engine: Two Distinct Use Cases

## 🎯 Overview

The Control Flow Engine serves two fundamentally different use cases with different requirements and workflows:

1. **Greenfield**: Generating control flow YAML for a new project (design-first)
2. **Brownfield**: Discovering and documenting existing code structure (code-first)

---

## Use Case 1: Greenfield - Design-First Approach

### Scenario
Starting a new project or adding a new component. No code exists yet.

### Goal
Create a control flow specification that will guide implementation.

### Workflow

```
📝 Define Specification → 🏗️ Generate Scaffolding → 💻 Implement Code → ✅ Validate
```

#### Step 1: Create Initial Specification
```yaml
# control_flows.yml - Initial design
flows:
  main_config_flow:
    description: Primary Configuration Process
    phases:
    - phase_id: discovery
      name: Discovery Phase
      status: PLANNED
      description: Discover system environment
      steps: []  # Empty - will be added progressively
```

#### Step 2: Add Steps Progressively
```python
# Designer's workflow
from control_flow_engine.designer import ControlFlowDesigner

designer = ControlFlowDesigner.new_project("config-manager")

# Add first step
designer.add_step(
    phase_id="discovery",
    step=StepInsertion(
        step_id="env_discovery",
        name="Environment Discovery",
        description="Detect runtime environment",
        status=ImplementationStatus.PLANNED,
        step_type="processing"
    ),
    create_scaffolding=True  # Generate directories/files
)

# Result:
# ✅ YAML updated with step definition
# ✅ Directory created: phases/phase_1_discovery/step_0_env_discovery/
# ✅ Files generated: __init__.py, env_discovery.py, README.md
# ✅ Ready to implement
```

#### Step 3: Implement Generated Scaffolding
```python
# Developer fills in the TODOs in generated file
def execute_env_discovery(context, phase_dir):
    # TODO: Implement step logic  ← Developer adds code here
    
    env_data = detect_environment()
    
    return {
        'step': 'env_discovery',
        'env_data': env_data,
        'status': 'completed'
    }
```

#### Step 4: Mark as Implemented
```python
designer.update_step_status(
    phase_id="discovery",
    step_id="env_discovery",
    status=ImplementationStatus.IMPLEMENTED
)
```

### Characteristics

| Aspect | Greenfield |
|--------|------------|
| **Starting Point** | Empty directory or basic skeleton |
| **Control Flow** | Specification drives code structure |
| **Accuracy** | 100% - spec matches code exactly |
| **Maintenance** | Easy - spec is source of truth |
| **Challenges** | Requires upfront design, may change during development |
| **Best For** | New projects, major refactors, well-understood domains |

### Benefits
- ✅ Clean architecture from the start
- ✅ Consistent naming conventions
- ✅ Complete documentation
- ✅ Clear implementation roadmap
- ✅ No legacy code to reconcile

### Challenges
- ⚠️ Requires significant upfront design
- ⚠️ Design may need adjustment during implementation
- ⚠️ Risk of over-engineering if requirements unclear

---

## Use Case 2: Brownfield - Code-First Approach

### Scenario
Existing codebase with implemented functionality. Need to document and manage control flow.

### Goal
Generate accurate control flow specification from existing code structure.

### Workflow

```
🔍 Analyze Code → 📊 Extract Structure → 📝 Generate Spec → 🔄 Maintain Sync
```

#### Step 1: Analyze Existing Codebase

```python
from control_flow_engine.analyzer import CodebaseAnalyzer

analyzer = CodebaseAnalyzer(project_root="/opt/openproject/external/config-manager")

# Scan for existing structure
discovered = analyzer.discover_control_flow(
    entry_points=["run_phases.py"],
    phase_dirs=["phases/"]
)

# Result:
# {
#   'phases': [
#     {
#       'phase_id': 'discovery',
#       'directory': 'phases/phase_1_discovery',
#       'orchestrator': 'orchestrator_discovery.py',
#       'class': 'DiscoveryPhase',
#       'steps': [
#         {'step_id': 'env_discovery', 'file': 'step_1_env_discovery/environment.py'},
#         {'step_id': 'system_discovery', 'file': 'step_2_system_discovery/system.py'},
#       ]
#     }
#   ]
# }
```

#### Step 2: Extract Detailed Metadata

```python
# Analyze each step to extract metadata
for phase in discovered['phases']:
    for step in phase['steps']:
        metadata = analyzer.extract_step_metadata(step['file'])
        # Extracts:
        # - Function/class names
        # - Docstrings → descriptions
        # - Parameters → artifacts consumed
        # - Return values → artifacts produced
        # - Dependencies (imports)
        # - TODO/FIXME markers → status hints
```

#### Step 3: Generate Control Flow Specification

```python
generator = ControlFlowGenerator(discovered_structure=discovered)

# Generate YAML from discovered code
spec = generator.generate_specification(
    include_implementation_details=True,  # Add file paths, class names
    infer_status=True,                     # Mark as IMPLEMENTED if code exists
    extract_docstrings=True,               # Use docstrings for descriptions
    analyze_data_flow=True                 # Trace variable usage
)

# Save to file
spec.save_to_file("control_flows_generated.yml")
```

#### Step 4: Maintain Synchronization

```python
# Detect drift between code and spec
drift_detector = DriftDetector(
    spec_file="control_flows.yml",
    code_root="/opt/openproject/external/config-manager"
)

drift = drift_detector.check()

# Example drift report:
# {
#   'missing_in_spec': [
#     {
#       'type': 'step',
#       'location': 'phases/phase_1_discovery/step_4_new_feature/',
#       'suggestion': 'Add to discovery phase steps'
#     }
#   ],
#   'missing_in_code': [
#     {
#       'type': 'step',
#       'step_id': 'old_deprecated_step',
#       'spec_location': 'flows.main_config_flow.phases[0].steps[3]',
#       'suggestion': 'Remove from spec or implement'
#     }
#   ],
#   'metadata_mismatch': [
#     {
#       'step_id': 'env_discovery',
#       'field': 'description',
#       'spec_value': 'Old description',
#       'code_value': 'Updated description from docstring',
#       'suggestion': 'Update spec with code docstring'
#     }
#   ]
# }
```

### Characteristics

| Aspect | Brownfield |
|--------|------------|
| **Starting Point** | Existing codebase with implemented features |
| **Control Flow** | Code structure drives specification |
| **Accuracy** | Initial: 80-95% - needs human review/correction |
| **Maintenance** | Complex - need drift detection |
| **Challenges** | Code may not follow patterns, inconsistent naming |
| **Best For** | Legacy projects, documentation generation, migration |

### Benefits
- ✅ Quickly document existing systems
- ✅ No disruption to working code
- ✅ Identify inconsistencies and technical debt
- ✅ Gradual migration to structured approach
- ✅ Reverse-engineer undocumented systems

### Challenges
- ⚠️ Code may not follow clean patterns
- ⚠️ Difficult to infer intent from implementation
- ⚠️ May discover accidental complexity
- ⚠️ Keeping spec and code in sync
- ⚠️ Handling legacy naming conventions

---

## Comparison Matrix

| Feature | Greenfield (Design-First) | Brownfield (Code-First) |
|---------|---------------------------|--------------------------|
| **Starting Artifact** | control_flows.yml specification | Existing code files |
| **Primary Tool** | `ControlFlowDesigner` | `CodebaseAnalyzer` |
| **Scaffolding** | Generate from spec | Optional - refactor existing |
| **Accuracy** | 100% (spec is truth) | 80-95% (needs review) |
| **Workflow** | Design → Scaffold → Implement | Analyze → Extract → Document |
| **Status Tracking** | PLANNED → IN_PROGRESS → IMPLEMENTED | Auto-detect from code presence |
| **Naming** | Consistent from start | May need normalization |
| **Documentation** | Generated templates | Extract from docstrings |
| **Data Flow** | Declared in spec | Inferred from code |
| **Validation** | Check code matches spec | Check spec matches code |
| **Iteration** | Update spec, regenerate scaffolding | Update code, sync spec |
| **Best For** | New components, rewrites | Documentation, migration, audits |

---

## Hybrid Approach: Best of Both Worlds

### Scenario
Partially implemented project. Some phases exist, need to add new ones.

### Workflow

```
🔍 Discover Existing → 📝 Extend Spec → 🏗️ Generate New → 🔄 Maintain All
```

#### Step 1: Import Existing Structure
```python
# Start with what exists
analyzer = CodebaseAnalyzer(project_root=".")
existing = analyzer.discover_control_flow()

# Convert to specification
spec = ControlFlowGenerator(existing).generate_specification()
spec.save_to_file("control_flows.yml")
```

#### Step 2: Add New Phases/Steps (Design-First)
```python
designer = ControlFlowDesigner.from_existing("control_flows.yml")

# Add new planned phase
designer.add_phase(
    PhaseInsertion(
        phase_id="validation",
        name="Validation Phase",
        status=ImplementationStatus.PLANNED,
        create_scaffolding=True
    )
)

# Add step to new phase
designer.add_step(
    phase_id="validation",
    step=StepInsertion(
        step_id="schema_validation",
        status=ImplementationStatus.PLANNED,
        ...
    ),
    create_scaffolding=True
)
```

#### Step 3: Periodic Sync Checks
```python
# Weekly CI check
drift = DriftDetector("control_flows.yml", ".").check()

if drift.has_issues():
    print(drift.report())
    # Option to auto-fix certain issues
    drift.auto_fix(safe_fixes_only=True)
```

---

## Implementation Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Save YAML specifications
- [x] Navigate phases structure  
- [x] Insert steps into phases
- [x] Generate scaffolding
- [x] TUI form templates

### Phase 2: Greenfield Support (P0)
**Goal**: Complete design-first workflow

#### 2.1 Designer API
```python
class ControlFlowDesigner:
    @classmethod
    def new_project(cls, project_name: str) -> 'ControlFlowDesigner':
        """Create new project with minimal spec."""
    
    @classmethod
    def from_existing(cls, spec_file: Path) -> 'ControlFlowDesigner':
        """Load existing specification."""
    
    def add_phase(self, phase: PhaseInsertion, create_scaffolding: bool = True) -> bool:
        """Add new phase to flow."""
    
    def add_step(self, phase_id: str, step: StepInsertion, create_scaffolding: bool = True) -> bool:
        """Add step to phase."""
    
    def update_step_status(self, phase_id: str, step_id: str, status: ImplementationStatus) -> bool:
        """Mark step as IMPLEMENTED, IN_PROGRESS, etc."""
    
    def validate(self) -> ValidationReport:
        """Check spec for completeness, consistency."""
```

#### 2.2 Phase Scaffolding
```python
class ScaffoldGenerator:
    def create_phase_scaffolding(self, phase: PhaseInsertion, base_path: Path) -> Dict[str, Path]:
        """
        Create complete phase directory structure:
        - phase_N_phaseid/
          - __init__.py
          - orchestrator_phaseid.py (with execute method)
          - outputs/
          - README.md
        """
```

#### 2.3 Orchestrator Auto-Update
```python
class OrchestratorUpdater:
    def integrate_step(self, orchestrator_file: Path, step: StepInsertion) -> bool:
        """
        Add step to orchestrator:
        - Import statement
        - Call in execute() method
        - Error handling
        - Logging
        """
    
    def update_phase_metadata(self, orchestrator_file: Path, phase: PhaseInsertion) -> bool:
        """Update orchestrator class docstring, return types, etc."""
```

**Estimated Effort**: 8-10 hours

### Phase 3: Brownfield Support (P1)
**Goal**: Code discovery and specification generation

#### 3.1 Codebase Analyzer
```python
class CodebaseAnalyzer:
    def __init__(self, project_root: Path):
        """Initialize analyzer with project root."""
    
    def discover_control_flow(
        self,
        entry_points: List[str] = None,
        phase_dirs: List[str] = None,
        pattern: str = "phase_*"
    ) -> Dict[str, Any]:
        """
        Scan codebase and discover:
        - Entry points (main scripts, CLI commands)
        - Phase directories and orchestrators
        - Step directories and implementations
        - Dependencies between components
        """
    
    def extract_step_metadata(self, step_file: Path) -> StepMetadata:
        """
        Extract metadata from step implementation:
        - Function/class name
        - Docstring → description
        - Type hints → artifacts
        - Imports → dependencies
        - Comments → status hints (TODO, FIXME, etc.)
        """
    
    def analyze_data_flow(self, phase_dir: Path) -> DataFlowGraph:
        """
        Trace data flow through phase:
        - Variables passed between steps
        - File I/O
        - External service calls
        """
    
    def detect_patterns(self) -> List[Pattern]:
        """
        Identify architectural patterns:
        - Orchestrator pattern
        - Step/command pattern
        - TUI form usage
        - Configuration files
        """
```

#### 3.2 Metadata Extraction (AST-based)
```python
import ast

class StepMetadataExtractor:
    def extract_from_file(self, file_path: Path) -> StepMetadata:
        """
        Use Python AST to extract:
        - Function definitions
        - Docstrings
        - Type annotations
        - Return statements
        - Imports
        - Decorators
        """
    
    def infer_step_type(self, metadata: StepMetadata) -> str:
        """
        Infer step type from code analysis:
        - Has FormRenderer → 'interactive'
        - Has file I/O → 'io'
        - Has validation logic → 'validation'
        - Default → 'processing'
        """
    
    def extract_dependencies(self, metadata: StepMetadata) -> List[str]:
        """Extract from import statements and function calls."""
    
    def infer_status(self, metadata: StepMetadata) -> ImplementationStatus:
        """
        Infer status from code markers:
        - Has 'TODO' or 'FIXME' → PLANNED or IN_PROGRESS
        - Has 'NotImplementedError' → PLANNED
        - Has tests → IMPLEMENTED
        - Default → IMPLEMENTED (code exists)
        """
```

#### 3.3 Specification Generator
```python
class ControlFlowGenerator:
    def __init__(self, discovered_structure: Dict[str, Any]):
        """Initialize with discovered code structure."""
    
    def generate_specification(
        self,
        include_implementation_details: bool = True,
        infer_status: bool = True,
        extract_docstrings: bool = True,
        analyze_data_flow: bool = False
    ) -> ControlFlowSpecification:
        """
        Generate control_flows.yml from discovered structure.
        """
    
    def generate_flow(self, flow_data: Dict) -> Dict[str, Any]:
        """Generate flow section of spec."""
    
    def generate_phase(self, phase_data: Dict) -> Dict[str, Any]:
        """Generate phase with implementation details."""
    
    def generate_step(self, step_data: Dict, metadata: StepMetadata) -> Dict[str, Any]:
        """Generate step with extracted metadata."""
```

#### 3.4 Drift Detection
```python
class DriftDetector:
    def __init__(self, spec_file: Path, code_root: Path):
        """Initialize with spec and code root."""
    
    def check(self) -> DriftReport:
        """
        Detect discrepancies:
        - Steps in spec but not in code
        - Steps in code but not in spec
        - Metadata mismatches (name, description, etc.)
        - Structure changes (file moves, renames)
        """
    
    def auto_fix(self, safe_fixes_only: bool = True) -> FixReport:
        """
        Automatically fix certain issues:
        - Update descriptions from docstrings (safe)
        - Add missing steps to spec (safe)
        - Remove deprecated steps (requires confirmation)
        """
```

**Estimated Effort**: 16-20 hours

### Phase 4: Maintenance & Advanced Features (P2)
- Rename operations with reference updates
- Reorder operations with renumbering
- Template library for common patterns
- Version control integration (track changes)
- Diff viewer (spec vs code)

**Estimated Effort**: 12-15 hours

---

## Recommended Implementation Order

### Sprint 1: Complete Greenfield (Phase 2)
**Justification**: Builds on completed Phase 1, provides immediate value

1. Designer API (3 hours)
2. Phase scaffolding (3 hours)
3. Orchestrator auto-update (4 hours)
4. Testing & docs (2 hours)

**Deliverable**: Complete design-first workflow

### Sprint 2: Basic Brownfield (Phase 3.1 + 3.2)
**Justification**: Enables documentation of existing code

1. Codebase analyzer structure (4 hours)
2. AST-based metadata extraction (6 hours)
3. Basic pattern detection (3 hours)
4. Testing & docs (3 hours)

**Deliverable**: Can discover and extract from existing code

### Sprint 3: Specification Generation (Phase 3.3)
**Justification**: Complete the brownfield workflow

1. Specification generator (6 hours)
2. YAML formatting and structure (3 hours)
3. Testing with real codebases (3 hours)
4. Docs and examples (2 hours)

**Deliverable**: Can generate control_flows.yml from code

### Sprint 4: Drift Detection & Sync (Phase 3.4)
**Justification**: Enable maintenance of hybrid projects

1. Drift detector (5 hours)
2. Auto-fix capabilities (4 hours)
3. CI integration (2 hours)
4. Reporting and visualization (3 hours)

**Deliverable**: Keep spec and code in sync

---

## Decision Matrix: Which Approach to Use?

### Use Greenfield When:
- ✅ Starting new component/project
- ✅ Major refactor where you can restructure
- ✅ Requirements are well understood
- ✅ Team agrees on architecture
- ✅ Want consistent patterns from start

### Use Brownfield When:
- ✅ Documenting existing system
- ✅ Inherited codebase with no docs
- ✅ Migration/modernization project
- ✅ Compliance requires documentation
- ✅ Want to identify technical debt

### Use Hybrid When:
- ✅ Partially implemented project
- ✅ Gradual migration to structured approach
- ✅ Different modules at different maturity
- ✅ Some legacy + some new code

---

## Example: Real-World Scenario

### Scenario: config-manager Project

**Current State**:
- ✅ Phase 1 (Discovery) - IMPLEMENTED
- ✅ Phase 2 (TUI Mapping) - IMPLEMENTED  
- ✅ Phase 3 (Collection) - IMPLEMENTED
- ⚠️ Phase 4 (Validation) - PLANNED
- ⚠️ Phase 5 (Generation) - PLANNED

**Recommended Approach**: **Hybrid**

#### Step 1: Document Existing (Brownfield)
```python
# Generate spec for phases 1-3
analyzer = CodebaseAnalyzer("/opt/openproject/external/config-manager")
existing = analyzer.discover_control_flow(phase_dirs=["phases/phase_1*", "phases/phase_2*", "phases/phase_3*"])
spec = ControlFlowGenerator(existing).generate_specification()
```

#### Step 2: Add New Phases (Greenfield)
```python
# Add phases 4-5 using design-first
designer = ControlFlowDesigner.from_existing("control_flows.yml")

designer.add_phase(
    PhaseInsertion(
        phase_id="validation",
        name="Validation Phase",
        sequence=4,
        status=ImplementationStatus.PLANNED,
        create_scaffolding=True
    )
)
```

#### Step 3: Maintain Sync
```python
# Regular drift checks
drift = DriftDetector("control_flows.yml", ".").check()
drift.report_to_file("drift_report.md")
```

---

## Conclusion

Both use cases are valid and valuable:

1. **Greenfield** enables clean, structured development with guardrails
2. **Brownfield** enables documentation and modernization of legacy code
3. **Hybrid** provides flexibility for real-world projects

**Recommendation**: Implement both, starting with Greenfield (Sprint 1) since Phase 1 foundation is already complete, then add Brownfield capabilities (Sprints 2-3) for broader applicability.

---

**Status**: 📋 ANALYSIS COMPLETE  
**Next Action**: Approve implementation order and proceed with Sprint 1
