# Config-Manager Implementation Reference

**Version:** 2.0  
**Last Updated:** October 14, 2025  
**Purpose:** Complete implementation reference for the openproject-config-manager system - use this document to recover full understanding of the current implementation, structure, and patterns.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Phase Implementations](#phase-implementations)
4. [Libraries & Units](#libraries--units)
5. [File Locations](#file-locations)
6. [Data Flow](#data-flow)
7. [Current Status](#current-status)
8. [Development Guide](#development-guide)

---

## System Overview

### What is Config-Manager?

**openproject-config-manager** is a YAML-driven interactive configuration system for Docker Compose projects. It uses the control-flow engine to orchestrate a 5-phase workflow:

1. **Discovery** - Auto-detect system environment
2. **TUI Mapping** - Transform rich data to TUI format
3. **Collection** - Interactive user configuration
4. **Validation** - Validate configuration completeness
5. **Export** - Generate deployment files

### Design Philosophy

- **Auto-discovery first** - Reduce manual configuration
- **Interactive when needed** - Beautiful TUI for user input
- **Validation before export** - Catch errors early
- **YAML-driven workflow** - Control flow defined in YAML
- **Reusable units** - Shared components in libraries

### Key Features

- **System Discovery**: Automatically detects Docker, network, OS, resources
- **Intelligent Defaults**: Generates smart defaults from discovery
- **Interactive TUI**: Rich-based terminal interface
- **Live Validation**: Real-time configuration validation
- **Multiple Formats**: Exports to .env, .cfg, docker-compose.yml
- **Resumable**: Can resume interrupted configuration

---

## Architecture

### Directory Structure

```
config-manager/
├── design_specs/
│   └── control_flows.yml                    # YAML workflow specification
├── phases/
│   ├── libraries/                           # Shared units
│   │   ├── __init__.py
│   │   └── probing/                         # Discovery units
│   │       ├── __init__.py
│   │       ├── docker_detector.py           # DockerDiscovery class
│   │       ├── network_detector.py          # NetworkDiscovery class
│   │       └── system_detector.py           # SystemDiscovery class
│   ├── phases_orchestrator.py               # Global orchestrator
│   ├── phase_1_discovery/
│   │   ├── orchestrator_discovery.py        # Phase orchestrator
│   │   ├── step_0_discovery_prompt/
│   │   ├── step_1_env_discovery/
│   │   │   ├── env_discovery.py
│   │   │   └── environment.py
│   │   ├── step_2_system_discovery/
│   │   │   └── system_discovery.py          # Uses libraries.probing
│   │   ├── step_3_defaults_generation/
│   │   │   ├── defaults_generation.py
│   │   │   └── defaults_generator.py
│   │   └── outputs/
│   │       └── discovery/
│   │           └── enhanced_defaults.yml    # Generated output
│   ├── phase_2_tui_mapping/
│   │   ├── orchestrator_tui_mapping.py
│   │   ├── step_1_transform_defaults/
│   │   │   ├── defaults_transformer.py
│   │   │   └── transform_defaults.py
│   │   └── outputs/
│   │       └── tui/
│   │           └── tui_defaults.yml         # Generated output
│   ├── phase_3_collection/
│   │   ├── orchestrator_collection.py
│   │   ├── step_1_interactive_collection/
│   │   │   └── interactive_collection.py
│   │   └── outputs/
│   │       └── config/
│   │           └── user_configuration.yml   # User input
│   ├── phase_4_validation/
│   │   ├── orchestrator_validation.py
│   │   ├── step_1_schema_validation/
│   │   ├── step_2_dependency_validation/
│   │   ├── step_3_environment_validation/
│   │   └── step_4_transformation_validation/
│   └── phase_5_export/
│       ├── orchestrator_export.py
│       ├── step_1_export_docker_compose/
│       ├── step_2_export_env_file/
│       ├── step_3_export_manifest/
│       └── outputs/
│           └── export/
├── src/
│   └── openproject_config_manager/
│       ├── cli/
│       │   └── main.py                      # CLI entry point
│       ├── core/
│       │   ├── defaults_map.json            # TUI mapping config
│       │   └── configuration.py
│       └── tui/
│           └── form_engine.py               # Interactive UI
└── tests/
    ├── libraries/                           # Library unit tests
    │   └── probing/
    ├── steps/                               # Step tests
    └── integration/                         # Integration tests
```

### Component Map

| Component | Location | Purpose |
|-----------|----------|---------|
| **Global Orchestrator** | `phases/phases_orchestrator.py` | Execute all 5 phases |
| **Phase Orchestrators** | `phases/phase_X_*/orchestrator_*.py` | Execute steps within phase |
| **Step Functions** | `phases/phase_X_*/step_Y_*/step_name.py` | Execute atomic tasks |
| **Units** | `phases/libraries/*/` | Reusable single-responsibility components |
| **YAML Spec** | `design_specs/control_flows.yml` | Workflow definition |
| **CLI** | `src/openproject_config_manager/cli/main.py` | Command-line interface |
| **TUI** | `src/openproject_config_manager/tui/` | Interactive forms |

---

## Phase Implementations

### Phase 1: Discovery

**Purpose:** Auto-detect system environment and generate intelligent defaults

**Status:** ✅ IMPLEMENTED

**Steps:**

1. **discovery_prompt** (PLANNED) - Ask user for discovery preference
2. **env_discovery** (IMPLEMENTED) - Discover environment variables
3. **system_discovery** (IMPLEMENTED) - Discover Docker, network, system resources
4. **defaults_generation** (IMPLEMENTED) - Generate enhanced defaults YAML

**Key Files:**

```
phase_1_discovery/
├── orchestrator_discovery.py               # Orchestrates 4 steps
├── step_1_env_discovery/
│   ├── env_discovery.py                    # Step function
│   └── environment.py                      # EnvironmentDiscovery class
├── step_2_system_discovery/
│   └── system_discovery.py                 # Uses library units
├── step_3_defaults_generation/
│   ├── defaults_generation.py              # Step function
│   └── defaults_generator.py               # DefaultsGenerator class
└── outputs/discovery/
    └── enhanced_defaults.yml               # Rich defaults with metadata
```

**Units Used:**
- `libraries.probing.DockerDiscovery` - Detect Docker installation/status
- `libraries.probing.NetworkDiscovery` - Detect network interfaces/config
- `libraries.probing.SystemDiscovery` - Detect OS/CPU/memory/disk

**Artifacts Produced:**
- `discovery_data` (memory) - Complete discovery results
- `enhanced_defaults_file` (file) - `enhanced_defaults.yml`

**Example Output:**

```yaml
# phases/phase_1_discovery/outputs/discovery/enhanced_defaults.yml
discovery_info:
  timestamp: "2025-10-14T22:00:00"
  hostname: "srv1035368"
  
domains:
  value: "example.com"
  source: "default"
  confidence: "low"
  alternatives: []
  
database:
  postgres_host:
    value: "postgres"
    source: "default"
    confidence: "high"
  postgres_port:
    value: 5432
    source: "default"
    confidence: "high"
```

**Implementation Notes:**

- Step 2 uses Units & Libraries pattern (as of Oct 14, 2025)
- Originally had co-located `docker.py`, `network.py`, `system.py`
- Now uses `from phases.libraries.probing import DockerDiscovery, NetworkDiscovery, SystemDiscovery`
- Units declared in `control_flows.yml` under `system_discovery.units`

---

### Phase 2: TUI Mapping

**Purpose:** Transform rich enhanced defaults to simple TUI-compatible format

**Status:** ✅ IMPLEMENTED

**Steps:**

1. **transform_defaults** (IMPLEMENTED) - Flatten enhanced → TUI defaults

**Key Files:**

```
phase_2_tui_mapping/
├── orchestrator_tui_mapping.py             # Orchestrates transformation
├── step_1_transform_defaults/
│   ├── transform_defaults.py               # Step function
│   └── defaults_transformer.py             # DefaultsTransformer class
└── outputs/tui/
    └── tui_defaults.yml                    # Simple key-value defaults
```

**Artifacts Consumed:**
- `enhanced_defaults_file` - From Phase 1
- `defaults_mapping_config` - `src/openproject_config_manager/core/defaults_map.json`

**Artifacts Produced:**
- `tui_defaults_file` - `tui_defaults.yml`
- `tui_defaults` (memory) - In-memory dict

**Transformation:**

```yaml
# Input (enhanced_defaults.yml)
database:
  postgres_host:
    value: "postgres"
    source: "default"
    confidence: "high"

# Output (tui_defaults.yml)
database:
  postgres_host: "postgres"
```

**Purpose of Transformation:**
- TUI form engine expects simple `key: value` format
- Enhanced format has metadata (`source`, `confidence`, `alternatives`)
- Transformation strips metadata, keeps just values

---

### Phase 3: Collection

**Purpose:** Collect user configuration via interactive TUI

**Status:** ✅ IMPLEMENTED

**Steps:**

1. **interactive_collection** (IMPLEMENTED) - Present TUI forms to user

**Key Files:**

```
phase_3_collection/
├── orchestrator_collection.py              # Orchestrates collection
├── step_1_interactive_collection/
│   └── interactive_collection.py           # Step function using TUI
└── outputs/config/
    └── user_configuration.yml              # User responses
```

**TUI Integration:**

```python
# Uses tui-form-designer system
from openproject_config_manager.tui.form_engine import FormEngine

form_engine = FormEngine()
responses = form_engine.run_interactive_session(
    flow_file="collection_flow.layout.yml",
    defaults=tui_defaults
)
```

**Artifacts Consumed:**
- `tui_defaults_file` - From Phase 2

**Artifacts Produced:**
- `user_configuration` - User input as YAML

---

### Phase 4: Validation

**Purpose:** Validate configuration completeness and correctness

**Status:** ✅ IMPLEMENTED

**Steps:**

1. **schema_validation** (IMPLEMENTED) - Validate against JSON schema
2. **dependency_validation** (IMPLEMENTED) - Check dependencies available
3. **environment_validation** (IMPLEMENTED) - Validate environment setup
4. **transformation_validation** (IMPLEMENTED) - Validate transformations

**Key Files:**

```
phase_4_validation/
├── orchestrator_validation.py              # Orchestrates validation
├── step_1_schema_validation/
│   └── schema_validation.py
├── step_2_dependency_validation/
│   └── dependency_validation.py
├── step_3_environment_validation/
│   └── environment_validation.py
└── step_4_transformation_validation/
    └── transformation_validation.py
```

**Artifacts Consumed:**
- `user_configuration` - From Phase 3
- `enhanced_defaults` - From Phase 1

**Artifacts Produced:**
- `validated_configuration` - Validated config dict
- `validation_report` - Validation results

**Validation Types:**

1. **Schema** - JSON schema validation
2. **Dependencies** - Check Docker, ports, etc.
3. **Environment** - Verify system capabilities
4. **Transformation** - Validate data transformations

---

### Phase 5: Export

**Purpose:** Generate deployment files (.env, docker-compose.yml, manifest)

**Status:** ✅ IMPLEMENTED

**Steps:**

1. **export_docker_compose** (NEEDS RESTRUCTURING) - Generate docker-compose.yml
2. **export_env_file** (NEEDS RESTRUCTURING) - Generate .env file
3. **export_manifest** (NEEDS RESTRUCTURING) - Generate deployment manifest

**Current Structure (Needs Work):**

```
phase_5_export/
├── orchestrator_export.py                  # ❌ Contains all export logic
├── cfg_writer.py                           # Utility module
└── outputs/export/
    ├── docker-compose.yml
    ├── .env
    └── deployment_manifest.yml
```

**Recommended Structure:**

```
phase_5_export/
├── orchestrator_export.py                  # ✅ Orchestrates 3 steps
├── utils/
│   └── cfg_writer.py                       # Shared utility
├── step_1_export_docker_compose/
│   ├── export_docker_compose.py            # Step function
│   └── docker_compose_exporter.py          # Exporter class
├── step_2_export_env_file/
│   ├── export_env_file.py                  # Step function
│   └── env_file_exporter.py                # Exporter class
├── step_3_export_manifest/
│   ├── export_manifest.py                  # Step function
│   └── manifest_exporter.py                # Exporter class
└── outputs/export/
    ├── docker-compose.yml
    ├── .env
    └── deployment_manifest.yml
```

**Implementation Notes:**
- Phase 5 doesn't follow control-flow step pattern yet
- All logic is in `orchestrator_export.py`
- Needs refactoring to extract steps (see ARCHITECTURE_DISCUSSION_OCT14.md)

**Artifacts Consumed:**
- `validated_configuration` - From Phase 4

**Artifacts Produced:**
- `docker_compose_file` - `docker-compose.yml`
- `env_file` - `.env`
- `manifest_file` - `deployment_manifest.yml`

---

## Libraries & Units

### Probing Library

**Location:** `phases/libraries/probing/`

**Purpose:** System and environment discovery units

**Units:**

#### DockerDiscovery

**File:** `docker_detector.py`

**Class:** `DockerDiscovery`

**Method:** `discover() -> Dict[str, Any]`

**Purpose:** Detect Docker installation and status

**Returns:**
```python
{
    'docker_available': bool,
    'docker_info': {...},
    'containers': [...],
    'images': [...],
    'networks': [...],
    'volumes': [...]
}
```

**Used By:**
- `phase_1_discovery/step_2_system_discovery`
- `phase_4_validation/step_3_environment_validation` (potential)

**Size:** 22KB (534 lines)

#### NetworkDiscovery

**File:** `network_detector.py`

**Class:** `NetworkDiscovery`

**Method:** `discover() -> Dict[str, Any]`

**Purpose:** Detect network configuration and interfaces

**Returns:**
```python
{
    'hostname': str,
    'fqdn': str,
    'interfaces': [...],
    'default_gateway': str,
    'dns_servers': [...],
    'docker_networks': [...],
    'available_ports': [...]
}
```

**Used By:**
- `phase_1_discovery/step_2_system_discovery`

**Size:** 34KB (complex network detection)

#### SystemDiscovery

**File:** `system_detector.py`

**Class:** `SystemDiscovery`

**Method:** `discover() -> Dict[str, Any]`

**Purpose:** Detect system information (OS, CPU, memory, disk)

**Returns:**
```python
{
    'os': {...},
    'cpu': {...},
    'memory': {...},
    'disk': {...},
    'python': {...}
}
```

**Used By:**
- `phase_1_discovery/step_2_system_discovery`

**Size:** 19KB (comprehensive system detection)

### Library __init__.py

```python
# phases/libraries/probing/__init__.py
"""
Probing Library - System Discovery Units

This library contains units for discovering various aspects of the system environment.
Units are single-responsibility, reusable components used across multiple steps/phases.
"""

from .docker_detector import DockerDiscovery
from .network_detector import NetworkDiscovery
from .system_detector import SystemDiscovery

__all__ = [
    'DockerDiscovery',
    'NetworkDiscovery',
    'SystemDiscovery',
]
```

### Future Libraries (Not Yet Created)

Based on the control-flow pattern, future libraries could include:

- **validation/** - Validation units (schema_validator, dependency_checker)
- **transformation/** - Transformation units (config_transformer, defaults_mapper)
- **io/** - File I/O units (yaml_handler, json_handler)
- **export/** - Export units (docker_compose_generator, env_generator)

---

## File Locations

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `control_flows.yml` | `design_specs/control_flows.yml` | YAML workflow specification |
| `defaults_map.json` | `src/openproject_config_manager/core/defaults_map.json` | Enhanced → TUI field mapping |
| `pyproject.toml` | Root | Package configuration |

### Generated Outputs

| Artifact | Location | Phase |
|----------|----------|-------|
| `enhanced_defaults.yml` | `phases/phase_1_discovery/outputs/discovery/` | Phase 1 |
| `tui_defaults.yml` | `phases/phase_2_tui_mapping/outputs/tui/` | Phase 2 |
| `user_configuration.yml` | `phases/phase_3_collection/outputs/config/` | Phase 3 |
| `docker-compose.yml` | `phases/phase_5_export/outputs/export/` | Phase 5 |
| `.env` | `phases/phase_5_export/outputs/export/` | Phase 5 |
| `deployment_manifest.yml` | `phases/phase_5_export/outputs/export/` | Phase 5 |

### TUI Layouts

| Layout | Location | Purpose |
|--------|----------|---------|
| `discovery_prompt.layout.yml` | `phases/phase_1_discovery/step_0_discovery_prompt/` | Discovery config prompt |
| `collection_flow.layout.yml` | `phases/phase_3_collection/step_1_interactive_collection/` | Main config collection |

---

## Data Flow

### Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Discovery                                          │
│                                                             │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│ │ Env Discovery│→ │Sys Discovery │→ │   Defaults   │      │
│ └──────────────┘  └──────────────┘  │  Generation  │      │
│                   (Uses Libraries)   └──────────────┘      │
│                                             ↓              │
│                                    enhanced_defaults.yml   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: TUI Mapping                                        │
│                                                             │
│                   ┌──────────────┐                         │
│ enhanced_defaults │  Transform   │ tui_defaults.yml        │
│     .yml      →   │   Defaults   │  →                      │
│                   └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Collection                                         │
│                                                             │
│                   ┌──────────────┐                         │
│ tui_defaults.yml  │ Interactive  │ user_configuration.yml  │
│      →            │ Collection   │  →                      │
│                   └──────────────┘                         │
│                   (Rich TUI)                               │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Validation                                         │
│                                                             │
│ ┌──────────┐  ┌────────────┐  ┌────────────┐             │
│ │  Schema  │→ │Dependency  │→ │Environment │             │
│ │Validation│  │ Validation │  │ Validation │             │
│ └──────────┘  └────────────┘  └────────────┘             │
│                                       ↓                    │
│                          validated_configuration           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Export                                             │
│                                                             │
│        ┌─────────────┐  ┌─────────────┐  ┌──────────┐     │
│        │Docker Compose│ │   .env      │  │ Manifest │     │
│   →    │   Export    │→ │   Export    │→ │  Export  │     │
│        └─────────────┘  └─────────────┘  └──────────┘     │
│              ↓                ↓                ↓           │
│    docker-compose.yml      .env     deployment_manifest.yml│
└─────────────────────────────────────────────────────────────┘
```

### Artifact Dependencies

```yaml
Phase 1 produces:
  - discovery_data (memory)
  - enhanced_defaults_file (file)

Phase 2 consumes:
  - enhanced_defaults_file
  produces:
  - tui_defaults_file
  - tui_defaults (memory)

Phase 3 consumes:
  - tui_defaults_file
  produces:
  - user_configuration

Phase 4 consumes:
  - user_configuration
  - enhanced_defaults (memory)
  produces:
  - validated_configuration
  - validation_report

Phase 5 consumes:
  - validated_configuration
  produces:
  - docker_compose_file
  - env_file
  - manifest_file
```

---

## Current Status

### Implemented ✅

**Phase 1: Discovery**
- ✅ Environment discovery
- ✅ System discovery (using Units & Libraries pattern)
- ✅ Defaults generation
- ✅ Libraries/probing with 3 units (docker, network, system)

**Phase 2: TUI Mapping**
- ✅ Enhanced → TUI transformation
- ✅ Defaults mapping configuration

**Phase 3: Collection**
- ✅ Interactive TUI collection
- ✅ Form engine integration

**Phase 4: Validation**
- ✅ Schema validation
- ✅ Dependency validation
- ✅ Environment validation
- ✅ Transformation validation

**Phase 5: Export**
- ✅ Docker Compose export (in orchestrator)
- ✅ .env file export (in orchestrator)
- ✅ Manifest export (in orchestrator)

**Control Flow Integration**
- ✅ YAML specification (`control_flows.yml`)
- ✅ Global orchestrator (`phases_orchestrator.py`)
- ✅ Phase orchestrators (all 5 phases)
- ✅ Units declared in YAML
- ✅ Libraries directory created
- ✅ Units extracted and imported properly

### Planned / Needs Work ⚠️

**Phase 1:**
- ⚠️ discovery_prompt step (interactive) - Currently PLANNED

**Phase 5:**
- ⚠️ Refactor to proper step structure (currently all in orchestrator)
- ⚠️ Extract step_1_export_docker_compose
- ⚠️ Extract step_2_export_env_file
- ⚠️ Extract step_3_export_manifest
- ⚠️ Move cfg_writer.py to utils/

**Future Libraries:**
- ⚠️ libraries/validation (when validation units are extracted)
- ⚠️ libraries/transformation (when transformers are extracted)
- ⚠️ libraries/io (when file handlers are extracted)
- ⚠️ libraries/export (when export generators are extracted)

### Recent Changes (October 14, 2025)

**Units & Libraries Implementation:**
1. Created `phases/libraries/probing/` directory
2. Extracted units from step_2_system_discovery:
   - `docker.py` → `libraries/probing/docker_detector.py`
   - `network.py` → `libraries/probing/network_detector.py`
   - `system.py` → `libraries/probing/system_detector.py`
3. Created library `__init__.py` with exports
4. Updated `control_flows.yml` to declare units
5. Updated `system_discovery.py` imports to use library
6. Removed old co-located unit files
7. Verified Phase 1 execution works with library imports

---

## Development Guide

### Running the System

**Complete workflow:**
```bash
cd /opt/openproject/external/config-manager
python3 -m phases.phases_orchestrator
```

**Individual phases:**
```bash
# Phase 1: Discovery
python3 -m phases.phase_1_discovery.orchestrator_discovery

# Phase 2: TUI Mapping
python3 -m phases.phase_2_tui_mapping.orchestrator_tui_mapping

# Phase 3: Collection
python3 -m phases.phase_3_collection.orchestrator_collection

# Phase 4: Validation
python3 -m phases.phase_4_validation.orchestrator_validation

# Phase 5: Export
python3 -m phases.phase_5_export.orchestrator_export
```

**Individual steps:**
```bash
# Step can be run standalone if it has __main__ block
python3 phases/phase_1_discovery/step_2_system_discovery/system_discovery.py
```

### Testing

**Unit tests (for library units):**
```bash
pytest tests/libraries/probing/test_docker_detector.py
pytest tests/libraries/probing/test_network_detector.py
pytest tests/libraries/probing/test_system_detector.py
```

**Step tests:**
```bash
pytest tests/steps/test_system_discovery.py
```

**Integration tests:**
```bash
pytest tests/integration/test_phase_1_discovery.py
```

**All tests:**
```bash
pytest tests/
```

### Adding a New Unit

**1. Determine if unit is needed:**
- Is logic reused by 2+ steps? → Yes, create unit
- Is logic >50 lines and complex? → Yes, create unit
- Is logic simple and step-specific? → No, keep in step

**2. Choose library:**
- Does library exist for this domain? → Add to existing library
- No library exists and 3+ units? → Create new library
- No library exists and <3 units? → Co-locate, extract later

**3. Create unit file:**

```python
# phases/libraries/probing/new_detector.py
"""
New detection unit.

Unit: NewDetector
Library: probing
Domain Method: detect()
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class NewDetector:
    """
    Unit: Detect something new.
    
    Single Responsibility: Describe what this detects.
    """
    
    def __init__(self):
        """Initialize detector."""
        pass
    
    def detect(self) -> Dict[str, Any]:
        """
        Detect something.
        
        Returns:
            Dictionary with detection results
        """
        # Implementation here
        return {}
```

**4. Update library __init__.py:**

```python
# phases/libraries/probing/__init__.py
from .new_detector import NewDetector

__all__ = [
    'DockerDiscovery',
    'NetworkDiscovery',
    'SystemDiscovery',
    'NewDetector',  # Add this
]
```

**5. Declare in YAML (optional but recommended):**

```yaml
steps:
  - step_id: some_step
    units:
      - unit_id: new_detector
        library: probing
        class: NewDetector
        method: detect
        description: Detects something new
```

**6. Use in step:**

```python
from phases.libraries.probing import NewDetector

def execute_some_step(context, phase_dir):
    detector = NewDetector()
    result = detector.detect()
    return {'detection_result': result}
```

**7. Write tests:**

```python
# tests/libraries/probing/test_new_detector.py
import pytest
from phases.libraries.probing import NewDetector

class TestNewDetector:
    def test_detect(self):
        detector = NewDetector()
        result = detector.detect()
        assert 'expected_key' in result
```

### Adding a New Step

**1. Add to YAML:**

```yaml
phases:
  - phase_id: some_phase
    steps:
      - step_id: new_step
        name: New Step Name
        type: processing
        description: What this step does
        sequence: 3
        dependencies:
          - previous_step
        artifacts_produced:
          - new_artifact
```

**2. Create step directory:**

```bash
mkdir -p phases/phase_X_name/step_Y_new_step
```

**3. Create step file:**

```python
# phases/phase_X_name/step_Y_new_step/new_step.py
"""
Step: New Step Name

Description of what this step does.
"""

from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def execute_new_step(
    context: Dict[str, Any],
    phase_dir: Path
) -> Dict[str, Any]:
    """
    Execute new step.
    
    Args:
        context: Execution context
        phase_dir: Phase directory path
        
    Returns:
        Dict with step results
    """
    logger.info("Executing step: New Step Name")
    
    # Step implementation
    result = {}
    
    logger.info("Step New Step Name completed")
    return result
```

**4. Regenerate phase orchestrator:**

```bash
cd /opt/openproject/external/control-flow
python3 src/control_flow_engine/core/orchestrator_regenerator.py \
    --spec /path/to/control_flows.yml \
    --type phase \
    --orchestrator /path/to/orchestrator_phase.py \
    --phase-id phase_name \
    --flow main_config_flow
```

**5. Test step:**

```python
# tests/steps/test_new_step.py
import pytest
from pathlib import Path
from phases.phase_X_name.step_Y_new_step.new_step import execute_new_step

class TestNewStep:
    def test_execute(self):
        context = {}
        phase_dir = Path('.')
        result = execute_new_step(context, phase_dir)
        assert 'expected_key' in result
```

### Regenerating Orchestrators

**After YAML changes, regenerate orchestrators:**

```bash
cd /opt/openproject/external/control-flow

# Regenerate global orchestrator
python3 src/control_flow_engine/core/orchestrator_regenerator.py \
    --spec ../config-manager/design_specs/control_flows.yml \
    --type global \
    --orchestrator ../config-manager/phases/phases_orchestrator.py \
    --flow main_config_flow

# Regenerate specific phase orchestrator
python3 src/control_flow_engine/core/orchestrator_regenerator.py \
    --spec ../config-manager/design_specs/control_flows.yml \
    --type phase \
    --orchestrator ../config-manager/phases/phase_1_discovery/orchestrator_discovery.py \
    --phase-id discovery \
    --flow main_config_flow
```

**Important:** Only content between markers is regenerated. Custom code outside markers is preserved.

---

## Summary

### Key Points

1. **5-Phase Workflow**: Discovery → TUI Mapping → Collection → Validation → Export
2. **YAML-Driven**: All structure defined in `control_flows.yml`
3. **Units & Libraries**: Reusable components in `phases/libraries/`
4. **Control Flow Integration**: Full control-flow engine implementation
5. **Status**: Phases 1-4 fully implemented, Phase 5 needs restructuring

### Quick Reference

| Task | Command/Location |
|------|------------------|
| Run complete workflow | `python3 -m phases.phases_orchestrator` |
| Run Phase 1 | `python3 -m phases.phase_1_discovery.orchestrator_discovery` |
| Edit workflow | `design_specs/control_flows.yml` |
| Probing units | `phases/libraries/probing/` |
| Discovery outputs | `phases/phase_1_discovery/outputs/discovery/` |
| TUI layouts | `phases/phase_*/step_*/*.layout.yml` |
| Tests | `pytest tests/` |

### Related Documentation

- **Control Flow System**: `/opt/openproject/external/control-flow/docs/CONTROL_FLOW_SYSTEM_REFERENCE.md`
- **Units & Libraries Pattern**: `/opt/openproject/external/control-flow/docs/UNITS_LIBRARIES_PATTERN.md`
- **Library Generator**: `/opt/openproject/external/control-flow/docs/LIBRARY_GENERATOR_USAGE.md`
- **Architecture Discussion**: `/opt/openproject/external/control-flow/docs/ARCHITECTURE_DISCUSSION_OCT14.md`

---

**Document Status:** Complete and current  
**Last Verified:** October 14, 2025  
**Purpose:** Context recovery and implementation reference
