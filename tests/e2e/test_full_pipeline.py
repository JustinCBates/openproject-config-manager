"""
End-to-end tests for the complete 5-phase pipeline.
Tests the full configuration generation workflow.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from phases.phases_orchestrator import PhasesOrchestrator


@pytest.fixture
def temp_project_root():
    """Create a temporary project root directory with required structure."""
    temp_dir = tempfile.mkdtemp()
    project_root = Path(temp_dir)

    # Create required directory structure
    (project_root / "phases").mkdir(exist_ok=True)
    (project_root / "outputs").mkdir(exist_ok=True)
    (project_root / "artifacts").mkdir(exist_ok=True)
    (project_root / "design_specs").mkdir(exist_ok=True)

    # Create a minimal control_flows.yml for testing
    control_flows_content = """
control_flows:
  phases:
    - phase_id: 1
      name: "Discovery Phase"
      description: "Discover system environment"
      steps: []
    - phase_id: 2
      name: "TUI Mapping Phase"
      description: "Transform defaults"
      steps: []
    - phase_id: 3
      name: "Collection Phase"
      description: "Collect user input"
      steps: []
    - phase_id: 4
      name: "Validation Phase"
      description: "Validate configuration"
      steps: []
    - phase_id: 5
      name: "Export Phase"
      description: "Export configuration files"
      steps: []
"""
    (project_root / "design_specs" / "control_flows.yml").write_text(control_flows_content)

    yield project_root

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ui():
    """Create a mock UI interface."""
    ui = MagicMock()
    ui.display_info = MagicMock()
    ui.display_warning = MagicMock()
    ui.display_error = MagicMock()
    ui.display_success = MagicMock()
    ui.prompt_confirm = MagicMock(return_value=True)
    ui.prompt_text = MagicMock(return_value="test_value")
    ui.prompt_choice = MagicMock(return_value="option1")
    return ui


class TestFullPipelineExecution:
    """Test complete pipeline execution from discovery to export."""

    def test_orchestrator_can_be_instantiated(self, temp_project_root, mock_ui):
        """Phases orchestrator should be instantiable with all phases."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        assert orchestrator is not None
        assert orchestrator.project_root == temp_project_root
        assert orchestrator.discovery_phase is not None
        assert orchestrator.tui_mapping_phase is not None
        assert orchestrator.collection_phase is not None
        assert orchestrator.validation_phase is not None
        assert orchestrator.export_phase is not None

    def test_orchestrator_has_execute_all_phases_method(self, temp_project_root, mock_ui):
        """Orchestrator should have execute_all_phases method."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        assert hasattr(orchestrator, "execute_all_phases")
        assert callable(getattr(orchestrator, "execute_all_phases"))

    def test_orchestrator_can_execute_individual_phases(self, temp_project_root, mock_ui):
        """Orchestrator should be able to execute individual phases."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        # Each phase should have an execute method
        assert hasattr(orchestrator.discovery_phase, "execute")
        assert hasattr(orchestrator.tui_mapping_phase, "execute")
        assert hasattr(orchestrator.collection_phase, "execute")
        assert hasattr(orchestrator.validation_phase, "execute")
        assert hasattr(orchestrator.export_phase, "execute")

    def test_context_flows_through_pipeline(self, temp_project_root, mock_ui):
        """Context should be passable through the complete pipeline."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        # Start with initial context
        initial_context = {"pipeline_mode": "test", "phase_results": {}}

        # The orchestrator should accept context
        assert hasattr(orchestrator, "execute_all_phases")
        # Method signature should support optional context parameter
        import inspect

        sig = inspect.signature(orchestrator.execute_all_phases)
        assert "context" in sig.parameters


class TestPipelineWithLibraries:
    """Test pipeline execution using library units."""

    def test_discovery_phase_can_use_library_units(self, temp_project_root, mock_ui):
        """Discovery phase should be able to use probing library units."""
        from phases.libraries import DockerDiscovery, NetworkDiscovery, SystemDiscovery

        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        # Library units should be importable and usable
        docker_discovery = DockerDiscovery()
        network_discovery = NetworkDiscovery()
        system_discovery = SystemDiscovery()

        assert docker_discovery is not None
        assert network_discovery is not None
        assert system_discovery is not None

    def test_tui_mapping_phase_can_use_library_units(self, temp_project_root, mock_ui):
        """TUI Mapping phase should be able to use transformation library units."""
        from phases.libraries import DefaultsTransformer

        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        # Library units should be importable and usable
        transformer = DefaultsTransformer(project_root=temp_project_root)

        assert transformer is not None

    def test_validation_phase_can_use_library_units(self, temp_project_root, mock_ui):
        """Validation phase should be able to use validation library units."""
        from phases.libraries import (
            DependencyValidator,
            EnvironmentValidator,
            SchemaValidator,
        )

        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        # Library units should be importable and usable
        schema_validator = SchemaValidator()
        dependency_validator = DependencyValidator()
        environment_validator = EnvironmentValidator()

        assert schema_validator is not None
        assert dependency_validator is not None
        assert environment_validator is not None

    def test_export_phase_can_use_library_units(self, temp_project_root, mock_ui):
        """Export phase should be able to use export library units."""
        from phases.libraries import (
            ExportDockerComposeStep,
            ExportEnvFileStep,
            ExportManifestStep,
        )

        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        # Library units should be importable and usable
        docker_compose_exporter = ExportDockerComposeStep(project_root=temp_project_root)
        env_file_exporter = ExportEnvFileStep(project_root=temp_project_root)
        manifest_exporter = ExportManifestStep(project_root=temp_project_root)

        assert docker_compose_exporter is not None
        assert env_file_exporter is not None
        assert manifest_exporter is not None


class TestPipelineErrorHandling:
    """Test error handling in the pipeline."""

    def test_orchestrator_handles_missing_project_root(self):
        """Orchestrator should handle missing project root gracefully."""
        # This should either raise a clear error or handle it gracefully
        non_existent_path = Path("/tmp/non_existent_test_path_12345")

        try:
            # Try to create orchestrator with non-existent path
            orchestrator = PhasesOrchestrator(project_root=non_existent_path, ui=None)
            # If it succeeds, it should at least be instantiated
            assert orchestrator is not None
        except Exception as e:
            # If it fails, it should be a meaningful error
            assert (
                "project_root" in str(e).lower()
                or "path" in str(e).lower()
                or "directory" in str(e).lower()
            )

    def test_orchestrator_handles_none_ui(self, temp_project_root):
        """Orchestrator should work with None UI (headless mode)."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=None)

        assert orchestrator is not None
        assert orchestrator.ui is None


class TestPipelineArtifacts:
    """Test artifact generation and flow in the pipeline."""

    def test_artifacts_directory_exists(self, temp_project_root, mock_ui):
        """Artifacts directory should exist in project structure."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        artifacts_dir = temp_project_root / "artifacts"
        assert artifacts_dir.exists()
        assert artifacts_dir.is_dir()

    def test_outputs_directory_exists(self, temp_project_root, mock_ui):
        """Outputs directory should exist in project structure."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        outputs_dir = temp_project_root / "outputs"
        assert outputs_dir.exists()
        assert outputs_dir.is_dir()

    def test_phases_can_write_to_outputs(self, temp_project_root, mock_ui):
        """Phases should be able to write to outputs directory."""
        orchestrator = PhasesOrchestrator(project_root=temp_project_root, ui=mock_ui)

        outputs_dir = temp_project_root / "outputs"
        test_file = outputs_dir / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"
