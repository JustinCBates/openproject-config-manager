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
        flow_name: str = "layouts/config_tui.layout",
        mock_responses: Dict[str, Any] = None,
        skip_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the full configuration collection workflow.
        
        Args:
            flow_name: Name of the flow YAML file (without .yml extension)
            mock_responses: Optional mock responses for testing
            skip_validation: Skip configuration validation (useful for testing)
            
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
        
        # Step 3: Validate and transform using ConfigurationManager (optional)
        if skip_validation:
            print(f"⚠️  Skipping configuration validation...")
            # Create a simple config structure for deploy-manager
            final_config = self._generate_simple_deploy_config(user_responses)
        else:
            print(f"🔍 Validating configuration...")
            try:
                # Convert responses to Configuration object
                config = self._transform_responses_to_config(user_responses)
                
                # Validate using ConfigurationManager
                validation_result = self.config_manager.validator.validate_configuration(config)
                
                if not validation_result.is_valid:
                    print(f"❌ Configuration validation failed:")
                    for error in validation_result.errors:
                        print(f"  - {error}")
                    raise ValueError("Configuration validation failed")
                
                # Step 4: Generate final configuration for deploy-manager
                final_config = self._generate_deploy_config(config, user_responses)
                
            except Exception as e:
                print(f"❌ Configuration validation failed: {e}")
                raise
        
        # Step 5: Save final configuration
        config_file = self.output_dir / f"openproject_config.json"
        with open(config_file, 'w') as f:
            json.dump(final_config, f, indent=2)
        print(f"✅ Final configuration saved: {config_file}")
        
        print(f"🎉 Configuration collection complete!")
        return final_config
    
    def _transform_responses_to_config(self, responses: Dict[str, Any]) -> Configuration:
        """Transform user responses to Configuration object."""
        import secrets
        
        # Generate required fields that weren't collected in the form
        secret_key_base = secrets.token_hex(64)  # Generate 128-character hex string
        
        # Extract data from nested response structure
        project = responses.get('project', {})
        admin = responses.get('admin', {})
        database = responses.get('database', {})
        network = responses.get('network', {})
        email = responses.get('email', {})
        smtp = email.get('smtp', {})
        storage = responses.get('storage', {})
        repositories = responses.get('repositories', {})
        resources = responses.get('resources', {})
        backup = responses.get('backup', {})
        monitoring = responses.get('monitoring', {})
        
        # Map to Configuration model structure
        config_data = {
            # Required core settings
            'secret_key_base': secret_key_base,
            'rails_env': project.get('environment', 'production'),
            
            # Database configuration
            'database': {
                'adapter': database.get('type', 'postgresql'),
                'host': 'db' if database.get('setup') == 'container' else database.get('host', 'localhost'),
                'port': 5432 if database.get('type') == 'postgresql' else 3306,
                'name': project.get('name', 'openproject'),
                'username': 'openproject',
                'password': admin.get('password', 'changeme123'),  # Use admin password as db password for container setup
            },
            
            # Proxy configuration
            'proxy': {
                'domain': network.get('domain', 'localhost'),
                'ssl_enabled': True,  # Default to enabled
                'lets_encrypt': True,  # Default to Let's Encrypt
                'lets_encrypt_email': admin.get('email'),
            },
            
            # Storage configuration
            'storage': {
                'data_volume': f"{project.get('name', 'openproject')}_data",
                'logs_volume': f"{project.get('name', 'openproject')}_logs",
                'backup_enabled': backup.get('enabled', True),
                'backup_retention_days': int(backup.get('retention_days', 30)),
            },
            
            # Email configuration
            'email_delivery_method': email.get('delivery_method', 'smtp'),
            'smtp_address': smtp.get('host'),
            'smtp_port': int(smtp.get('port', 587)),
            'smtp_domain': network.get('domain'),
            'smtp_user_name': smtp.get('username'),
            'smtp_password': smtp.get('password'),
            'smtp_enable_starttls_auto': smtp.get('encryption') == 'starttls',
            
            # Performance settings from resources
            'web_concurrency': int(resources.get('worker_processes', 2)),
            
            # Logging
            'log_level': monitoring.get('log_level', 'info'),
            
            # Security settings
            'force_ssl': network.get('domain') != 'localhost',
            'session_cookie_secure': network.get('domain') != 'localhost',
        }
        
        return Configuration(**config_data)
    
    def _generate_simple_deploy_config(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple configuration for deploy-manager without full validation."""
        from datetime import datetime
        
        project = responses.get('project', {})
        
        return {
            'metadata': {
                'generated_by': 'openproject-config-manager',
                'timestamp': datetime.now().isoformat(),
                'flow_version': '1.0.0',
                'validation_skipped': True
            },
            'openproject': {
                'project_name': project.get('name', 'openproject'),
                'environment': project.get('environment', 'development'),
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
            '_raw_responses': responses,
            '_note': 'Configuration generated without validation - suitable for testing only'
        }
    
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
    parser.add_argument("flow_name", nargs="?", default="layouts/config_tui.layout", 
                       help="Name of the flow to execute (default: layouts/config_tui.layout)")
    parser.add_argument("--mock-file", help="Path to JSON file with mock responses")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip configuration validation (useful for testing layouts)")
    
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
        config = collector.collect_configuration(
            args.flow_name, 
            mock_responses,
            skip_validation=args.skip_validation
        )
        
        print(f"\n🎉 Configuration collection complete!")
        print(f"📁 Files generated:")
        print(f"  - User responses: output/{args.flow_name}_responses.json")
        print(f"  - Final config: output/openproject_config.json")
        if args.skip_validation:
            print(f"⚠️  Note: Validation was skipped - configuration is for testing only")
        print(f"\n✅ Ready for deployment with deploy-manager!")
        
    except Exception as e:
        print(f"\n❌ Configuration collection failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())