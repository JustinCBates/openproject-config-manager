# Config Manager - Phases Directory

This directory contains the phase-based architecture for the OpenProject configuration management system.

## Structure

```
phases/
├── phases_orchestrator.py          # Main orchestrator coordinating all 5 phases
├── tests/                           # Tests for the orchestrator
│   ├── integration/                 # Integration tests
│   │   └── test_phases_orchestrator.py
│   └── unit/                        # Unit tests
├── outputs/                         # Shared outputs across phases
├── phase_1_discovery/               # Phase 1: System discovery and defaults generation
│   ├── orchestrator_discovery.py
│   ├── step_1_env_discovery/
│   ├── step_2_system_discovery/
│   ├── step_3_defaults_generation/
│   ├── outputs/
│   └── tests/
├── phase_2_tui_mapping/             # Phase 2: Transform defaults for TUI
│   ├── orchestrator_tui_mapping.py
│   ├── step_1_transform_defaults/
│   ├── outputs/
│   └── tests/
├── phase_3_collection/              # Phase 3: Interactive configuration collection
│   ├── orchestrator_collection.py
│   ├── step_1_collect_user_configuration/
│   ├── outputs/
│   └── tests/
├── phase_4_validation/              # Phase 4: Configuration validation
│   ├── orchestrator_validation.py
│   ├── step_1_schema_validation/
│   ├── step_2_dependency_validation/
│   ├── step_3_environment_validation/
│   ├── outputs/
│   └── tests/
└── phase_5_export/                  # Phase 5: Export final configuration
    ├── orchestrator_export.py
    ├── outputs/
    └── tests/
```

## Phases Overview

### Phase 1: Discovery ✅ MIGRATED
**Status**: Fully implemented and tested

Discovers the system environment and generates intelligent defaults with confidence scoring.

- **Step 1**: Environment Discovery - Probes environment variables
- **Step 2**: System Discovery - Collects system, Docker, and network information
- **Step 3**: Defaults Generation - Generates intelligent defaults with reasoning

**Outputs**: `enhanced_defaults.yml` with metadata and confidence-scored defaults

### Phase 2: TUI Mapping ✅ MIGRATED
**Status**: Fully implemented and tested

Transforms rich enhanced defaults to simple TUI-consumable format.

- **Step 1**: Transform Defaults - Flattens defaults and applies field mappings

**Outputs**: `tui_defaults.yml` with flattened structure

### Phase 3: Collection ⏸️ PENDING
**Status**: Scaffolded, awaiting migration

Collects user configuration through interactive terminal UI.

- **Step 1**: Collect User Configuration - TUI-based interactive collection

**Outputs**: `collected_configuration.yml`

### Phase 4: Validation ⏸️ PENDING
**Status**: Scaffolded, awaiting migration

Validates the collected configuration for integrity and correctness.

- **Step 1**: Schema Validation - Validates against schema definitions
- **Step 2**: Dependency Validation - Checks service dependencies
- **Step 3**: Environment Validation - Validates environment compatibility

**Outputs**: `validation_results.yml`

### Phase 5: Export ⏸️ PENDING
**Status**: Scaffolded, basic implementation

Exports final configuration to various formats for deployment.

**Outputs**: 
- `phases/outputs/docker-compose.yml` - Docker Compose configuration
- `phases/outputs/.env` - Environment variables
- `phases/outputs/configuration_manifest.yml` - Metadata for deploy-manager

**Note**: Phase 5 outputs to the top-level `phases/outputs/` directory, which is where
the deploy-manager component will look for configuration files.

## Using the Phases Orchestrator

### Execute All Phases (when all are migrated)

```python
from pathlib import Path
from phases.phases_orchestrator import create_orchestrator

orchestrator = create_orchestrator(Path.cwd())
result = orchestrator.execute_all_phases()
```

### Execute a Single Phase

```python
orchestrator = create_orchestrator(Path.cwd())
context = {}
result = orchestrator.execute_phase(1, context)  # Execute Phase 1
```

### Execute a Range of Phases

```python
orchestrator = create_orchestrator(Path.cwd())
result = orchestrator.execute_phases_range(1, 2)  # Execute Phases 1-2
```

## Testing

### Run All Orchestrator Tests

```bash
python3 phases/tests/integration/test_phases_orchestrator.py
```

### Run Phase-Specific Tests

```bash
# Phase 1
python3 phases/phase_1_discovery/tests/integration/test_orchestrator_discovery.py

# Phase 2
python3 phases/phase_2_tui_mapping/tests/integration/test_orchestrator_tui_mapping.py
```

## Migration Progress

| Phase | Status | Steps | Tests | Migration Date |
|-------|--------|-------|-------|----------------|
| Phase 1: Discovery | ✅ Complete | 3/3 | 6/6 passing | 2025-10-13 |
| Phase 2: TUI Mapping | ✅ Complete | 1/1 | 6/6 passing | 2025-10-13 |
| Phase 3: Collection | ⏸️ Pending | 0/1 | 6/6 passing (mock) | - |
| Phase 4: Validation | ⏸️ Pending | 0/3 | 6/6 passing (mock) | - |
| Phase 5: Export | ⏸️ Pending | 0/0 | 6/6 passing (mock) | - |

**Overall Progress**: 40% (2/5 phases complete)

## Architecture Principles

1. **Phase Independence**: Each phase is self-contained with its own orchestrator
2. **Context Passing**: Data flows between phases via context dictionary
3. **Artifact-Based**: Each phase consumes artifacts from previous phases and produces new ones
4. **Testable**: Each phase and step has comprehensive unit and integration tests
5. **Modular**: Business logic separated into dedicated modules within step directories

## Data Flow

```
┌─────────────────┐
│  Phase 1:       │
│  Discovery      │──→ phases/phase_1_discovery/outputs/discovery/enhanced_defaults.yml
└─────────────────┘
         ↓
┌─────────────────┐
│  Phase 2:       │
│  TUI Mapping    │──→ phases/phase_2_tui_mapping/outputs/tui/tui_defaults.yml
└─────────────────┘
         ↓
┌─────────────────┐
│  Phase 3:       │
│  Collection     │──→ phases/phase_3_collection/outputs/collected_configuration.yml
└─────────────────┘
         ↓
┌─────────────────┐
│  Phase 4:       │
│  Validation     │──→ phases/phase_4_validation/outputs/validation_results.yml
└─────────────────┘
         ↓
┌─────────────────┐
│  Phase 5:       │
│  Export         │──→ phases/outputs/ (for deploy-manager)
└─────────────────┘    ├── docker-compose.yml
                        ├── .env
                        └── configuration_manifest.yml
```

**Note**: Phase 5 outputs to the top-level `phases/outputs/` directory. This is where
the deploy-manager component will look for the final configuration files.

## Development Guidelines

### Adding New Steps to a Phase

1. Create step directory: `step_N_<step_name>/`
2. Add step implementation: `<step_name>.py` with `execute_<step_name>(context, phase_dir)` function
3. Create supporting modules as needed in the step directory
4. Update phase orchestrator to call the new step
5. Add unit tests: `tests/unit/test_<step_name>.py`
6. Update integration tests: `tests/integration/test_orchestrator_<phase_name>.py`

### Migrating Code to Phases

1. Identify source code in `src/openproject_config_manager/`
2. Determine target phase and step based on functionality
3. Extract code into step module (e.g., `<step_name>/<module>.py`)
4. Update step entry point to use the module
5. Update phase orchestrator if needed
6. Run tests to validate migration
7. Update `MIGRATION_STATUS.md`

## See Also

- `CODE_MIGRATION_MAP.md` - Detailed mapping of source code to phases
- `MIGRATION_STATUS.md` - Current migration status and progress
- `control_flows.yml` - Original flow specifications
