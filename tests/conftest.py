"""
Pytest configuration and shared fixtures for config-manager tests.
"""

import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest

# Project root for fixtures
project_root = Path(__file__).parent.parent

# NOTE: sys.path.insert is required here because the phases/ directory
# is intentionally structured at project root (not inside src/) for modularity.
# Tests need to import from 'phases.*' which requires project_root in sys.path.
# This is a legitimate architectural decision, not a hack.
sys.path.insert(0, str(project_root))


# ============================================================================
# Path Fixtures
# ============================================================================


@pytest.fixture
def project_root_path():
    """Return the project root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def test_data_dir(project_root_path):
    """Return the test data directory path."""
    return project_root_path / "tests" / "fixtures" / "data"


# ============================================================================
# Mock Fixtures (for pytest-mock integration)
# ============================================================================


@pytest.fixture
def mock_docker_client(mocker):
    """Create a mock Docker client for testing."""
    mock_client = mocker.MagicMock()
    mock_client.containers.list.return_value = []
    mock_client.images.list.return_value = []
    return mock_client


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config_file = tmp_path / "test_config.json"
    config_file.write_text('{"test": "value"}')
    return config_file


# ============================================================================
# Coverage Configuration (applied via pytest-cov)
# ============================================================================
# Coverage is configured in pyproject.toml:
#   [tool.pytest.ini_options]
#   addopts = ["--cov-report=term-missing", "--cov-report=html"]
#
# Run tests with coverage:
#   pytest tests/ --cov=src
#
# Generate HTML coverage report:
#   pytest tests/ --cov=src --cov-report=html
#   open htmlcov/index.html
# ============================================================================


# ============================================================================
# Test Markers Reference
# ============================================================================
# @pytest.mark.unit        - Fast unit tests
# @pytest.mark.integration - Integration tests requiring multiple components
# @pytest.mark.e2e         - End-to-end workflow tests
# @pytest.mark.slow        - Slow running tests
# @pytest.mark.ui          - UI component tests
# ============================================================================
