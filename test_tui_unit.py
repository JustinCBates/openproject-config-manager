#!/usr/bin/env python3
"""
Test TUI Form Caller Unit

Demonstrates using the TUI Form Caller unit in Phase 3.
"""

import sys
from pathlib import Path

# Add phases to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from phases.libraries.interactive import TUIFormCaller


def test_tui_caller_with_mock():
    """Test TUI Form Caller with mock responses."""
    print("=" * 70)
    print("Testing TUI Form Caller Unit")
    print("=" * 70)
    print()
    
    # Initialize the unit
    caller = TUIFormCaller()
    print("✅ TUI Form Caller initialized")
    print()
    
    # Prepare test data
    config_manager_root = Path(__file__).parent
    layout_path = config_manager_root / "src/openproject_config_manager/collector/layouts/test_layouts/config_tui_minimal.layout.yml"
    defaults_path = config_manager_root / "phases/phase_2_tui_mapping/outputs/tui/tui_defaults.yml"
    output_path = config_manager_root / "phases/phase_3_collection/outputs/test_responses.json"
    
    # Mock responses for testing (simulates user input)
    mock_responses = {
        "project_name": "test-project",
        "admin_email": "admin@test.com",
        "admin_password": "TestPassword123",
        "domain": "test.example.com"
    }
    
    print(f"📋 Layout: {layout_path.name}")
    print(f"📊 Defaults: {defaults_path.name if defaults_path.exists() else 'None'}")
    print(f"🤖 Using mock responses (test mode)")
    print()
    
    try:
        # Execute form with unit
        responses = caller.execute_form(
            layout_path=str(layout_path),
            defaults_path=str(defaults_path) if defaults_path.exists() else None,
            output_path=str(output_path),
            mock_responses=mock_responses,
            quiet=False
        )
        
        print()
        print(f"✅ Form executed successfully!")
        print(f"📦 Collected {len(responses)} responses")
        print()
        
        # Display responses
        print("Responses:")
        for key, value in responses.items():
            # Mask password
            display_value = "********" if "password" in key.lower() else value
            print(f"  {key}: {display_value}")
        
        print()
        print("=" * 70)
        print("🎉 Unit Test PASSED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ Unit Test FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False


def test_load_layout():
    """Test loading layout file."""
    print()
    print("=" * 70)
    print("Testing Layout Loading")
    print("=" * 70)
    print()
    
    caller = TUIFormCaller()
    config_manager_root = Path(__file__).parent
    layout_path = config_manager_root / "src/openproject_config_manager/collector/layouts/test_layouts/config_tui_minimal.layout.yml"
    
    try:
        layout = caller.load_layout(str(layout_path))
        print(f"✅ Layout loaded successfully")
        print(f"   Layout ID: {layout.get('layout_id')}")
        print(f"   Title: {layout.get('title')}")
        print(f"   Steps: {len(layout.get('steps', []))}")
        print()
        return True
    except Exception as e:
        print(f"❌ Failed to load layout: {e}")
        return False


if __name__ == "__main__":
    print("\n")
    
    # Test 1: Load layout
    test1_passed = test_load_layout()
    
    # Test 2: Execute with mock
    test2_passed = test_tui_caller_with_mock()
    
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"  Load Layout: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  Execute Form: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print()
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
