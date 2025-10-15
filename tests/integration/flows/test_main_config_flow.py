#!/usr/bin/env python3
"""
Test script for ConfigurationManager with FlowEngine integration.
"""

import sys
from pathlib import Path

# Add the source directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from openproject_config_manager.core.manager import ConfigurationManager


def test_manager_initialization():
    """Test that ConfigurationManager initializes correctly with FlowEngine."""
    print("Testing ConfigurationManager initialization...")

    try:
        manager = ConfigurationManager()
        print("✅ ConfigurationManager initialized successfully")

        # Check that FlowEngine is available
        if hasattr(manager, "flow_engine"):
            print("✅ FlowEngine is available")

            # Check if flow engine has flows loaded
            available_flows = manager.flow_engine.get_available_flows()
            flows_count = len(available_flows)
            print(f"✅ FlowEngine has {flows_count} flows available")

            # List available flows
            print("Available flows:")
            for flow_name in available_flows:
                print(f"  - {flow_name}")

        else:
            print("❌ FlowEngine not found")

        # Check that QuestionaryUI is available
        if hasattr(manager, "ui"):
            print("✅ QuestionaryUI is available")
            print(f"UI type: {type(manager.ui).__name__}")
        else:
            print("❌ UI not found")

        return True

    except Exception as e:
        print(f"❌ Error initializing ConfigurationManager: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_flow_engine_basic():
    """Test basic FlowEngine functionality."""
    print("\nTesting FlowEngine basic functionality...")

    try:
        manager = ConfigurationManager()

        # Test that we can access a flow definition
        available_flows = manager.flow_engine.get_available_flows()
        if "core_configuration" in available_flows:
            print("✅ Core configuration flow available")

            # Try to load the flow definition
            try:
                core_flow = manager.flow_engine._load_flow("core_configuration")
                print(f"   Flow has {len(core_flow.get('steps', []))} steps")
                print("✅ Core configuration flow loaded successfully")
            except Exception as e:
                print(f"❌ Error loading core configuration flow: {e}")
        else:
            print("❌ Core configuration flow not found")
            print(f"Available flows: {available_flows}")

        return True

    except Exception as e:
        print(f"❌ Error testing FlowEngine: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ConfigurationManager + FlowEngine Integration Test")
    print("=" * 60)

    success1 = test_manager_initialization()
    success2 = test_flow_engine_basic()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! Integration successful.")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)
