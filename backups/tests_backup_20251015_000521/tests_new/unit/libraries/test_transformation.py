"""
Unit tests for transformation library classes.
Tests transformation units can be instantiated and have required methods.
"""
import pytest
from pathlib import Path
from phases.libraries.transformation import DefaultsTransformer


class TestDefaultsTransformer:
    """Test DefaultsTransformer unit."""
    
    def test_can_instantiate(self):
        """DefaultsTransformer should be instantiable with project_root."""
        transformer = DefaultsTransformer(project_root=Path("/tmp/test"))
        assert transformer is not None
    
    def test_has_transform_method(self):
        """DefaultsTransformer should have transform_enhanced_defaults method."""
        transformer = DefaultsTransformer(project_root=Path("/tmp/test"))
        assert hasattr(transformer, 'transform_enhanced_defaults')
        assert callable(getattr(transformer, 'transform_enhanced_defaults'))
