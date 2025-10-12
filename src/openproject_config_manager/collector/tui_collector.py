#!/usr/bin/env python3
"""
OpenProject Configuration Collector using TUI Form Engine

This module integrates the TUI Form Engine to collect user configuration
and then validates/transforms it for deployment.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any

# Import the lightweight TUI Form Engine renderer (end-user interface)
from tui_form_engine.renderer import FormRenderer
from tui_form_engine.core.exceptions import FlowValidationError, FlowExecutionError

from ..core.config import Configuration
from ..core.manager import ConfigurationManager


class OpenProjectConfigCollector:
    """
    Collects OpenProject configuration using TUI Form Engine flows.
    
    Workflow:
    1. Load YAML flow definition (input schema)
    2. Execute flow with TUI Form Engine (collect user input)
    3. Save raw user responses 
    4. Validate and transform responses using ConfigurationManager
    5. Output final configuration for deploy-manager
    """
    
    def __init__(self, flows_dir: str = None, output_dir: str = "output"):
        # Use collector directory for flows if not specified
        if flows_dir is None:
            flows_dir = Path(__file__).parent
        
        self.flows_dir = Path(flows_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize TUI Form Renderer (end-user interface)
        self.renderer = FormRenderer()
        
        # Initialize Config Manager for validation
        self.config_manager = ConfigurationManager()
    
    def collect_configuration(
        self, 
        flow_name: str = "openproject_main_config",
        mock_responses: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute the full configuration collection workflow.
        
        Args:
            flow_name: Name of the flow YAML file (without .yml extension)
            mock_responses: Optional mock responses for testing
            
        Returns:
            Dict containing the final validated configuration
            
        Raises:
            FlowValidationError: If flow definition is invalid
            FlowExecutionError: If flow execution fails
            ValueError: If configuration validation fails
        """
        print(f"🎯 Starting OpenProject configuration collection...")
        
        # Step 1: Execute TUI flow to collect user input using renderer
        print(f"📋 Executing flow: {flow_name}")
        try:
            flow_path = self.flows_dir / f"{flow_name}.yml"
            flow_response = self.renderer.render_flow(
                flow_path=str(flow_path),
                mock_responses=mock_responses,
                quiet=False
            )
            user_responses = flow_response["responses"]
        except (FlowValidationError, FlowExecutionError) as e:
            print(f"❌ Flow execution failed: {e}")
            raise
        
        # Step 2: Save raw user responses
        responses_file = self.output_dir / f"{flow_name}_responses.json"
        with open(responses_file, 'w') as f:
            json.dump(user_responses, f, indent=2)
        print(f"💾 User responses saved: {responses_file}")
        
        # Step 3: Validate and transform using ConfigurationManager
        print(f"🔍 Validating configuration...")
        try:
            # Convert responses to Configuration object
            config = self._transform_responses_to_config(user_responses)
            
            # Validate using ConfigurationManager
            validation_result = self.config_manager.validate_configuration(config)
            
            if not validation_result.is_valid:
                print(f"❌ Configuration validation failed:")
                for error in validation_result.errors:
                    print(f"  - {error}")
                raise ValueError("Configuration validation failed")
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            raise
        
        # Step 4: Generate final configuration for deploy-manager
        final_config = self._generate_deploy_config(config, user_responses)
        
        # Step 5: Save final configuration
        config_file = self.output_dir / f"openproject_config.json"
        with open(config_file, 'w') as f:
            json.dump(final_config, f, indent=2)
        print(f"✅ Final configuration saved: {config_file}")
        
        print(f"🎉 Configuration collection complete!")
        return final_config
    
    def _transform_responses_to_config(self, responses: Dict[str, Any]) -> Configuration:
        """Transform user responses to Configuration object."""
        # Map flow responses to Configuration fields
        config_data = {
            # Basic project settings
            'project_name': responses.get('project', {}).get('name', 'openproject'),
            'admin_email': responses.get('admin', {}).get('email'),
            
            # Database configuration
            'database': {
                'type': responses.get('database', {}).get('type', 'postgresql'),
                'host': responses.get('database', {}).get('host', 'localhost'),
                'port': responses.get('database', {}).get('port', 5432),
                'name': responses.get('database', {}).get('name', 'openproject'),
                'username': responses.get('database', {}).get('username', 'openproject'),
                'password': responses.get('database', {}).get('password'),
            },
            
            # Network configuration
            'network': {
                'domain': responses.get('network', {}).get('domain'),
                'ssl_enabled': responses.get('network', {}).get('ssl_enabled', True),
                'port': responses.get('network', {}).get('port', 80),
            },
            
            # Add more mappings as needed...
        }
        
        return Configuration(**config_data)
    
    def _generate_deploy_config(self, config: Configuration, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final configuration for deploy-manager."""
        return {
            'metadata': {
                'generated_by': 'openproject-config-manager',
                'timestamp': str(Path().resolve()),
                'flow_version': '1.0.0'
            },
            'openproject': {
                'project_name': config.project_name,
                'admin_email': config.admin_email,
                'database': config.database,
                'network': config.network,
                # Include any additional validated configuration
            },
            'deployment': {
                'docker_compose_template': 'openproject-standard',
                'environment_files': [
                    'openproject.env',
                    'database.env'
                ],
                'volumes': [
                    'openproject_data',
                    'openproject_logs'
                ]
            },
            # Raw responses for reference/debugging
            '_raw_responses': responses
        }
    
    def test_flow(self, flow_name: str, mock_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Test flow execution with mock responses (for development/CI)."""
        print(f"🧪 Testing flow: {flow_name}")
        
        try:
            # Execute flow with mocks using renderer
            flow_path = self.flows_dir / f"{flow_name}.yml"
            flow_response = self.renderer.render_flow(
                flow_path=str(flow_path),
                mock_responses=mock_responses,
                quiet=True
            )
            result = flow_response["responses"]
            
            # Validate the result
            config = self._transform_responses_to_config(result)
            final_config = self._generate_deploy_config(config, result)
            
            print(f"✅ Flow test successful")
            return final_config
            
        except Exception as e:
            print(f"❌ Flow test failed: {e}")
            raise


def main():
    """Main entry point for interactive configuration collection."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="OpenProject Configuration Collector")
    parser.add_argument("flow_name", nargs="?", default="openproject_main_config", 
                       help="Name of the flow to execute")
    parser.add_argument("--mock-file", help="Path to JSON file with mock responses")
    
    args = parser.parse_args()
    
    # Load mock responses if provided
    mock_responses = None
    if args.mock_file:
        try:
            with open(args.mock_file, 'r') as f:
                mock_responses = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load mock file: {e}")
            return 1
    
    collector = OpenProjectConfigCollector()
    
    try:
        # Configuration collection (interactive or mocked)
        config = collector.collect_configuration(args.flow_name, mock_responses)
        
        print(f"\n🎉 Configuration collection complete!")
        print(f"📁 Files generated:")
        print(f"  - User responses: output/{args.flow_name}_responses.json")
        print(f"  - Final config: output/openproject_config.json")
        print(f"\n✅ Ready for deployment with deploy-manager!")
        
    except Exception as e:
        print(f"\n❌ Configuration collection failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())