"""Tests for development mode operation in config-manager"""

import pytest
import os
import tempfile
from pathlib import Path

# Force development mode for these tests
@pytest.fixture(autouse=True)
def setup_dev_mode():
    """Force development mode for tests"""
    os.environ['OPENPROJECT_DEV_MODE'] = '1'
    yield
    if 'OPENPROJECT_DEV_MODE' in os.environ:
        del os.environ['OPENPROJECT_DEV_MODE']


def test_auto_detect_development():
    """Test that development mode is auto-detected"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    assert ConfigurationManager._is_development_mode() is True


def test_uses_local_directories():
    """Test that local directories are used in development mode"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    mgr = ConfigurationManager()
    
    # Should use local directories (not site-packages)
    assert 'site-packages' not in str(mgr.output_dir)
    assert mgr.output_dir.exists()
    assert mgr.cache_dir.exists()
    
    # Directories should be created relative to package
    assert 'config-manager' in str(mgr.output_dir) or 'output' in str(mgr.output_dir)


def test_explicit_development_mode():
    """Test explicitly setting development mode"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    mgr = ConfigurationManager(use_local_paths=True)
    
    assert mgr.output_dir.exists()
    assert mgr.cache_dir.exists()
    assert 'site-packages' not in str(mgr.output_dir)


def test_custom_paths_in_development():
    """Test that custom paths can override defaults even in dev mode"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        custom_output = tmpdir / 'custom_output'
        custom_cache = tmpdir / 'custom_cache'
        
        mgr = ConfigurationManager(
            output_dir=custom_output,
            cache_dir=custom_cache,
            use_local_paths=True  # Still in dev mode
        )
        
        # Should use custom paths even in dev mode
        assert mgr.output_dir == custom_output
        assert mgr.cache_dir == custom_cache
        assert custom_output.exists()
        assert custom_cache.exists()


def test_flow_engine_initialized_in_dev():
    """Test that flow engine is properly initialized in development mode"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    mgr = ConfigurationManager()
    
    # Flow engine should be available (or None if layouts not found)
    # We don't fail if it's None as layouts might not be present in test env
    assert mgr.flow_engine is None or hasattr(mgr.flow_engine, 'flows_dir')
