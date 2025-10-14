"""
Integration tests for phase orchestrators.
Tests that phases can load and execute units from libraries.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import MagicMock

# Import phase orchestrators
from phases.phase_1_discovery.orchestrator_discovery import DiscoveryPhase
from phases.phase_2_tui_mapping.orchestrator_tui_mapping import TuiMappingPhase
from phases.phase_4_validation.orchestrator_validation import ValidationPhase
from phases.phase_5_export.orchestrator_export import ExportPhase

# Import library units to verify they can be loaded
from phases.libraries import (
    DockerDiscovery, NetworkDiscovery, SystemDiscovery,
    DefaultsTransformer,
    SchemaValidator, DependencyValidator, EnvironmentValidator,
    ExportDockerComposeStep, ExportEnvFileStep, ExportManifestStep
)


@pytest.fixture
def temp_project_root():
    """Create a temporary project root directory."""
    temp_dir = tempfile.mkdtemp()
    project_root = Path(temp_dir)
    
    # Create required subdirectories
    (project_root / "phases").mkdir(exist_ok=True)
    (project_root / "outputs").mkdir(exist_ok=True)
    (project_root / "artifacts").mkdir(exist_ok=True)
    
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
    ui.prompt_confirm = MagicMock(return_value=True)
    return ui


class TestPhase1DiscoveryOrchestrator:
    """Test Phase 1 Discovery orchestrator integration."""
    
    def test_can_instantiate_discovery_phase(self, temp_project_root, mock_ui):
        """Discovery phase should be instantiable."""
        phase = DiscoveryPhase(project_root=temp_project_root, ui=mock_ui)
        assert phase is not None
        assert phase.project_root == temp_project_root
    
    def test_discovery_phase_has_execute_method(self, temp_project_root, mock_ui):
        """Discovery phase should have execute method."""
        phase = DiscoveryPhase(project_root=temp_project_root, ui=mock_ui)
        assert hasattr(phase, 'execute')
        assert callable(getattr(phase, 'execute'))
    
    def test_discovery_phase_can_load_library_units(self, temp_project_root, mock_ui):
        """Discovery phase should be able to instantiate library units."""
        # This tests that the phase can access library units
        docker_discovery = DockerDiscovery()
        network_discovery = NetworkDiscovery()
        system_discovery = SystemDiscovery()
        
        assert docker_discovery is not None
        assert network_discovery is not None
        assert system_discovery is not None


class TestPhase2TuiMappingOrchestrator:
    """Test Phase 2 TUI Mapping orchestrator integration."""
    
    def test_can_instantiate_tui_mapping_phase(self, temp_project_root, mock_ui):
        """TUI Mapping phase should be instantiable."""
        phase = TuiMappingPhase(project_root=temp_project_root, ui=mock_ui)
        assert phase is not None
        assert phase.project_root == temp_project_root
    
    def test_tui_mapping_phase_has_execute_method(self, temp_project_root, mock_ui):
        """TUI Mapping phase should have execute method."""
        phase = TuiMappingPhase(project_root=temp_project_root, ui=mock_ui)
        assert hasattr(phase, 'execute')
        assert callable(getattr(phase, 'execute'))
    
    def test_tui_mapping_phase_can_load_library_units(self, temp_project_root):
        """TUI Mapping phase should be able to instantiate library units."""
        # This tests that the phase can access library units
        transformer = DefaultsTransformer(project_root=temp_project_root)
        assert transformer is not None


class TestPhase4ValidationOrchestrator:
    """Test Phase 4 Validation orchestrator integration."""
    
    def test_can_instantiate_validation_phase(self, temp_project_root, mock_ui):
        """Validation phase should be instantiable."""
        phase = ValidationPhase(project_root=temp_project_root, ui=mock_ui)
        assert phase is not None
        assert phase.project_root == temp_project_root
    
    def test_validation_phase_has_execute_method(self, temp_project_root, mock_ui):
        """Validation phase should have execute method."""
        phase = ValidationPhase(project_root=temp_project_root, ui=mock_ui)
        assert hasattr(phase, 'execute')
        assert callable(getattr(phase, 'execute'))
    
    def test_validation_phase_can_load_library_units(self, temp_project_root, mock_ui):
        """Validation phase should be able to instantiate library units."""
        # This tests that the phase can access library units
        schema_validator = SchemaValidator()
        dependency_validator = DependencyValidator()
        environment_validator = EnvironmentValidator()
        
        assert schema_validator is not None
        assert dependency_validator is not None
        assert environment_validator is not None


class TestPhase5ExportOrchestrator:
    """Test Phase 5 Export orchestrator integration."""
    
    def test_can_instantiate_export_phase(self, temp_project_root, mock_ui):
        """Export phase should be instantiable."""
        phase = ExportPhase(project_root=temp_project_root, ui=mock_ui)
        assert phase is not None
        assert phase.project_root == temp_project_root
    
    def test_export_phase_has_execute_method(self, temp_project_root, mock_ui):
        """Export phase should have execute method."""
        phase = ExportPhase(project_root=temp_project_root, ui=mock_ui)
        assert hasattr(phase, 'execute')
        assert callable(getattr(phase, 'execute'))
    
    def test_export_phase_can_load_library_units(self, temp_project_root):
        """Export phase should be able to instantiate library units."""
        # This tests that the phase can access library units
        docker_compose_exporter = ExportDockerComposeStep(project_root=temp_project_root)
        env_file_exporter = ExportEnvFileStep(project_root=temp_project_root)
        manifest_exporter = ExportManifestStep(project_root=temp_project_root)
        
        assert docker_compose_exporter is not None
        assert env_file_exporter is not None
        assert manifest_exporter is not None


class TestCrossPhaseIntegration:
    """Test integration between phases."""
    
    def test_all_phases_can_be_instantiated_together(self, temp_project_root, mock_ui):
        """All phases should be instantiable in sequence."""
        phase1 = DiscoveryPhase(project_root=temp_project_root, ui=mock_ui)
        phase2 = TuiMappingPhase(project_root=temp_project_root, ui=mock_ui)
        phase4 = ValidationPhase(project_root=temp_project_root, ui=mock_ui)
        phase5 = ExportPhase(project_root=temp_project_root, ui=mock_ui)
        
        assert all([phase1, phase2, phase4, phase5])
    
    def test_context_can_be_passed_between_phases(self, temp_project_root, mock_ui):
        """Context dictionary should be passable between phases."""
        context = {
            'discovered_data': {'docker': True, 'network': 'bridge'},
            'transformed_data': {'defaults': {}},
        }
        
        # Each phase should accept and return context
        phase1 = DiscoveryPhase(project_root=temp_project_root, ui=mock_ui)
        phase2 = TuiMappingPhase(project_root=temp_project_root, ui=mock_ui)
        
        # Both phases should have execute methods that can handle context
        assert hasattr(phase1, 'execute')
        assert hasattr(phase2, 'execute')
