"""Tests for production mode operation in config-manager"""

import pytest
import tempfile
from pathlib import Path


def test_production_mode_requires_output_dir():
    """Test that production mode requires output_dir parameter"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with pytest.raises(ValueError, match="output_dir required in production mode"):
        ConfigurationManager(use_local_paths=False)


def test_production_mode_with_paths():
    """Test production mode with provided paths"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / 'config'
        cache_dir = tmpdir / 'cache'
        
        mgr = ConfigurationManager(
            output_dir=output_dir,
            cache_dir=cache_dir,
            use_local_paths=False
        )
        
        # Should use provided paths
        assert mgr.output_dir == output_dir
        assert mgr.cache_dir == cache_dir
        assert output_dir.exists()
        assert cache_dir.exists()


def test_production_mode_cache_defaults_to_output():
    """Test that cache_dir defaults to output_dir/cache in production"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / 'config'
        
        mgr = ConfigurationManager(
            output_dir=output_dir,
            use_local_paths=False
        )
        
        # Cache should default to output_dir/cache
        assert mgr.cache_dir == output_dir / 'cache'
        assert mgr.cache_dir.exists()


def test_production_mode_project_root():
    """Test that project_root is derived from output_dir in production"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / 'workspace' / 'config'
        
        mgr = ConfigurationManager(
            output_dir=output_dir,
            use_local_paths=False
        )
        
        # project_root should be parent of output_dir
        assert mgr.project_root == output_dir.parent


def test_production_mode_all_paths_specified():
    """Test production mode with all paths explicitly specified"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / 'outputs'
        cache_dir = tmpdir / 'cache'
        flows_dir = tmpdir / 'flows'
        
        # Create flows dir (required for flow engine)
        flows_dir.mkdir(parents=True, exist_ok=True)
        
        mgr = ConfigurationManager(
            output_dir=output_dir,
            cache_dir=cache_dir,
            flows_dir=flows_dir,
            use_local_paths=False
        )
        
        assert mgr.output_dir == output_dir
        assert mgr.cache_dir == cache_dir
        assert mgr.flows_dir == flows_dir
        assert output_dir.exists()
        assert cache_dir.exists()


def test_enhanced_defaults_written_to_output_dir():
    """Test that enhanced defaults are written to output_dir"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / 'config'
        
        mgr = ConfigurationManager(
            output_dir=output_dir,
            use_local_paths=False
        )
        
        # Write enhanced defaults
        enhanced_defaults = {
            'domain': {'value': 'example.com', 'source': 'test'},
            'postgres_password': {'value': 'secret123', 'source': 'test'}
        }
        
        defaults_path = mgr._write_enhanced_defaults_file(enhanced_defaults)
        
        # Should be written to output_dir/discovery/
        assert output_dir.name in defaults_path
        assert Path(defaults_path).exists()
        assert 'discovery' in defaults_path


def test_production_without_flows_dir():
    """Test that production mode works without flows_dir (optional)"""
    from openproject_config_manager.core.manager import ConfigurationManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / 'config'
        
        # Should work without flows_dir (flow_engine will be None or use fallback)
        mgr = ConfigurationManager(
            output_dir=output_dir,
            use_local_paths=False
        )
        
        # Manager should initialize successfully
        assert mgr.output_dir == output_dir
        assert output_dir.exists()
