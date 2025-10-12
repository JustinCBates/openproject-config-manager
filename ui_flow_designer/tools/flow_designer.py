#!/usr/bin/env python3
"""
Interactive Flow Designer Tool
Create and edit YAML flows using Questionary interface.
"""

import questionary
from questionary import Style
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import sys
from datetime import datetime


class InteractiveFlowDesigner:
    """Interactive tool for designing and editing YAML flows."""
    
    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        self.flows_dir.mkdir(exist_ok=True)
        
        self.style = Style([
            ('question', 'bold blue'),
            ('answer', 'fg:#ff9d00 bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
            ('selected', 'fg:#cc5454'),
            ('instruction', 'italic'),
            ('separator', 'fg:#888888'),
        ])
        
        # Available step types and their configurations
        self.step_types = {
            'text': {
                'name': 'Text Input',
                'description': 'Single line text input with optional validation',
                'required_fields': ['id', 'message'],
                'optional_fields': ['default', 'instruction', 'validate']
            },
            'select': {
                'name': 'Single Selection',
                'description': 'Choose one option from a list',
                'required_fields': ['id', 'message', 'choices'],
                'optional_fields': ['default', 'instruction']
            },
            'confirm': {
                'name': 'Yes/No Confirmation',
                'description': 'Boolean confirmation prompt',
                'required_fields': ['id', 'message'],
                'optional_fields': ['default', 'instruction']
            },
            'computed': {
                'name': 'Computed Value',
                'description': 'Calculate value from other responses',
                'required_fields': ['id', 'compute'],
                'optional_fields': ['when']
            }
        }
        
        self.validators = [
            'not_empty',
            'domain_name', 
            'email_address',
            'positive_integer',
            'port_number',
            'uri_namespace'
        ]
    
    def run(self):
        """Run the interactive flow designer."""
        questionary.print("\n🎨 Interactive Flow Designer", style="bold blue")
        questionary.print("   Design and edit YAML flows using an interactive interface\n")
        
        while True:
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Create New Flow",
                    "Edit Existing Flow", 
                    "Test Flow",
                    "List All Flows",
                    "Validate Flow",
                    "Exit"
                ],
                style=self.style
            ).ask()
            
            if action == "Create New Flow":
                self.create_new_flow()
            elif action == "Edit Existing Flow":
                self.edit_existing_flow()
            elif action == "Test Flow":
                self.test_flow()
            elif action == "List All Flows":
                self.list_flows()
            elif action == "Validate Flow":
                self.validate_flow()
            elif action == "Exit":
                questionary.print("👋 Goodbye!", style="bold green")
                break
    
    def create_new_flow(self):
        """Create a new flow interactively."""
        questionary.print("\n✨ Creating New Flow", style="bold green")
        
        # Get basic flow information
        flow_id = questionary.text(
            "Flow ID (filename without .yml):",
            instruction="Use lowercase with underscores, e.g., 'user_config'",
            validate=lambda x: len(x) > 0 and x.replace('_', '').isalnum()
        ).ask()
        
        if not flow_id:
            return
        
        title = questionary.text(
            "Flow Title:",
            instruction="Human-readable title for the flow"
        ).ask()
        
        description = questionary.text(
            "Description (optional):",
            default=""
        ).ask()
        
        icon = questionary.text(
            "Icon (emoji, optional):",
            default="🔧"
        ).ask()
        
        # Create basic flow structure
        flow_def = {
            'title': title or flow_id.replace('_', ' ').title(),
            'description': description,
            'icon': icon,
            'steps': []
        }
        
        # Add steps
        questionary.print(f"\n📝 Adding steps to '{flow_def['title']}'")
        self.add_steps_to_flow(flow_def)
        
        # Configure output mapping
        if questionary.confirm("Configure output mapping?", default=False).ask():
            self.configure_output_mapping(flow_def)
        
        # Save flow
        self.save_flow(flow_id, flow_def)
        questionary.print(f"✅ Flow '{flow_id}' created successfully!", style="bold green")
    
    def add_steps_to_flow(self, flow_def: Dict[str, Any]):
        """Add steps to a flow interactively."""
        while True:
            if questionary.confirm("Add a step?", default=True).ask():
                step = self.create_step()
                if step:
                    flow_def['steps'].append(step)
                    questionary.print(f"   ➕ Added step: {step['id']}", style="green")
            else:
                break
    
    def create_step(self) -> Optional[Dict[str, Any]]:
        """Create a single step interactively."""
        step_type = questionary.select(
            "Step type:",
            choices=[
                questionary.Choice(
                    title=f"{info['name']} - {info['description']}", 
                    value=step_type
                ) for step_type, info in self.step_types.items()
            ]
        ).ask()
        
        if not step_type:
            return None
        
        step_info = self.step_types[step_type]
        step = {'type': step_type}
        
        # Get required fields
        for field in step_info['required_fields']:
            value = self.get_field_value(field, step_type, required=True)
            if value is not None:
                step[field] = value
            else:
                return None  # User cancelled
        
        # Get optional fields
        for field in step_info['optional_fields']:
            if questionary.confirm(f"Add {field}?", default=False).ask():
                value = self.get_field_value(field, step_type, required=False)
                if value is not None:
                    step[field] = value
        
        return step
    
    def get_field_value(self, field: str, step_type: str, required: bool = True) -> Any:
        """Get value for a specific field."""
        if field == 'id':
            return questionary.text(
                "Step ID:",
                instruction="Unique identifier for this step",
                validate=lambda x: len(x) > 0 if required else True
            ).ask()
        
        elif field == 'message':
            return questionary.text(
                "Question/Message:",
                instruction="The prompt shown to the user"
            ).ask()
        
        elif field == 'choices':
            choices = []
            questionary.print("Add choices (enter empty to finish):")
            while True:
                choice = questionary.text("Choice:").ask()
                if choice:
                    choices.append(choice)
                else:
                    break
            return choices if choices else None
        
        elif field == 'default':
            return questionary.text(
                "Default value:",
                default=""
            ).ask()
        
        elif field == 'instruction':
            return questionary.text(
                "Instruction (help text):",
                default=""
            ).ask()
        
        elif field == 'validate':
            return questionary.select(
                "Validation:",
                choices=self.validators
            ).ask()
        
        elif field == 'compute':
            return questionary.text(
                "Compute expression:",
                instruction="e.g., 'discovered_data.environment.RAILS_ENV'"
            ).ask()
        
        elif field == 'when':
            return questionary.text(
                "When condition:",
                instruction="e.g., 'response_id == \"value\"'"
            ).ask()
        
        return None
    
    def edit_existing_flow(self):
        """Edit an existing flow."""
        flows = self.get_available_flows()
        if not flows:
            questionary.print("❌ No flows found", style="red")
            return
        
        flow_id = questionary.select(
            "Select flow to edit:",
            choices=flows
        ).ask()
        
        if not flow_id:
            return
        
        flow_def = self.load_flow(flow_id)
        if not flow_def:
            return
        
        questionary.print(f"\n✏️  Editing Flow: {flow_def.get('title', flow_id)}", style="bold blue")
        
        while True:
            action = questionary.select(
                "What would you like to edit?",
                choices=[
                    "Basic Information (title, description, icon)",
                    "Add Step",
                    "Edit Step",
                    "Remove Step",
                    "Reorder Steps",
                    "Output Mapping",
                    "Save and Exit",
                    "Cancel"
                ]
            ).ask()
            
            if action == "Basic Information (title, description, icon)":
                self.edit_basic_info(flow_def)
            elif action == "Add Step":
                step = self.create_step()
                if step:
                    flow_def['steps'].append(step)
            elif action == "Edit Step":
                self.edit_step(flow_def)
            elif action == "Remove Step":
                self.remove_step(flow_def)
            elif action == "Reorder Steps":
                self.reorder_steps(flow_def)
            elif action == "Output Mapping":
                self.configure_output_mapping(flow_def)
            elif action == "Save and Exit":
                self.save_flow(flow_id, flow_def)
                questionary.print(f"✅ Flow '{flow_id}' saved successfully!", style="bold green")
                break
            elif action == "Cancel":
                break
    
    def edit_basic_info(self, flow_def: Dict[str, Any]):
        """Edit basic flow information."""
        flow_def['title'] = questionary.text(
            "Title:", 
            default=flow_def.get('title', '')
        ).ask()
        
        flow_def['description'] = questionary.text(
            "Description:", 
            default=flow_def.get('description', '')
        ).ask()
        
        flow_def['icon'] = questionary.text(
            "Icon:", 
            default=flow_def.get('icon', '🔧')
        ).ask()
    
    def edit_step(self, flow_def: Dict[str, Any]):
        """Edit a specific step."""
        steps = flow_def.get('steps', [])
        if not steps:
            questionary.print("❌ No steps to edit", style="red")
            return
        
        step_choices = [
            f"{i+1}. {step.get('id', 'unnamed')} ({step.get('type', 'unknown')})"
            for i, step in enumerate(steps)
        ]
        
        choice = questionary.select(
            "Select step to edit:",
            choices=step_choices
        ).ask()
        
        if choice:
            step_index = int(choice.split('.')[0]) - 1
            step = steps[step_index]
            
            # For now, just recreate the step
            questionary.print("Current step will be recreated. Current values:")
            questionary.print(yaml.dump(step, default_flow_style=False))
            
            new_step = self.create_step()
            if new_step:
                steps[step_index] = new_step
    
    def remove_step(self, flow_def: Dict[str, Any]):
        """Remove a step from the flow."""
        steps = flow_def.get('steps', [])
        if not steps:
            questionary.print("❌ No steps to remove", style="red")
            return
        
        step_choices = [
            f"{i+1}. {step.get('id', 'unnamed')} ({step.get('type', 'unknown')})"
            for i, step in enumerate(steps)
        ]
        
        choice = questionary.select(
            "Select step to remove:",
            choices=step_choices
        ).ask()
        
        if choice:
            step_index = int(choice.split('.')[0]) - 1
            removed_step = steps.pop(step_index)
            questionary.print(f"✅ Removed step: {removed_step.get('id', 'unnamed')}", style="green")
    
    def configure_output_mapping(self, flow_def: Dict[str, Any]):
        """Configure output mapping for the flow."""
        questionary.print("\n🗂️  Configuring Output Mapping")
        questionary.print("   Map step responses to final output structure")
        
        steps = flow_def.get('steps', [])
        if not steps:
            questionary.print("❌ No steps available for mapping", style="red")
            return
        
        output_mapping = flow_def.get('output_mapping', {})
        
        for step in steps:
            step_id = step.get('id')
            if not step_id or step.get('type') == 'computed':
                continue
            
            current_mapping = output_mapping.get(step_id, step_id)
            
            new_mapping = questionary.text(
                f"Map '{step_id}' to:",
                default=current_mapping,
                instruction="Use dot notation for nested keys, e.g., 'database.host'"
            ).ask()
            
            if new_mapping:
                output_mapping[step_id] = new_mapping
        
        if output_mapping:
            flow_def['output_mapping'] = output_mapping
    
    def test_flow(self):
        """Test a flow by executing it."""
        flows = self.get_available_flows()
        if not flows:
            questionary.print("❌ No flows found", style="red")
            return
        
        flow_id = questionary.select(
            "Select flow to test:",
            choices=flows
        ).ask()
        
        if not flow_id:
            return
        
        questionary.print(f"\n🧪 Testing Flow: {flow_id}", style="bold blue")
        
        # Import the FlowEngine to test
        try:
            sys.path.append(str(Path(__file__).parent.parent))
            from engine.flow_engine import FlowEngine
            
            engine = FlowEngine(flows_dir=str(self.flows_dir))
            
            # Execute the flow
            result = engine.execute_flow(flow_id)
            
            questionary.print("\n✅ Flow execution completed!", style="bold green")
            questionary.print("📊 Results:")
            questionary.print(yaml.dump(result, default_flow_style=False))
            
        except Exception as e:
            questionary.print(f"❌ Flow execution failed: {e}", style="red")
    
    def validate_flow(self):
        """Validate a flow definition."""
        flows = self.get_available_flows()
        if not flows:
            questionary.print("❌ No flows found", style="red")
            return
        
        flow_id = questionary.select(
            "Select flow to validate:",
            choices=flows
        ).ask()
        
        if not flow_id:
            return
        
        flow_def = self.load_flow(flow_id)
        if not flow_def:
            return
        
        questionary.print(f"\n✅ Validating Flow: {flow_id}", style="bold blue")
        
        errors = []
        warnings = []
        
        # Basic validation
        if not flow_def.get('title'):
            errors.append("Missing title")
        
        if not flow_def.get('steps'):
            errors.append("No steps defined")
        
        # Step validation
        step_ids = set()
        for i, step in enumerate(flow_def.get('steps', [])):
            step_id = step.get('id')
            if not step_id:
                errors.append(f"Step {i+1}: Missing id")
            elif step_id in step_ids:
                errors.append(f"Step {i+1}: Duplicate id '{step_id}'")
            else:
                step_ids.add(step_id)
            
            step_type = step.get('type')
            if step_type not in self.step_types:
                errors.append(f"Step {step_id}: Invalid type '{step_type}'")
            else:
                # Check required fields
                required_fields = self.step_types[step_type]['required_fields']
                for field in required_fields:
                    if field not in step:
                        errors.append(f"Step {step_id}: Missing required field '{field}'")
        
        # Report results
        if errors:
            questionary.print("❌ Validation Errors:", style="red")
            for error in errors:
                questionary.print(f"   • {error}")
        
        if warnings:
            questionary.print("⚠️  Warnings:", style="yellow")
            for warning in warnings:
                questionary.print(f"   • {warning}")
        
        if not errors and not warnings:
            questionary.print("✅ Flow validation passed!", style="green")
    
    def list_flows(self):
        """List all available flows."""
        flows = self.get_available_flows()
        if not flows:
            questionary.print("❌ No flows found", style="red")
            return
        
        questionary.print(f"\n📋 Available Flows ({len(flows)}):", style="bold blue")
        
        for flow_id in flows:
            flow_def = self.load_flow(flow_id)
            if flow_def:
                title = flow_def.get('title', flow_id)
                description = flow_def.get('description', '')
                icon = flow_def.get('icon', '🔧')
                step_count = len(flow_def.get('steps', []))
                
                questionary.print(f"   {icon} {title}")
                questionary.print(f"      ID: {flow_id}")
                if description:
                    questionary.print(f"      Description: {description}")
                questionary.print(f"      Steps: {step_count}")
                questionary.print("")
    
    def get_available_flows(self) -> List[str]:
        """Get list of available flow files."""
        if not self.flows_dir.exists():
            return []
        
        flows = []
        for flow_file in self.flows_dir.glob("*.yml"):
            flows.append(flow_file.stem)
        return sorted(flows)
    
    def load_flow(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Load a flow definition."""
        flow_path = self.flows_dir / f"{flow_id}.yml"
        if not flow_path.exists():
            questionary.print(f"❌ Flow file not found: {flow_path}", style="red")
            return None
        
        try:
            with open(flow_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            questionary.print(f"❌ Error loading flow: {e}", style="red")
            return None
    
    def save_flow(self, flow_id: str, flow_def: Dict[str, Any]):
        """Save a flow definition."""
        flow_path = self.flows_dir / f"{flow_id}.yml"
        
        # Add metadata
        metadata = {
            'created': datetime.now().isoformat(),
            'version': '1.0'
        }
        flow_def['metadata'] = metadata
        
        try:
            with open(flow_path, 'w') as f:
                yaml.dump(flow_def, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            questionary.print(f"❌ Error saving flow: {e}", style="red")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive Flow Designer")
    parser.add_argument(
        '--flows-dir', 
        default='flows',
        help='Directory containing flow definitions (default: flows)'
    )
    
    args = parser.parse_args()
    
    designer = InteractiveFlowDesigner(flows_dir=args.flows_dir)
    designer.run()


if __name__ == "__main__":
    main()