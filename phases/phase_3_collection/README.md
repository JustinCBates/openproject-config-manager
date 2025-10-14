# Phase 3: Interactive Collection

## Overview

Phase 3 collects user configuration through an interactive Terminal User Interface (TUI). It uses the TUI Form Engine to present a user-friendly form based on layout definitions and defaults from Phase 2.

## Architecture

```
Phase 3: Interactive Collection
├── orchestrator_collection.py       # Phase orchestrator
├── step_1_collect_user_configuration/
│   ├── collect_user_configuration.py   # Entry point
│   ├── tui_collector.py                # TUI collector implementation (migrated)
│   └── layouts/                        # TUI layout definitions
│       ├── config_tui.layout.yml       # Main layout
│       ├── defaults/                   # Default values
│       ├── sublayouts/                 # Component layouts
│       └── test_layouts/               # Test configurations
├── outputs/
│   ├── collected_configuration.yml     # Primary output for Phase 4
│   └── config_tui.layout_responses.json # Raw user responses
└── tests/
    └── test_collection_phase.py        # Phase tests
```

## Migration History

Phase 3 was migrated from:
- **Source**: `src/openproject_config_manager/collector/tui_collector.py`
- **Date**: 2025-10-13
- **Changes**:
  - Simplified to focus on collection only (validation moved to Phase 4)
  - Added graceful handling for missing TUI Form Engine
  - Support for mock responses for testing
  - Integrated with Phase 2 TUI defaults output
  - Layouts migrated to step directory

## Input (Consumed Artifacts)

- **tui_defaults_file**: `phases/phase_2_tui_mapping/outputs/tui/tui_defaults.yml`
  - Contains transformed defaults ready for TUI consumption
  - Optional but recommended

## Output (Produced Artifacts)

- **user_configuration**: `phases/phase_3_collection/outputs/collected_configuration.yml`
  - Primary output containing:
    - `metadata`: Collection information (timestamp, flow name, etc.)
    - `user_responses`: Raw user input from TUI
    - `tui_defaults_applied`: Whether defaults were loaded
    - `collection_method`: "tui_form_engine" or "mock"

- **responses_file**: `phases/phase_3_collection/outputs/{flow_name}_responses.json`
  - Raw JSON responses for debugging

## Usage

### Via Main Orchestrator

```bash
# Execute Phase 3 only (with mock responses)
python3 phases/phases_orchestrator.py --phase 3

# Execute Phases 1-3
python3 phases/phases_orchestrator.py --start 1 --end 3
```

### Standalone Testing

```bash
# With mock responses
python3 phases/phase_3_collection/test_manual.py

# Direct TUI collector (requires TUI engine)
cd phases/phase_3_collection/step_1_collect_user_configuration
python3 tui_collector.py --mock-file mocks.json
```

### Programmatic Usage

```python
from phases.phase_3_collection.orchestrator_collection import CollectionPhase

phase = CollectionPhase(project_root)

# With mock responses for testing
context = {
    'flow_name': 'config_tui.layout',
    'mock_responses': {...},
    'tui_defaults_file': 'path/to/tui_defaults.yml'
}

result = phase.execute(context)
output_file = result['user_configuration']
```

## Dependencies

### Required
- `pyyaml` - YAML parsing
- Python 3.8+

### Optional
- `tui-form-engine` - For interactive TUI (from tui-form-designer submodule)
  - Located in `/opt/openproject/external/tui-form-designer/src/tui_form_engine/`
  - Required for interactive mode
  - Not required for mock/testing mode

## Configuration Files

### Layout Files

Layout files define the TUI form structure:

- **config_tui.layout.yml**: Main layout defining all form fields
- **defaults/**: Default values for fields
- **sublayouts/**: Reusable layout components
- **test_layouts/**: Test-specific layouts

## Testing

### Unit Tests

```bash
# Run pytest tests (if pytest installed)
pytest phases/phase_3_collection/tests/

# Manual testing
python3 phases/phase_3_collection/test_manual.py
```

### Integration Tests

```bash
# Test Phase 1-3 pipeline
python3 test_pipeline_1_to_3.py
```

## Mock Responses Format

For testing without the TUI engine, provide mock responses:

```python
mock_responses = {
    'project': {
        'name': 'my-project',
        'environment': 'production'
    },
    'admin': {
        'email': 'admin@example.com',
        'password': 'secure123'
    },
    'database': {
        'type': 'postgresql',
        'setup': 'container'
    },
    'network': {
        'domain': 'example.com'
    },
    # ... other sections
}
```

## Output Format

### collected_configuration.yml

```yaml
metadata:
  collected_by: config-manager-phase-3
  timestamp: '2025-10-13T21:51:37.010176'
  flow_name: config_tui.layout
  flow_version: 1.0.0
user_responses:
  project:
    name: my-project
    environment: production
  admin:
    email: admin@example.com
    password: secure123
  # ... all collected responses
tui_defaults_applied: true
collection_method: mock
```

## Error Handling

### TUI Engine Not Available

If the TUI Form Engine is not installed:
- Collector will log a warning
- Interactive mode will be disabled
- Must provide `mock_responses` in context
- Raises `RuntimeError` if neither engine nor mocks available

### Flow File Not Found

If layout file is missing:
- Raises `FileNotFoundError` with clear message
- Check that layouts were copied to step directory

### Phase 2 Defaults Missing

If TUI defaults file doesn't exist:
- Logs a warning
- Continues with `tui_defaults_applied: false`
- Uses empty defaults dict

## Future Enhancements

1. **Interactive Mode**: Install tui-form-engine for full interactive TUI
2. **Layout Validation**: Validate layout files before rendering
3. **Progress Indicators**: Show collection progress in TUI
4. **Field-level Validation**: Real-time validation during input
5. **Response History**: Save/load previous responses

## Related Files

- **Control Flows**: `design_specs/control_flows.yml`
- **Phase 2 Output**: `phases/phase_2_tui_mapping/outputs/tui/tui_defaults.yml`
- **Phase 4 Input**: Phase 4 validation expects this output format

## Status

✅ **IMPLEMENTED** - Phase 3 migration complete
- Basic collection with mock responses working
- Integration with Phase 2 working
- Layouts migrated to step directory
- Tests passing
- Documentation complete

⚠️ **TUI Engine Integration Pending**
- Requires tui-form-designer submodule installation
- Interactive mode not yet tested
- Mock mode fully functional for testing
