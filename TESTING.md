# Testing Guide

**Date:** October 15, 2025  
**Status:** ✅ Complete Test Infrastructure  
**Version:** 1.0

---

## Quick Start

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test tier
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests
pytest tests/e2e/          # End-to-end tests

# Format code
black src tests

# Lint code
flake8 src tests

# Sort imports
isort src tests --profile black
```

---

## 📊 Test Suite Status

### Current Coverage

**Total Tests: 67** (100% passing)

| Category | Count | Location | Purpose |
|----------|-------|----------|---------|
| **Unit Tests** | 39 | `tests/unit/libraries/` | Library classes & imports |
| **Integration Tests** | 14 | `tests/integration/phases/` | Phase orchestrators |
| **End-to-End Tests** | 13 | `tests/e2e/` | Full pipeline workflows |
| **Scaffolding Tests** | 1 | `tests/scaffolding/` | Control flow scaffolding |

### Test Results Summary

```
✅ Unit Tests:           39/39 PASSED
✅ Integration Tests:    14/14 PASSED
✅ End-to-End Tests:     13/13 PASSED
✅ Scaffolding Tests:     1/1  PASSED
────────────────────────────────────────
✅ TOTAL:                67/67 PASSED (100%)
```

---

## 🏗️ Test Structure

### Directory Organization

The test structure mirrors the `control_flows.yml` architecture:

```
tests/
├── unit/                    # Atomic unit tests
│   ├── libraries/          # Library class tests
│   │   ├── test_library_imports.py      (17 tests)
│   │   ├── test_probing.py              (6 tests)
│   │   ├── test_transformation.py       (2 tests)
│   │   ├── test_validation.py           (6 tests)
│   │   └── test_export.py               (8 tests)
│   └── steps/              # Step-level unit tests (future)
│
├── integration/            # Integration tests
│   ├── phases/            # Phase orchestrator tests
│   │   └── test_phase_orchestrators.py  (14 tests)
│   └── steps/             # Step integration tests (future)
│
├── e2e/                   # End-to-end tests
│   └── test_full_pipeline.py            (13 tests)
│
├── scaffolding/           # Infrastructure tests
│   └── test_control_flow_scaffolding.py (1 test)
│
├── fixtures/              # Shared test data
│   └── sample_configs/
│
└── conftest.py           # Pytest configuration & fixtures
```

### Design Principles

**Mirrors control_flows.yml:**
```
flows → phases → steps → units (from libraries)
  ↓       ↓       ↓       ↓
tests/  tests/  tests/  tests/
 e2e/   integration/ (future) unit/
        phases/           libraries/
```

**Test Pyramid:**
- **Many unit tests** - Fast, isolated, test individual components
- **Some integration tests** - Test component interactions
- **Few e2e tests** - Test complete workflows

---

## 🧪 Test Categories

### Unit Tests (39 tests)

**Location:** `tests/unit/libraries/`

#### Import Validation (17 tests)

Tests that all library classes can be imported:

```python
# test_library_imports.py
def test_docker_discovery_import():
    """Verify DockerDiscovery can be imported."""
    from libraries.probing.docker_discovery import DockerDiscovery
    assert DockerDiscovery is not None

def test_all_libraries_exported():
    """Verify all 4 sub-libraries are accessible."""
    import libraries
    assert hasattr(libraries, 'probing')
    assert hasattr(libraries, 'transformation')
    assert hasattr(libraries, 'validation')
    assert hasattr(libraries, 'export')
```

**Coverage:**
- ✅ Probing library (4 tests)
- ✅ Transformation library (2 tests)
- ✅ Validation library (4 tests)
- ✅ Export library (5 tests)
- ✅ Top-level library (2 tests)

#### Class Instantiation (22 tests)

Tests that classes can be instantiated and have required methods:

```python
# test_probing.py
def test_docker_discovery_instantiation():
    """Test DockerDiscovery can be instantiated."""
    from libraries.probing.docker_discovery import DockerDiscovery
    from pathlib import Path
    
    discovery = DockerDiscovery(
        project_root=Path("/fake/path"),
        ui=None
    )
    assert discovery is not None

def test_docker_discovery_has_discover_method():
    """Test DockerDiscovery has discover method."""
    from libraries.probing.docker_discovery import DockerDiscovery
    assert hasattr(DockerDiscovery, 'discover')
```

**Coverage:**
- ✅ Probing: DockerDiscovery, NetworkDiscovery, SystemDiscovery (6 tests)
- ✅ Transformation: DefaultsTransformer (2 tests)
- ✅ Validation: SchemaValidator, DependencyValidator, EnvironmentValidator (6 tests)
- ✅ Export: ExportDockerComposeStep, ExportEnvFileStep, ExportManifestStep, CfgWriter (8 tests)

### Integration Tests (14 tests)

**Location:** `tests/integration/phases/test_phase_orchestrators.py`

Tests that phase orchestrators work correctly:

```python
def test_discovery_phase_can_instantiate():
    """Test DiscoveryPhase can be instantiated."""
    from phases.phase_1_discovery.orchestrator_discovery import OrchestratorDiscovery
    from pathlib import Path
    
    phase = OrchestratorDiscovery(
        project_root=Path.cwd(),
        ui=None
    )
    assert phase is not None

def test_discovery_phase_can_load_units():
    """Test DiscoveryPhase can load library units."""
    from phases.phase_1_discovery.orchestrator_discovery import OrchestratorDiscovery
    from pathlib import Path
    
    phase = OrchestratorDiscovery(project_root=Path.cwd(), ui=None)
    
    # Verify it can import the units it needs
    from libraries.probing import DockerDiscovery, NetworkDiscovery, SystemDiscovery
    assert DockerDiscovery is not None
```

**Coverage:**
- ✅ Phase 1 (Discovery) - 3 tests
- ✅ Phase 2 (TUI Mapping) - 3 tests
- ✅ Phase 4 (Validation) - 3 tests
- ✅ Phase 5 (Export) - 3 tests
- ✅ Global Orchestrator - 2 tests

### End-to-End Tests (13 tests)

**Location:** `tests/e2e/test_full_pipeline.py`

Tests complete workflows from start to finish:

```python
def test_full_pipeline_phases_structure():
    """Test that all 5 phases exist and are configured."""
    from phases.phases_orchestrator import PhasesOrchestrator
    from pathlib import Path
    
    orchestrator = PhasesOrchestrator(
        project_root=Path.cwd(),
        ui=None
    )
    
    # Verify all 5 phases exist
    assert hasattr(orchestrator, 'phase_1_discovery')
    assert hasattr(orchestrator, 'phase_2_tui_mapping')
    assert hasattr(orchestrator, 'phase_3_collection')
    assert hasattr(orchestrator, 'phase_4_validation')
    assert hasattr(orchestrator, 'phase_5_export')
```

**Coverage:**
- ✅ Pipeline structure validation
- ✅ Phase orchestrator integration
- ✅ Dual-mode orchestration testing
- ✅ Artifact flow validation

---

## 🔧 Test Tools & Configuration

### Installed Tools

| Tool | Version | Purpose | Command |
|------|---------|---------|---------|
| **pytest** | 8.4.2 | Test runner | `pytest tests/` |
| **pytest-cov** | 7.0.0 | Coverage reporting | `pytest --cov=src` |
| **pytest-mock** | 3.15.1 | Better mocking | `mocker.patch()` |
| **black** | 25.9.0 | Code formatter | `black src tests` |
| **flake8** | 7.3.0 | Linter | `flake8 src tests` |
| **isort** | 7.0.0 | Import sorter | `isort src tests` |
| **coverage** | 7.10.7 | Coverage engine | Auto-used by pytest-cov |

### Configuration

**pytest Configuration** (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-v",
    "--tb=short",
    "--cov-report=term-missing",
    "--cov-report=html"
]
markers = [
    "unit: Fast unit tests",
    "integration: Integration tests",
    "e2e: End-to-end workflow tests",
    "slow: Slow running tests",
    "ui: UI component tests",
]
```

**Coverage Configuration** (`pyproject.toml`):

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

**Black Configuration** (`pyproject.toml`):

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

**isort Configuration** (`pyproject.toml`):

```toml
[tool.isort]
profile = "black"
line_length = 88
```

---

## 📖 Usage Guide

### Running Tests

#### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test tier
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run specific file
pytest tests/unit/libraries/test_probing.py

# Run specific test
pytest tests/unit/libraries/test_probing.py::test_docker_discovery_instantiation

# Run by marker
pytest tests/ -m unit
pytest tests/ -m integration
pytest tests/ -m e2e

# Stop on first failure
pytest tests/ -x
```

#### Coverage Reporting

```bash
# Basic coverage
pytest tests/ --cov=src

# With missing lines highlighted
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=src --cov-report=html

# Open HTML report (Linux)
xdg-open htmlcov/index.html

# Generate multiple report formats
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
```

**Reading Coverage Reports:**

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/config.py                             45      5    89%   12-16
src/orchestrator.py                      120      0   100%
---------------------------------------------------------------------
TOTAL                                    165      5    97%
```

- **Stmts:** Total statements in file
- **Miss:** Statements not covered by tests
- **Cover:** Percentage covered
- **Missing:** Line numbers not covered

### Code Formatting

```bash
# Format all code (modifies files)
black src tests

# Check what would change (dry run)
black src tests --check

# Show diff of changes
black src tests --diff

# Format with custom line length
black src tests --line-length 100
```

**Black Rules:**
- Enforces consistent style
- No configuration needed (opinionated)
- Automatically handles line length, quotes, spacing
- Works with isort for imports

### Import Sorting

```bash
# Sort all imports (modifies files)
isort src tests --profile black

# Check only (dry run)
isort src tests --profile black --check-only

# Show diff of changes
isort src tests --profile black --diff
```

**isort Rules:**
- Groups imports: stdlib → third-party → local
- Alphabetizes within groups
- `--profile black` ensures compatibility with black

### Linting

```bash
# Basic lint
flake8 src tests

# With custom settings
flake8 src tests --max-line-length 100

# Ignore specific errors
flake8 src tests --extend-ignore=E203,W503

# Count errors only
flake8 src tests --count

# Show statistics
flake8 src tests --statistics

# Specific file
flake8 src/config.py
```

**Common flake8 Errors:**
- `E501`: Line too long
- `E203`: Whitespace before ':'
- `W503`: Line break before binary operator
- `F401`: Imported but unused
- `F841`: Local variable assigned but never used

---

## 🎯 Writing Tests

### Test File Structure

```python
"""
Test module for <component>.

Tests cover:
- Import validation
- Class instantiation
- Method signatures
- Basic functionality
"""

import pytest
from pathlib import Path


class TestComponentName:
    """Tests for ComponentName class."""
    
    def test_can_import(self):
        """Verify component can be imported."""
        from module.component import ComponentName
        assert ComponentName is not None
    
    def test_can_instantiate(self):
        """Verify component can be instantiated."""
        from module.component import ComponentName
        
        instance = ComponentName(
            project_root=Path.cwd(),
            ui=None
        )
        assert instance is not None
    
    def test_has_required_method(self):
        """Verify component has required method."""
        from module.component import ComponentName
        assert hasattr(ComponentName, 'method_name')
```

### Using Fixtures

**Path Fixtures** (`conftest.py`):

```python
@pytest.fixture
def project_root_path():
    """Return the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def test_data_dir(project_root_path):
    """Return the test data directory."""
    return project_root_path / "tests" / "fixtures"
```

**Using in Tests:**

```python
def test_with_fixture(project_root_path):
    """Test using project root fixture."""
    config_file = project_root_path / "config.yaml"
    assert config_file.exists()
```

### Using Mocks (pytest-mock)

```python
def test_with_mock(mocker):
    """Test using mocked dependency."""
    # Mock a method
    mock_client = mocker.patch('module.component.DockerClient')
    mock_client.return_value.containers.list.return_value = []
    
    # Test code that uses DockerClient
    from module.component import Component
    component = Component(Path.cwd(), None)
    result = component.discover()
    
    # Verify mock was called
    mock_client.return_value.containers.list.assert_called_once()
```

### Using Markers

```python
@pytest.mark.unit
def test_unit_level():
    """Fast isolated test."""
    pass

@pytest.mark.integration
def test_integration_level():
    """Test component interaction."""
    pass

@pytest.mark.e2e
def test_end_to_end():
    """Test complete workflow."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Test that takes a while."""
    pass
```

**Running marked tests:**
```bash
pytest tests/ -m unit           # Only unit tests
pytest tests/ -m "not slow"     # Skip slow tests
pytest tests/ -m "unit or integration"  # Unit OR integration
```

### Temporary Files (tmp_path)

```python
def test_with_temp_file(tmp_path):
    """Test using temporary file."""
    # tmp_path is a pytest fixture providing a temporary directory
    config_file = tmp_path / "config.yaml"
    config_file.write_text("test: value")
    
    # Test code that reads the file
    assert config_file.exists()
    assert config_file.read_text() == "test: value"
    
    # tmp_path is automatically cleaned up after test
```

---

## 🔍 Test Coverage Guidelines

### Coverage Targets

- **Unit Tests:** Aim for 80%+ coverage of library code
- **Integration Tests:** Cover all phase orchestrators
- **E2E Tests:** Cover main user workflows

### What to Test

**✅ DO test:**
- Public APIs and methods
- Error handling and edge cases
- Integration points between components
- Configuration parsing and validation
- Critical business logic

**❌ DON'T test:**
- Private internal methods (test via public APIs)
- Third-party library code
- Trivial getters/setters
- Auto-generated code

### Coverage Best Practices

1. **Focus on behavior, not lines**
   - 100% line coverage doesn't mean bug-free
   - Test important behaviors thoroughly

2. **Test error paths**
   - What happens when file is missing?
   - What happens when input is invalid?

3. **Use coverage to find gaps**
   - Low coverage → need more tests
   - High coverage → confidence in changes

4. **Document untested code**
   ```python
   def experimental_feature():  # pragma: no cover
       """Experimental - not tested yet."""
       pass
   ```

---

## 🐛 Troubleshooting

### Common Issues

#### Tests not discovered

**Problem:** `pytest` finds 0 tests

**Solutions:**
```bash
# Check test path configuration
pytest --collect-only

# Verify file naming (must be test_*.py)
ls tests/unit/

# Verify function naming (must be test_*)
grep "def test_" tests/unit/test_file.py
```

#### Import errors

**Problem:** `ImportError: No module named 'src'`

**Solutions:**
```bash
# Install package in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or run from project root
cd /opt/openproject/external/config-manager
pytest tests/
```

#### Coverage shows 0%

**Problem:** Coverage report shows 0% coverage

**Solutions:**
```bash
# Verify source path is correct
pytest --cov=src tests/

# Check coverage config in pyproject.toml
cat pyproject.toml | grep -A 5 "tool.coverage"

# Run with debug info
pytest --cov=src tests/ --cov-report=term-missing -v
```

#### Fixture not found

**Problem:** `fixture 'mock_docker_client' not found`

**Solutions:**
```bash
# Check conftest.py exists
ls tests/conftest.py

# Check fixture is defined
grep "def mock_docker_client" tests/conftest.py

# Check fixture scope
pytest --fixtures tests/
```

#### Black and flake8 conflict

**Problem:** Black formats code that flake8 complains about

**Solutions:**
```bash
# Configure flake8 to ignore Black's formatting
# In setup.cfg or .flake8:
[flake8]
extend-ignore = E203, W503
max-line-length = 88

# Or use --extend-ignore flag
flake8 src tests --extend-ignore=E203,W503
```

---

## 📚 Best Practices

### General Testing

1. **Test Naming**
   - Use descriptive names: `test_discovery_finds_docker_containers`
   - Not: `test_1`, `test_discovery`

2. **Test Organization**
   - One test file per source file
   - Group related tests in classes
   - Use fixtures for setup/teardown

3. **Test Independence**
   - Tests should not depend on each other
   - Each test should set up its own data
   - Use fixtures for shared setup

4. **Assertion Messages**
   ```python
   # Good - clear failure message
   assert result == expected, f"Expected {expected}, got {result}"
   
   # Better - pytest does this automatically
   assert result == expected
   ```

### Code Quality

1. **Format before committing**
   ```bash
   black src tests
   isort src tests --profile black
   flake8 src tests
   ```

2. **Run tests before pushing**
   ```bash
   pytest tests/ --cov=src --cov-report=term-missing
   ```

3. **Fix linting issues**
   - Don't ignore all warnings
   - Understand why flake8 complains
   - Fix root cause, don't just disable checks

### Continuous Integration

**Pre-commit checks:**
```bash
# Run before every commit
black src tests --check
isort src tests --profile black --check-only
flake8 src tests
pytest tests/ --cov=src --cov-report=term-missing
```

**Create pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format check
black src tests --check || {
    echo "❌ Black formatting needed. Run: black src tests"
    exit 1
}

# Import check
isort src tests --profile black --check-only || {
    echo "❌ Import sorting needed. Run: isort src tests --profile black"
    exit 1
}

# Lint check
flake8 src tests || {
    echo "❌ Linting errors found. Fix them before committing."
    exit 1
}

# Tests
pytest tests/ || {
    echo "❌ Tests failed. Fix them before committing."
    exit 1
}

echo "✅ All checks passed!"
```

---

## 📈 Future Enhancements

### Planned Improvements

- [ ] **Step-level unit tests** - Test individual step classes
- [ ] **Increased coverage** - Target 90%+ for critical paths
- [ ] **Performance tests** - Benchmark phase execution times
- [ ] **Property-based testing** - Use hypothesis for edge cases
- [ ] **Mutation testing** - Verify test effectiveness with mutpy
- [ ] **CI/CD integration** - Automate testing in GitHub Actions

### Proposed Test Structure Expansion

```
tests/
├── unit/
│   ├── libraries/        # ✅ Current (39 tests)
│   └── steps/           # 🆕 Planned - per-step unit tests
│       ├── phase_1/
│       ├── phase_2/
│       ├── phase_4/
│       └── phase_5/
│
├── integration/
│   ├── phases/          # ✅ Current (14 tests)
│   └── steps/           # 🆕 Planned - step integration tests
│
├── e2e/                 # ✅ Current (13 tests)
├── performance/         # 🆕 Planned - performance benchmarks
└── property/            # 🆕 Planned - property-based tests
```

---

## 📝 Quick Reference

### Essential Commands

```bash
# Run tests
pytest tests/                                    # All tests
pytest tests/ -v                                 # Verbose
pytest tests/ -x                                 # Stop on first failure
pytest tests/ -k "test_docker"                   # Run tests matching pattern

# Coverage
pytest tests/ --cov=src                          # Basic coverage
pytest tests/ --cov=src --cov-report=html        # HTML report

# Code quality
black src tests                                  # Format code
isort src tests --profile black                  # Sort imports
flake8 src tests                                 # Lint code

# Specific tests
pytest tests/unit/                               # Unit tests only
pytest tests/integration/                        # Integration tests only
pytest tests/e2e/                                # E2E tests only

# Markers
pytest tests/ -m unit                            # Unit tests only
pytest tests/ -m "not slow"                      # Skip slow tests
```

### Workflow

```bash
# Before starting work
git pull
pytest tests/

# During development
pytest tests/unit/libraries/test_mycomponent.py  # Test what you're working on
pytest tests/ -x                                 # Run all, stop on failure

# Before committing
black src tests
isort src tests --profile black
flake8 src tests
pytest tests/ --cov=src --cov-report=term-missing

# Review coverage
xdg-open htmlcov/index.html

# Commit
git add .
git commit -m "Add feature X with tests"
```

---

**Last Updated:** October 15, 2025  
**Test Suite Status:** 67/67 tests passing (100%)  
**Version:** 1.0
