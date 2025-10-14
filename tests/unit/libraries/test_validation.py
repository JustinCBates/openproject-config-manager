"""
Unit tests for validation library classes.
Tests validation units can be instantiated and have required methods.
"""
import pytest
from phases.libraries.validation import SchemaValidator, DependencyValidator, EnvironmentValidator


class TestSchemaValidator:
    """Test SchemaValidator unit."""
    
    def test_can_instantiate(self):
        """SchemaValidator should be instantiable."""
        validator = SchemaValidator()
        assert validator is not None
    
    def test_has_validate_method(self):
        """SchemaValidator should have validate method."""
        validator = SchemaValidator()
        assert hasattr(validator, 'validate')
        assert callable(getattr(validator, 'validate'))


class TestDependencyValidator:
    """Test DependencyValidator unit."""
    
    def test_can_instantiate(self):
        """DependencyValidator should be instantiable."""
        validator = DependencyValidator()
        assert validator is not None
    
    def test_has_validate_method(self):
        """DependencyValidator should have validate method."""
        validator = DependencyValidator()
        assert hasattr(validator, 'validate')
        assert callable(getattr(validator, 'validate'))


class TestEnvironmentValidator:
    """Test EnvironmentValidator unit."""
    
    def test_can_instantiate(self):
        """EnvironmentValidator should be instantiable."""
        validator = EnvironmentValidator()
        assert validator is not None
    
    def test_has_validate_method(self):
        """EnvironmentValidator should have validate method."""
        validator = EnvironmentValidator()
        assert hasattr(validator, 'validate')
        assert callable(getattr(validator, 'validate'))
