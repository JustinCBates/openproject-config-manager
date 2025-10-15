"""
Test suite to validate library imports and class names.
This ensures __init__.py exports match actual class implementations.
"""

import inspect

import pytest


class TestProbingLibraryImports:
    """Test probing library exports match implementations."""

    def test_docker_discovery_import(self):
        """DockerDiscovery should be importable from probing library."""
        from phases.libraries.probing import DockerDiscovery

        assert inspect.isclass(DockerDiscovery)

    def test_network_discovery_import(self):
        """NetworkDiscovery should be importable from probing library."""
        from phases.libraries.probing import NetworkDiscovery

        assert inspect.isclass(NetworkDiscovery)

    def test_system_discovery_import(self):
        """SystemDiscovery should be importable from probing library."""
        from phases.libraries.probing import SystemDiscovery

        assert inspect.isclass(SystemDiscovery)

    def test_probing_all_exports(self):
        """Probing library __all__ should match actual exports."""
        import phases.libraries.probing as probing

        expected = ["DockerDiscovery", "NetworkDiscovery", "SystemDiscovery"]
        assert hasattr(probing, "__all__")
        assert set(probing.__all__) == set(expected)


class TestTransformationLibraryImports:
    """Test transformation library exports match implementations."""

    def test_defaults_transformer_import(self):
        """DefaultsTransformer should be importable from transformation library."""
        from phases.libraries.transformation import DefaultsTransformer

        assert inspect.isclass(DefaultsTransformer)

    def test_transformation_all_exports(self):
        """Transformation library __all__ should match actual exports."""
        import phases.libraries.transformation as transformation

        expected = ["DefaultsTransformer"]
        assert hasattr(transformation, "__all__")
        assert set(transformation.__all__) == set(expected)


class TestValidationLibraryImports:
    """Test validation library exports match implementations."""

    def test_schema_validator_import(self):
        """SchemaValidator should be importable from validation library."""
        from phases.libraries.validation import SchemaValidator

        assert inspect.isclass(SchemaValidator)

    def test_dependency_validator_import(self):
        """DependencyValidator should be importable from validation library."""
        from phases.libraries.validation import DependencyValidator

        assert inspect.isclass(DependencyValidator)

    def test_environment_validator_import(self):
        """EnvironmentValidator should be importable from validation library."""
        from phases.libraries.validation import EnvironmentValidator

        assert inspect.isclass(EnvironmentValidator)

    def test_validation_all_exports(self):
        """Validation library __all__ should match actual exports."""
        import phases.libraries.validation as validation

        expected = [
            "SchemaValidator",
            "DependencyValidator",
            "EnvironmentValidator",
            "SchemaValidationResult",
            "DependencyValidationResult",
            "EnvironmentValidationResult",
        ]
        assert hasattr(validation, "__all__")
        assert set(validation.__all__) == set(expected)


class TestExportLibraryImports:
    """Test export library exports match implementations."""

    def test_export_docker_compose_step_import(self):
        """ExportDockerComposeStep should be importable from export library."""
        from phases.libraries.export import ExportDockerComposeStep

        assert inspect.isclass(ExportDockerComposeStep)

    def test_export_env_file_step_import(self):
        """ExportEnvFileStep should be importable from export library."""
        from phases.libraries.export import ExportEnvFileStep

        assert inspect.isclass(ExportEnvFileStep)

    def test_export_manifest_step_import(self):
        """ExportManifestStep should be importable from export library."""
        from phases.libraries.export import ExportManifestStep

        assert inspect.isclass(ExportManifestStep)

    def test_cfg_writer_import(self):
        """CfgWriter should be importable from export library."""
        from phases.libraries.export import CfgWriter

        assert inspect.isclass(CfgWriter)

    def test_export_all_exports(self):
        """Export library __all__ should match actual exports."""
        import phases.libraries.export as export

        expected = [
            "ExportDockerComposeStep",
            "ExportEnvFileStep",
            "ExportManifestStep",
            "CfgWriter",
        ]
        assert hasattr(export, "__all__")
        assert set(export.__all__) == set(expected)


class TestTopLevelLibraryImports:
    """Test top-level libraries package exports all sub-libraries."""

    def test_all_libraries_exported(self):
        """Top-level libraries should export all 4 library domains."""
        import phases.libraries as libraries

        # Should be able to access all sub-libraries
        assert hasattr(libraries, "probing")
        assert hasattr(libraries, "transformation")
        assert hasattr(libraries, "validation")
        assert hasattr(libraries, "export")

    def test_can_import_from_top_level(self):
        """Should be able to import all classes from top-level libraries."""
        from phases.libraries import (
            CfgWriter,
            DefaultsTransformer,
            DependencyValidator,
            DockerDiscovery,
            EnvironmentValidator,
            ExportDockerComposeStep,
            ExportEnvFileStep,
            ExportManifestStep,
            NetworkDiscovery,
            SchemaValidator,
            SystemDiscovery,
        )

        # All should be classes
        for cls in [
            DockerDiscovery,
            NetworkDiscovery,
            SystemDiscovery,
            DefaultsTransformer,
            SchemaValidator,
            DependencyValidator,
            EnvironmentValidator,
            ExportDockerComposeStep,
            ExportEnvFileStep,
            ExportManifestStep,
            CfgWriter,
        ]:
            assert inspect.isclass(cls)
