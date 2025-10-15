"""
Unit tests for probing library classes.
Tests individual discovery units can be instantiated and have required methods.
"""
import pytest
from phases.libraries.probing import DockerDiscovery, NetworkDiscovery, SystemDiscovery


class TestDockerDiscovery:
    """Test DockerDiscovery unit."""
    
    def test_can_instantiate(self):
        """DockerDiscovery should be instantiable."""
        discovery = DockerDiscovery()
        assert discovery is not None
    
    def test_has_discover_method(self):
        """DockerDiscovery should have discover method."""
        discovery = DockerDiscovery()
        assert hasattr(discovery, 'discover')
        assert callable(getattr(discovery, 'discover'))


class TestNetworkDiscovery:
    """Test NetworkDiscovery unit."""
    
    def test_can_instantiate(self):
        """NetworkDiscovery should be instantiable."""
        discovery = NetworkDiscovery()
        assert discovery is not None
    
    def test_has_discover_method(self):
        """NetworkDiscovery should have discover method."""
        discovery = NetworkDiscovery()
        assert hasattr(discovery, 'discover')
        assert callable(getattr(discovery, 'discover'))


class TestSystemDiscovery:
    """Test SystemDiscovery unit."""
    
    def test_can_instantiate(self):
        """SystemDiscovery should be instantiable."""
        discovery = SystemDiscovery()
        assert discovery is not None
    
    def test_has_discover_method(self):
        """SystemDiscovery should have discover method."""
        discovery = SystemDiscovery()
        assert hasattr(discovery, 'discover')
        assert callable(getattr(discovery, 'discover'))
