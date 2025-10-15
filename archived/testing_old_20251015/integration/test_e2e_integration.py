#!/usr/bin/env python3
"""
End-to-end test for ConfigurationManager with FlowEngine.
This test simulates the discovery and interactive collection phases.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the source directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from openproject_config_manager.core.manager import ConfigurationManager


def test_discovery_phase():
    """Test the discovery phase works with QuestionaryUI."""
    print("Testing discovery phase...")
    
    try:
        manager = ConfigurationManager()
        
        # Mock the discovery methods to avoid actual system scanning
        manager.env_discovery.discover = MagicMock(return_value={
            'SECRET_KEY_BASE': 'test_secret',
            'RAILS_ENV': 'development'
        })
        
        manager.system_discovery.discover = MagicMock(return_value={
            'platform': 'linux',
            'memory_gb': 8,
            'cpu_cores': 4
        })
        
        manager.docker_discovery.discover = MagicMock(return_value={
            'containers': [],
            'networks': [],
            'volumes': []
        })
        
        # Run discovery
        discovered = manager.run_discovery_phase()
        
        print("✅ Discovery phase completed successfully")
        print(f"   Environment vars: {len(discovered.get('environment', {}))}")
        print(f"   System info: {len(discovered.get('system', {}))}")
        print(f"   Docker info: {len(discovered.get('docker', {}))}")
        
        return True, discovered
        
    except Exception as e:
        print(f"❌ Error in discovery phase: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def test_flow_execution():
    """Test that we can execute a single flow."""
    print("\nTesting single flow execution...")
    
    try:
        manager = ConfigurationManager()
        
        # Test executing the core configuration flow with mock variables
        test_variables = {
            'discovered_data': {
                'environment': {'RAILS_ENV': 'development'},
                'system': {'memory_gb': 8}
            }
        }
        
        # Mock questionary to avoid actual user input
        with patch('questionary.select') as mock_select, \
             patch('questionary.text') as mock_text, \
             patch('questionary.confirm') as mock_confirm, \
             patch('questionary.print') as mock_print:
            
            # Setup mock responses
            mock_select.return_value.ask.return_value = 'development'
            mock_text.return_value.ask.return_value = 'redis'
            mock_confirm.return_value.ask.return_value = True
            
            # Execute the core configuration flow
            try:
                result = manager.flow_engine.execute_flow('core_configuration', context=test_variables)
                print("✅ Flow execution completed")
                print(f"   Result type: {type(result)}")
                return True
                
            except Exception as flow_error:
                print(f"❌ Flow execution failed: {flow_error}")
                return False
                
    except Exception as e:
        print(f"❌ Error setting up flow test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ConfigurationManager End-to-End Integration Test")
    print("=" * 60)
    
    # Test discovery phase
    discovery_success, discovered_data = test_discovery_phase()
    
    # Test flow execution
    flow_success = test_flow_execution()
    
    print("\n" + "=" * 60)
    if discovery_success and flow_success:
        print("🎉 All end-to-end tests passed!")
        print("✅ ConfigurationManager + FlowEngine integration is working")
        sys.exit(0)
    else:
        print("❌ Some end-to-end tests failed.")
        sys.exit(1)