#!/usr/bin/env python3
"""
Phase 5 Integration Test
Test all interactive design tools together.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add tools to path
tools_path = Path(__file__).parent
sys.path.insert(0, str(tools_path))

from flow_validator import FlowValidator
from flow_tester import FlowTester
from flow_designer import InteractiveFlowDesigner


def test_validation_tool():
    """Test the flow validation tool."""
    print("🔍 Testing Flow Validator...")
    
    validator = FlowValidator()
    flows_dir = Path("../flows")
    
    if not flows_dir.exists():
        print("❌ Flows directory not found")
        return False
    
    results = validator.validate_directory(flows_dir)
    
    # Check that we found flows
    flow_count = len([k for k in results.keys() if k != "_directory_"])
    if flow_count == 0:
        print("❌ No flows found to validate")
        return False
    
    print(f"✅ Validated {flow_count} flows")
    
    # Check for critical errors
    total_errors = sum(len(errors) for errors, warnings in results.values())
    if total_errors > 0:
        print(f"⚠️  Found {total_errors} validation errors")
    else:
        print("✅ No validation errors found")
    
    return True


def test_testing_tool():
    """Test the flow testing tool."""
    print("\n🧪 Testing Flow Tester...")
    
    tester = FlowTester(flows_dir="../flows")
    
    # Test a specific flow
    result = tester.test_flow('core_configuration', verbose=False)
    if result is None:
        print("❌ Flow test failed")
        return False
    
    print("✅ Single flow test passed")
    
    # Test all flows
    results = tester.test_all_flows(verbose=False)
    if not results:
        print("❌ No flows tested")
        return False
    
    failed_count = sum(1 for success in results.values() if not success)
    passed_count = len(results) - failed_count
    
    print(f"✅ Tested {len(results)} flows: {passed_count} passed, {failed_count} failed")
    
    return failed_count == 0


def test_designer_tool():
    """Test the interactive flow designer tool."""
    print("\n🎨 Testing Flow Designer...")
    
    designer = InteractiveFlowDesigner("../flows")
    
    # Test flow listing
    flows = designer.get_available_flows()
    if not flows:
        print("❌ No flows found")
        return False
    
    print(f"✅ Found {len(flows)} flows")
    
    # Test flow loading
    for flow_id in flows[:2]:  # Test first 2 flows
        flow_def = designer.load_flow(flow_id)
        if not flow_def:
            print(f"❌ Failed to load flow: {flow_id}")
            return False
        
        # Basic validation
        if 'title' not in flow_def or 'steps' not in flow_def:
            print(f"❌ Invalid flow structure: {flow_id}")
            return False
    
    print("✅ Flow loading and basic validation passed")
    
    return True


def test_create_new_flow():
    """Test creating a new flow (without user interaction)."""
    print("\n✨ Testing Flow Creation...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_flows_dir = Path(temp_dir) / "test_flows"
        temp_flows_dir.mkdir()
        
        designer = InteractiveFlowDesigner(str(temp_flows_dir))
        
        # Create a test flow definition
        test_flow = {
            'title': 'Test Flow',
            'description': 'A test flow for validation',
            'icon': '🧪',
            'steps': [
                {
                    'type': 'text',
                    'id': 'test_input',
                    'message': 'Enter test value:'
                },
                {
                    'type': 'select',
                    'id': 'test_choice',
                    'message': 'Choose option:',
                    'choices': ['option1', 'option2']
                }
            ],
            'output_mapping': {
                'test_input': 'input_value',
                'test_choice': 'selected_option'
            }
        }
        
        # Save the test flow
        designer.save_flow('test_flow', test_flow)
        
        # Verify it was saved
        saved_flows = designer.get_available_flows()
        if 'test_flow' not in saved_flows:
            print("❌ Failed to save test flow")
            return False
        
        # Load and verify
        loaded_flow = designer.load_flow('test_flow')
        if not loaded_flow or loaded_flow['title'] != 'Test Flow':
            print("❌ Failed to load saved flow correctly")
            return False
        
        print("✅ Flow creation and saving test passed")
        
        # Test validation on the new flow
        validator = FlowValidator()
        flow_path = temp_flows_dir / "test_flow.yml"
        errors, warnings = validator.validate_flow_file(flow_path)
        
        if errors:
            print(f"❌ Created flow has validation errors: {errors}")
            return False
        
        print("✅ Created flow passes validation")
        
        # Test execution of the new flow
        tester = FlowTester(flows_dir=str(temp_flows_dir))
        result = tester.test_flow('test_flow', verbose=False)
        
        if result is None:
            print("❌ Created flow failed execution test")
            return False
        
        print("✅ Created flow passes execution test")
    
    return True


def test_integration():
    """Test integration between all tools."""
    print("\n🔗 Testing Tool Integration...")
    
    # This tests that all tools can work with the same flow directory
    flows_dir = Path("../flows")
    
    # 1. Validate flows
    validator = FlowValidator()
    validation_results = validator.validate_directory(flows_dir)
    
    # 2. Test flows that passed validation
    tester = FlowTester(flows_dir=str(flows_dir))
    valid_flows = [
        flow_id for flow_id, (errors, warnings) in validation_results.items() 
        if not errors and flow_id != "_directory_"
    ]
    
    if not valid_flows:
        print("❌ No valid flows to test")
        return False
    
    # 3. Test each valid flow
    test_results = {}
    for flow_id in valid_flows:
        result = tester.test_flow(flow_id, verbose=False)
        test_results[flow_id] = result is not None
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"✅ Integration test: {passed_tests}/{total_tests} flows passed end-to-end")
    
    return passed_tests > 0


def main():
    """Run all Phase 5 integration tests."""
    print("=" * 60)
    print("Phase 5: Interactive Design Tools - Integration Test")
    print("=" * 60)
    
    tests = [
        ("Validation Tool", test_validation_tool),
        ("Testing Tool", test_testing_tool),
        ("Designer Tool", test_designer_tool),
        ("Flow Creation", test_create_new_flow),
        ("Tool Integration", test_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = success
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Phase 5 Integration Test Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 5 integration tests passed!")
        print("✅ Interactive Design Tools are working correctly")
        return True
    else:
        print("❌ Some Phase 5 tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)