# Config Manager Testing Structure

## Test Organization

```
tests/
├── integration/                     # Integration Tests
│   ├── test_e2e_integration.py     # End-to-end workflow testing
│   └── test_manager_integration.py # ConfigurationManager integration
│
└── validation/                     # Validation Tests  
    └── test_migration_validation.py # Migration feature parity validation
```

## Test Categories

### Integration Tests (`tests/integration/`)

**`test_e2e_integration.py`**
- **Purpose**: End-to-end workflow testing
- **Scope**: Full discovery → collection → validation flow
- **Features**: Mocked system calls, UI testing, workflow validation
- **Usage**: `python tests/integration/test_e2e_integration.py`

**`test_manager_integration.py`**
- **Purpose**: ConfigurationManager component integration
- **Scope**: Manager initialization, FlowEngine integration, component interaction
- **Features**: Integration testing between core components
- **Usage**: `python tests/integration/test_manager_integration.py`

### Validation Tests (`tests/validation/`)

**`test_migration_validation.py`**
- **Purpose**: Migration feature parity validation
- **Scope**: Rich → Questionary migration, performance comparison, comprehensive functionality
- **Features**: Feature parity checks, performance metrics, regression testing
- **Usage**: `python tests/validation/test_migration_validation.py`

## Test Types by Purpose

### **Integration Tests**
- Test component interactions
- Verify workflow completeness
- Mock external dependencies
- Validate data flow between components

### **Validation Tests**
- Ensure migration completeness
- Performance regression testing
- Feature parity verification
- Comprehensive functionality checks

## Running Tests

### Individual Tests
```bash
# End-to-end integration
python tests/integration/test_e2e_integration.py

# Manager integration  
python tests/integration/test_manager_integration.py

# Migration validation
python tests/validation/test_migration_validation.py
```

### All Integration Tests
```bash
python -m pytest tests/integration/
```

### All Validation Tests
```bash
python -m pytest tests/validation/
```

### All Tests
```bash
python -m pytest tests/
```

## Test Dependencies

All tests include proper path setup to access:
- `src/openproject_config_manager/` - Core source code
- `src/openproject_config_manager/collector/` - TUI collectors
- External dependencies (TUI Form Engine, etc.)

## Test Organization Benefits

1. **Clear Separation** - Integration vs validation testing
2. **Logical Grouping** - Related tests grouped together
3. **Easy Discovery** - Tests easy to find and run
4. **Scalability** - Easy to add new test categories
5. **CI/CD Ready** - Standard pytest structure for automation

## Relationship to Source Code

```
src/openproject_config_manager/
├── collector/               # Tested by integration tests
│   ├── layouts/            # Layout files tested
│   ├── defaults/           # Defaults system tested  
│   ├── tools/             # Development tools (separate testing)
│   └── tui_collector.py   # Core TUI integration tested
├── core/                   # Tested by integration & validation
└── ...

tests/
├── integration/            # Tests component interactions
└── validation/            # Tests migration completeness
```

## Clean Root Directory

After moving test files, the root directory now contains only:
- Core configuration files (pyproject.toml, etc.)
- Documentation files
- Integration demos (demo_migration_complete.py)
- Main source code (src/)
- Organized tests (tests/)

This creates a clean, professional project structure! 🚀