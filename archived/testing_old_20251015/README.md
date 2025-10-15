# Testing Framework Documentation

Welcome to the OpenProject Configuration Manager testing framework! This directory contains comprehensive testing infrastructure organized for maintainability and clarity.

## 📁 Directory Structure

```
testing/
├── unit/                    # Fast unit tests for individual components
├── integration/             # Integration tests for multiple components
├── validation/              # Migration and configuration validation tests
├── e2e/                     # End-to-end workflow tests  
├── fixtures/                # Test data and configuration files
├── scripts/                 # Test runner utilities
├── config/                  # Test configuration files
├── results/                 # Test output and reports (gitignored)
├── documentation/           # Testing guides and documentation
└── env/                     # Virtual environment (gitignored)
```

## 🚀 Quick Start

### Run All Tests
```bash
cd /opt/openproject/external/config-manager
python testing/scripts/run_all_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only (fast)
python testing/scripts/run_unit_tests.py

# Integration tests only
python testing/scripts/run_integration_tests.py  

# End-to-end tests only
python testing/scripts/run_e2e_tests.py
```

### Run Tests with Pytest Directly
```bash
# All tests
pytest testing/

# Specific test type  
pytest testing/unit/
pytest testing/integration/
pytest testing/e2e/

# With coverage
pytest testing/ --cov=openproject_config_manager --cov-report=html
```

## 📋 Test Categories

### Unit Tests (`testing/unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: Minimal, heavily mocked
- **Files**:
  - `test_core_config.py` - Configuration model tests
  - `test_ui_console.py` - UI component tests
  - `test_discovery_environment.py` - Environment discovery tests
  - `test_export_cfg_writer.py` - Configuration export tests
  - `test_validation_validator.py` - Validation logic tests

### Integration Tests (`testing/integration/`)
- **Purpose**: Test multiple components working together
- **Speed**: Medium (1-10 seconds per test)
- **Dependencies**: Real components, some external dependencies
- **Files**:
  - `test_integration.py` - Cross-component integration
  - `test_collector_interactive.py` - Interactive collection flows
  - `test_main_cli.py` - CLI interface integration

### End-to-End Tests (`testing/e2e/`)
- **Purpose**: Test complete user workflows
- **Speed**: Slow (10+ seconds per test)
- **Dependencies**: Full system, real file I/O
- **Files**:
  - `test_e2e_ui_workflows.py` - Complete configuration workflows

## 🔧 Configuration

- **pytest.ini**: Located in `testing/config/pytest.ini`
- **pyproject.toml**: Main project config also contains pytest settings
- **conftest.py**: Shared fixtures in each test directory

## 📊 Coverage and Reporting

Test results and coverage reports are stored in `testing/results/` and are automatically ignored by git.

## 🏃‍♂️ CI/CD Integration

The GitHub Actions workflow automatically runs all test types in the correct sequence:
1. Unit tests (fast feedback)
2. Integration tests (component interaction)  
3. E2E tests (full workflows)

## 📚 Best Practices

1. **Write unit tests first** - Fast feedback loop
2. **Mock external dependencies** in unit tests
3. **Use real components** in integration tests
4. **Test real user scenarios** in E2E tests
5. **Keep tests independent** - No test dependencies
6. **Use descriptive test names** - Clear intent
7. **Maintain test fixtures** in conftest.py files

## 🐛 Debugging Tests

```bash
# Run with verbose output
pytest testing/ -v -s

# Run specific test
pytest testing/unit/test_core_config.py::TestConfiguration::test_basic_config

# Debug with pdb
pytest testing/ --pdb

# See coverage gaps
pytest testing/ --cov=openproject_config_manager --cov-report=html
open htmlcov/index.html
```

---

For more detailed information, see the individual documentation files in this directory.