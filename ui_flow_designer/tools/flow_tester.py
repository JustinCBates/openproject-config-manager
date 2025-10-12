#!/usr/bin/env python3
"""
Flow Testing Tool
Test YAML flows with mock data and automated responses.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import json
import sys
from unittest.mock import patch, MagicMock


class FlowTester:
    """Tool for testing flows with automated responses."""
    
    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        
        # Default mock responses for different question types
        self.default_responses = {
            'text': 'test_value',
            'select': None,  # Will use first choice
            'confirm': True,
        }
        
        # Common test contexts
        self.test_contexts = {
            'development': {
                'discovered_data': {
                    'environment': {
                        'RAILS_ENV': 'development',
                        'SECRET_KEY_BASE': 'dev_secret_key'
                    },
                    'system': {
                        'platform': 'linux',
                        'memory_gb': 8,
                        'cpu_cores': 4
                    },
                    'docker': {
                        'containers': [],
                        'networks': [],
                        'volumes': []
                    }
                }
            },
            'production': {
                'discovered_data': {
                    'environment': {
                        'RAILS_ENV': 'production',
                        'SECRET_KEY_BASE': 'prod_secret_key'
                    },
                    'system': {
                        'platform': 'linux',
                        'memory_gb': 32,
                        'cpu_cores': 8
                    },
                    'docker': {
                        'containers': [
                            {'image': 'postgres:13', 'name': 'db'}
                        ],
                        'networks': ['openproject_default'],
                        'volumes': ['db_data']
                    }
                }
            }
        }
    
    def load_flow(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Load a flow definition."""
        flow_path = self.flows_dir / f"{flow_id}.yml"
        if not flow_path.exists():
            print(f"❌ Flow file not found: {flow_path}")
            return None
        
        try:
            with open(flow_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading flow: {e}")
            return None
    
    def create_mock_responses(self, flow_def: Dict[str, Any], custom_responses: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create mock responses for all steps in a flow."""
        custom_responses = custom_responses or {}
        responses = {}
        
        for step in flow_def.get('steps', []):
            step_id = step.get('id')
            step_type = step.get('type')
            
            if not step_id or step_type == 'computed':
                continue
            
            # Use custom response if provided
            if step_id in custom_responses:
                responses[step_id] = custom_responses[step_id]
                continue
            
            # Generate default response based on step type
            if step_type == 'text':
                default = step.get('default', self.default_responses['text'])
                responses[step_id] = default if default else f"test_{step_id}"
            
            elif step_type == 'select':
                choices = step.get('choices', [])
                if choices:
                    default = step.get('default')
                    if default and default in choices:
                        responses[step_id] = default
                    else:
                        responses[step_id] = choices[0]
                else:
                    responses[step_id] = 'test_choice'
            
            elif step_type == 'confirm':
                default = step.get('default', self.default_responses['confirm'])
                responses[step_id] = default
        
        return responses
    
    def test_flow(self, flow_id: str, context: Dict[str, Any] = None, custom_responses: Dict[str, Any] = None, verbose: bool = False) -> Optional[Dict[str, Any]]:
        """Test a flow with mock responses."""
        flow_def = self.load_flow(flow_id)
        if not flow_def:
            return None
        
        context = context or self.test_contexts['development']
        mock_responses = self.create_mock_responses(flow_def, custom_responses)
        
        if verbose:
            print(f"🧪 Testing flow: {flow_def.get('title', flow_id)}")
            print(f"📝 Mock responses: {json.dumps(mock_responses, indent=2)}")
            print()
        
        try:
            # Import FlowEngine
            sys.path.append(str(self.flows_dir.parent))
            from engine.flow_engine import FlowEngine
            
            # Create mock questionary functions
            def mock_text_ask():
                current_step = getattr(mock_text_ask, 'current_step', None)
                if current_step and current_step in mock_responses:
                    return mock_responses[current_step]
                return 'mock_text_response'
            
            def mock_select_ask():
                current_step = getattr(mock_select_ask, 'current_step', None)
                if current_step and current_step in mock_responses:
                    return mock_responses[current_step]
                return 'mock_select_response'
            
            def mock_confirm_ask():
                current_step = getattr(mock_confirm_ask, 'current_step', None)
                if current_step and current_step in mock_responses:
                    return mock_responses[current_step]
                return True
            
            # Mock questionary with our responses
            with patch('questionary.text') as mock_text, \
                 patch('questionary.select') as mock_select, \
                 patch('questionary.confirm') as mock_confirm, \
                 patch('questionary.print') as mock_print:
                
                # Track which step we're on
                step_tracker = {'current_step': None}
                
                def create_mock_question(question_type, responses_dict):
                    """Create a mock question that returns appropriate response."""
                    mock_question = MagicMock()
                    
                    def ask_method():
                        # Find the current step based on the call stack or step tracking
                        for step in flow_def.get('steps', []):
                            step_id = step.get('id')
                            if step_id in responses_dict:
                                response = responses_dict[step_id]
                                if verbose:
                                    print(f"   {step_id} -> {response}")
                                return response
                        
                        # Fallback
                        if question_type == 'text':
                            return 'fallback_text'
                        elif question_type == 'select':
                            return 'fallback_choice'
                        elif question_type == 'confirm':
                            return True
                    
                    mock_question.ask = ask_method
                    return mock_question
                
                # Setup mocks
                mock_text.return_value = create_mock_question('text', mock_responses)
                mock_select.return_value = create_mock_question('select', mock_responses)
                mock_confirm.return_value = create_mock_question('confirm', mock_responses)
                
                # Execute flow
                engine = FlowEngine(flows_dir=str(self.flows_dir))
                result = engine.execute_flow(flow_id, context=context)
                
                if verbose:
                    print(f"✅ Flow execution completed")
                    print(f"📊 Result: {json.dumps(result, indent=2)}")
                
                return result
                
        except Exception as e:
            print(f"❌ Flow execution failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return None
    
    def test_all_flows(self, context_name: str = 'development', verbose: bool = False) -> Dict[str, bool]:
        """Test all flows in the directory."""
        if not self.flows_dir.exists():
            print(f"❌ Flows directory does not exist: {self.flows_dir}")
            return {}
        
        flow_files = list(self.flows_dir.glob("*.yml"))
        if not flow_files:
            print("❌ No flow files found")
            return {}
        
        context = self.test_contexts.get(context_name, self.test_contexts['development'])
        results = {}
        
        print(f"🧪 Testing {len(flow_files)} flows with '{context_name}' context...")
        print()
        
        for flow_file in flow_files:
            flow_id = flow_file.stem
            print(f"Testing {flow_id}...")
            
            result = self.test_flow(flow_id, context=context, verbose=verbose)
            success = result is not None
            results[flow_id] = success
            
            if success:
                print(f"   ✅ Passed")
            else:
                print(f"   ❌ Failed")
            
            print()
        
        return results
    
    def create_test_scenario(self, flow_id: str, scenario_name: str, custom_responses: Dict[str, Any], context: Dict[str, Any] = None):
        """Create and save a test scenario for a flow."""
        scenario = {
            'flow_id': flow_id,
            'name': scenario_name,
            'context': context or self.test_contexts['development'],
            'responses': custom_responses,
            'created': 'auto-generated'
        }
        
        scenarios_dir = self.flows_dir / 'test_scenarios'
        scenarios_dir.mkdir(exist_ok=True)
        
        scenario_file = scenarios_dir / f"{flow_id}_{scenario_name}.json"
        with open(scenario_file, 'w') as f:
            json.dump(scenario, f, indent=2)
        
        print(f"✅ Test scenario saved: {scenario_file}")
    
    def run_test_scenario(self, scenario_file: Path, verbose: bool = False) -> bool:
        """Run a saved test scenario."""
        try:
            with open(scenario_file, 'r') as f:
                scenario = json.load(f)
        except Exception as e:
            print(f"❌ Error loading scenario: {e}")
            return False
        
        flow_id = scenario.get('flow_id')
        context = scenario.get('context')
        responses = scenario.get('responses')
        
        print(f"🎬 Running scenario: {scenario.get('name', 'unnamed')}")
        
        result = self.test_flow(flow_id, context=context, custom_responses=responses, verbose=verbose)
        return result is not None
    
    def generate_test_scenarios(self, flow_id: str):
        """Generate common test scenarios for a flow."""
        flow_def = self.load_flow(flow_id)
        if not flow_def:
            return
        
        print(f"🏭 Generating test scenarios for {flow_id}...")
        
        # Scenario 1: All defaults
        default_responses = self.create_mock_responses(flow_def)
        self.create_test_scenario(flow_id, 'defaults', default_responses)
        
        # Scenario 2: Production context
        prod_responses = self.create_mock_responses(flow_def)
        self.create_test_scenario(flow_id, 'production', prod_responses, self.test_contexts['production'])
        
        # Scenario 3: Edge cases (empty strings, extreme values)
        edge_responses = {}
        for step in flow_def.get('steps', []):
            step_id = step.get('id')
            step_type = step.get('type')
            
            if step_type == 'text':
                edge_responses[step_id] = ''  # Empty string
            elif step_type == 'select':
                choices = step.get('choices', [])
                if choices:
                    edge_responses[step_id] = choices[-1]  # Last choice
            elif step_type == 'confirm':
                edge_responses[step_id] = False  # Negative response
        
        if edge_responses:
            self.create_test_scenario(flow_id, 'edge_cases', edge_responses)
        
        print(f"✅ Generated scenarios for {flow_id}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test YAML flows with mock data")
    parser.add_argument(
        '--flows-dir',
        default='flows',
        help='Directory containing flow definitions'
    )
    parser.add_argument(
        '--flow',
        help='Test specific flow by ID'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Test all flows'
    )
    parser.add_argument(
        '--context',
        choices=['development', 'production'],
        default='development',
        help='Test context to use'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--generate-scenarios',
        help='Generate test scenarios for specified flow'
    )
    parser.add_argument(
        '--run-scenario',
        help='Run a specific test scenario file'
    )
    
    args = parser.parse_args()
    
    tester = FlowTester(flows_dir=args.flows_dir)
    
    if args.generate_scenarios:
        tester.generate_test_scenarios(args.generate_scenarios)
    
    elif args.run_scenario:
        scenario_file = Path(args.run_scenario)
        success = tester.run_test_scenario(scenario_file, verbose=args.verbose)
        sys.exit(0 if success else 1)
    
    elif args.flow:
        result = tester.test_flow(args.flow, verbose=args.verbose)
        sys.exit(0 if result else 1)
    
    elif args.all:
        results = tester.test_all_flows(context_name=args.context, verbose=args.verbose)
        failed_count = sum(1 for success in results.values() if not success)
        
        print("📊 Test Summary:")
        print(f"   Total flows: {len(results)}")
        print(f"   Passed: {len(results) - failed_count}")
        print(f"   Failed: {failed_count}")
        
        sys.exit(1 if failed_count > 0 else 0)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()