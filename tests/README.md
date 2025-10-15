# Config Manager Test Suite

Comprehensive test suite aligned with `control_flows.yml` architecture.

## 📁 Structure

```
tests/
├── unit/              # Fast unit tests (no external dependencies)
│   ├── libraries/     # Library unit tests (11 units, 39 tests)
│   └── steps/         # Individual step unit tests
│
├── integration/       # Integration tests (multiple components)
│   ├── phases/        # Phase orchestrator tests (14 tests)
│   ├── steps/         # Step integration tests
│   └── flows/         # Flow integration tests
│
├── e2e/               # End-to-end tests (full workflows, 13 tests)
│
├── fixtures/          # Shared test data
│   ├── shared/        # Common fixtures
│   └── phase_N/       # Phase-specific fixtures
│
└── conftest.py        # Pytest configuration
```

## 🏃 Running Tests

```bash
# All tests
pytest tests/

# By type
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/e2e/            # End-to-end tests only

# Specific test file
pytest tests/unit/libraries/test_probing.py
```

## 📋 Test-to-Architecture Mapping

| Architecture Level | Test Location |
|-------------------|---------------|
| Library Units | `tests/unit/libraries/` |
| Phase Steps | `tests/integration/steps/` |
| Phase Orchestrators | `tests/integration/phases/` |
| Flows | `tests/integration/flows/` |
| Complete Pipeline | `tests/e2e/` |

## ✍️ Writing New Tests

**Follow this decision tree:**

1. Testing a library unit? → `tests/unit/libraries/test_{library_name}.py`
2. Testing a phase step? → `tests/integration/steps/test_phase_{N}_steps.py`
3. Testing a phase orchestrator? → `tests/integration/phases/test_phase_orchestrators.py`
4. Testing a complete flow? → `tests/integration/flows/test_{flow_name}.py`
5. Testing end-to-end? → `tests/e2e/test_{workflow_name}.py`

**NEVER create test directories adjacent to code!**

See `TEST_CONSOLIDATION_PROPOSAL.md` for full guidelines.
