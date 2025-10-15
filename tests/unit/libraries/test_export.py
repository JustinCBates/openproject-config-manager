"""
Unit tests for export library classes.
Tests export units can be instantiated and have required methods.
"""

from pathlib import Path

import pytest

from phases.libraries.export import (
    CfgWriter,
    ExportDockerComposeStep,
    ExportEnvFileStep,
    ExportManifestStep,
)


class TestExportDockerComposeStep:
    """Test ExportDockerComposeStep unit."""

    def test_can_instantiate(self):
        """ExportDockerComposeStep should be instantiable with project_root."""
        exporter = ExportDockerComposeStep(project_root=Path("/tmp/test"))
        assert exporter is not None

    def test_has_export_method(self):
        """ExportDockerComposeStep should have execute method."""
        exporter = ExportDockerComposeStep(project_root=Path("/tmp/test"))
        assert hasattr(exporter, "execute")
        assert callable(getattr(exporter, "execute"))


class TestExportEnvFileStep:
    """Test ExportEnvFileStep unit."""

    def test_can_instantiate(self):
        """ExportEnvFileStep should be instantiable with project_root."""
        exporter = ExportEnvFileStep(project_root=Path("/tmp/test"))
        assert exporter is not None

    def test_has_export_method(self):
        """ExportEnvFileStep should have execute method."""
        exporter = ExportEnvFileStep(project_root=Path("/tmp/test"))
        assert hasattr(exporter, "execute")
        assert callable(getattr(exporter, "execute"))


class TestExportManifestStep:
    """Test ExportManifestStep unit."""

    def test_can_instantiate(self):
        """ExportManifestStep should be instantiable with project_root."""
        exporter = ExportManifestStep(project_root=Path("/tmp/test"))
        assert exporter is not None

    def test_has_export_method(self):
        """ExportManifestStep should have execute method."""
        exporter = ExportManifestStep(project_root=Path("/tmp/test"))
        assert hasattr(exporter, "execute")
        assert callable(getattr(exporter, "execute"))


class TestCfgWriter:
    """Test CfgWriter unit."""

    def test_can_instantiate(self):
        """CfgWriter should be instantiable."""
        writer = CfgWriter()
        assert writer is not None

    def test_has_export_method(self):
        """CfgWriter should have write_configuration method."""
        writer = CfgWriter()
        # CfgWriter uses 'write_configuration' method
        assert hasattr(writer, "write_configuration")
        assert callable(getattr(writer, "write_configuration"))
