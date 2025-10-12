#!/usr/bin/env python3
"""
Direct YAML Flow Debugger - No hanging, immediate feedback
"""

import yaml
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def debug_flow_yaml(file_path):
    """Debug YAML flow structure with immediate feedback."""
    console = Console()
    
    try:
        # Load YAML
        with open(file_path, 'r') as f:
            flow_data = yaml.safe_load(f)
        
        console.print(f"✅ YAML loaded successfully from: {file_path}")
        
        # Check structure
        errors = []
        warnings = []
        
        # Required fields
        if 'title' not in flow_data:
            errors.append("Missing 'title' field")
        else:
            console.print(f"📋 Title: {flow_data['title']}")
        
        if 'steps' not in flow_data:
            errors.append("Missing 'steps' field")
        elif not isinstance(flow_data['steps'], list):
            errors.append("'steps' must be a list")
        else:
            console.print(f"📊 Found {len(flow_data['steps'])} steps")
            
            # Check each step
            for i, step in enumerate(flow_data['steps']):
                step_num = i + 1
                step_id = step.get('id', f'step_{step_num}')
                step_type = step.get('type', 'unknown')
                
                if 'id' not in step:
                    errors.append(f"Step {step_num}: Missing 'id'")
                if 'type' not in step:
                    errors.append(f"Step {step_num} ({step_id}): Missing 'type'")
                
                # Check select fields
                if step_type == 'select':
                    if 'choices' not in step:
                        errors.append(f"Step {step_num} ({step_id}): Select type needs 'choices'")
                    else:
                        choices = step['choices']
                        default = step.get('default')
                        console.print(f"  🔸 Step {step_num} ({step_id}): {step_type} with {len(choices)} choices")
                        
                        if default:
                            # Check if default is valid
                            valid_choices = []
                            for choice in choices:
                                if isinstance(choice, str):
                                    valid_choices.append(choice)
                                elif isinstance(choice, dict):
                                    if 'value' in choice:
                                        valid_choices.append(choice['value'])
                                    if 'name' in choice:
                                        valid_choices.append(choice['name'])
                            
                            if default not in valid_choices:
                                errors.append(f"Step {step_num} ({step_id}): Default '{default}' not in choices {valid_choices}")
                else:
                    console.print(f"  🔸 Step {step_num} ({step_id}): {step_type}")
        
        # Show results
        if errors:
            console.print("\n❌ ERRORS FOUND:")
            for error in errors:
                console.print(f"  • {error}", style="red")
        
        if warnings:
            console.print("\n⚠️  WARNINGS:")
            for warning in warnings:
                console.print(f"  • {warning}", style="yellow")
        
        if not errors and not warnings:
            console.print("\n🎉 Flow structure looks good!", style="green")
            
            # Show a preview of what would run
            console.print("\n📋 Flow Preview:")
            for i, step in enumerate(flow_data['steps'][:5]):  # Show first 5 steps
                step_id = step.get('id', f'step_{i+1}')
                step_type = step.get('type', 'unknown')
                message = step.get('message', step.get('title', 'No message'))
                console.print(f"  {i+1}. [{step_type}] {message}")
            
            if len(flow_data['steps']) > 5:
                console.print(f"  ... and {len(flow_data['steps']) - 5} more steps")
        
        return len(errors) == 0
        
    except yaml.YAMLError as e:
        console.print(f"❌ YAML Parse Error: {e}", style="red")
        return False
    except FileNotFoundError:
        console.print(f"❌ File not found: {file_path}", style="red")
        return False
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_flow.py <yaml_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = debug_flow_yaml(file_path)
    sys.exit(0 if success else 1)