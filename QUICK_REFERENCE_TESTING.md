# Test Tooling Quick Reference

**One-line reminders for common test and code quality commands**

---

## 🧪 Running Tests

```bash
# Basic test run
pytest tests/

# With coverage
pytest tests/ --cov=src

# Coverage with missing lines
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html && open htmlcov/index.html

# Run specific test tier
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
pytest tests/e2e/         # E2E tests only

# Run by marker
pytest tests/ -m unit
pytest tests/ -m integration
pytest tests/ -m e2e

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Run specific test file
pytest tests/unit/libraries/test_probing.py

# Run specific test
pytest tests/unit/libraries/test_probing.py::TestDockerDiscovery::test_can_instantiate
```

---

## 🎨 Code Formatting

```bash
# Format all code (modifies files)
black src tests

# Check what would change (no modifications)
black src tests --check

# Show diff
black src tests --diff

# Format with custom line length
black src tests --line-length 100
```

---

## 📦 Import Organization

```bash
# Sort all imports (modifies files)
isort src tests --profile black

# Check only (no modifications)
isort src tests --profile black --check-only

# Show diff
isort src tests --profile black --diff
```

---

## 🔍 Linting

```bash
# Basic lint
flake8 src tests

# With custom settings
flake8 src tests --max-line-length 100 --extend-ignore=E203,W503

# Count errors only
flake8 src tests --count

# Show statistics
flake8 src tests --statistics

# Specific file
flake8 src/openproject_config_manager/core/config.py
```

---

## 🚀 Pre-Commit Workflow

```bash
# All-in-one: Format, sort, lint, test with coverage
black src tests && isort src tests --profile black && flake8 src tests --count && pytest tests/ --cov=src --cov-report=term-missing
```

**Shorter version:**
```bash
# Just format and test
black src tests && pytest tests/ --cov=src
```

---

## 📊 Coverage Analysis

```bash
# Generate HTML report
pytest tests/ --cov=src --cov-report=html

# Open in browser (Linux)
xdg-open htmlcov/index.html

# Open in browser (macOS)
open htmlcov/index.html

# Require minimum coverage (fail if below threshold)
pytest tests/ --cov=src --cov-fail-under=70

# Coverage for specific module
pytest tests/ --cov=src/openproject_config_manager/discovery

# Coverage with branch coverage
pytest tests/ --cov=src --cov-branch
```

---

## 🧰 Using pytest-mock in Tests

```python
# Basic mock
def test_something(mocker):
    mock_obj = mocker.patch('module.ClassName')
    mock_obj.return_value = "mocked"
    
# Mock with side effects
def test_with_side_effect(mocker):
    mock_func = mocker.patch('module.function')
    mock_func.side_effect = [1, 2, 3]

# Spy on function
def test_spy(mocker):
    spy = mocker.spy(obj, 'method')
    obj.method()
    spy.assert_called_once()

# Use fixture
def test_with_fixture(mock_docker_client):
    # mock_docker_client is defined in conftest.py
    assert mock_docker_client.containers.list() == []
```

---

## 📝 Test Markers

```python
# In test files
@pytest.mark.unit
def test_fast_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_end_to_end():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

# Run tests by marker
pytest tests/ -m unit
pytest tests/ -m "unit or integration"
pytest tests/ -m "not slow"
```

---

## 🎯 Common Workflows

### **Quick Check Before Commit**
```bash
black src tests --check && pytest tests/ -x
```

### **Full Quality Check**
```bash
black src tests && \
isort src tests --profile black && \
flake8 src tests --count && \
pytest tests/ --cov=src --cov-fail-under=70
```

### **Watch Tests (requires pytest-watch)**
```bash
pip install pytest-watch
ptw tests/ -- --cov=src
```

### **Generate Coverage Badge**
```bash
pytest tests/ --cov=src --cov-report=xml
# Upload coverage.xml to codecov.io
```

---

## 📈 Current Coverage Stats

**Overall:** 32% (2986 statements, 2029 missing)

**By Module:**
- ✅ `__init__.py` modules: 100%
- ✅ System discovery: 67%
- ✅ Network discovery: 62%
- ⚠️ Docker discovery: 15%
- ⚠️ Validator: 13%
- ⚠️ Config writer: 10%
- ❌ UI/Console: 0%

**Target:** 70% overall coverage

---

## 🔧 Configuration Files

- **pyproject.toml** - pytest, black, isort, coverage config
- **tests/conftest.py** - shared fixtures and test utilities
- **.coverage** - coverage data (generated, git-ignored)
- **htmlcov/** - HTML coverage reports (generated, git-ignored)

---

## 📚 Learn More

- pytest docs: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- black: https://black.readthedocs.io/
- flake8: https://flake8.pycqa.org/
- isort: https://pycqa.github.io/isort/

---

**Last Updated:** October 15, 2025  
**Status:** All tooling integrated and working ✅
