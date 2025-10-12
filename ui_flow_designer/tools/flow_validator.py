#!/usr/bin/env python3
"""
Flow Validation Tool
Validate YAML flow definitions for correctness and best practices.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import argparse
import sys
import re


class FlowValidator:
    """Comprehensive validator for YAML flow definitions."""
    
    def __init__(self):
        self.step_types = {
            'text': {
                'required_fields': ['id', 'message'],
                'optional_fields': ['default', 'instruction', 'validate', 'when'],
                'description': 'Text input field'
            },
            'select': {
                'required_fields': ['id', 'message', 'choices'],
                'optional_fields': ['default', 'instruction', 'when'],
                'description': 'Single selection from choices'
            },
            'confirm': {
                'required_fields': ['id', 'message'],
                'optional_fields': ['default', 'instruction', 'when'],
                'description': 'Yes/No confirmation'
            },
            'computed': {
                'required_fields': ['id', 'compute'],
                'optional_fields': ['when'],
                'description': 'Computed value from expression'
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
        
        self.reserved_fields = [
            'discovered_data',
            'initial_config',
            'system_data',
            'docker_data',
            'env_data'
        ]
    
    def validate_flow_file(self, flow_path: Path) -> Tuple[List[str], List[str]]:
        """
        Validate a single flow file.
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        if not flow_path.exists():
            errors.append(f"File does not exist: {flow_path}")
            return errors, warnings
        
        try:
            with open(flow_path, 'r') as f:
                flow_def = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {e}")
            return errors, warnings
        except Exception as e:
            errors.append(f"Failed to read file: {e}")
            return errors, warnings
        
        if not isinstance(flow_def, dict):
            errors.append("Flow definition must be a dictionary")
            return errors, warnings
        
        # Validate flow structure
        flow_errors, flow_warnings = self.validate_flow_definition(flow_def, flow_path.stem)
        errors.extend(flow_errors)
        warnings.extend(flow_warnings)
        
        return errors, warnings
    
    def validate_flow_definition(self, flow_def: Dict[str, Any], flow_id: str) -> Tuple[List[str], List[str]]:
        """
        Validate a flow definition dictionary.
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Required top-level fields
        required_fields = ['title', 'steps']
        for field in required_fields:
            if field not in flow_def:
                errors.append(f"Missing required field: {field}")
        
        # Optional top-level fields validation
        if 'title' in flow_def:
            if not isinstance(flow_def['title'], str) or not flow_def['title'].strip():
                errors.append("Title must be a non-empty string")
        
        if 'description' in flow_def:
            if not isinstance(flow_def['description'], str):
                warnings.append("Description should be a string")
        
        if 'icon' in flow_def:
            icon = flow_def['icon']
            if not isinstance(icon, str) or len(icon) > 10:
                warnings.append("Icon should be a short string (preferably emoji)")
        
        # Validate steps
        steps = flow_def.get('steps', [])
        if not isinstance(steps, list):
            errors.append("Steps must be a list")
        elif len(steps) == 0:
            warnings.append("Flow has no steps")
        else:
            step_errors, step_warnings = self.validate_steps(steps)
            errors.extend(step_errors)
            warnings.extend(step_warnings)
        
        # Validate output mapping
        if 'output_mapping' in flow_def:
            mapping_errors, mapping_warnings = self.validate_output_mapping(
                flow_def['output_mapping'], steps
            )
            errors.extend(mapping_errors)
            warnings.extend(mapping_warnings)
        
        return errors, warnings
    
    def validate_steps(self, steps: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate flow steps."""
        errors = []
        warnings = []
        
        step_ids = set()
        
        for i, step in enumerate(steps):
            step_prefix = f"Step {i+1}"
            
            if not isinstance(step, dict):
                errors.append(f"{step_prefix}: Must be a dictionary")
                continue
            
            # Validate step ID
            step_id = step.get('id')
            if not step_id:
                errors.append(f"{step_prefix}: Missing 'id' field")
                continue
            
            if not isinstance(step_id, str):
                errors.append(f"{step_prefix}: 'id' must be a string")
                continue
            
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', step_id):
                errors.append(f"{step_prefix} ({step_id}): ID must start with letter and contain only letters, numbers, and underscores")
            
            if step_id in step_ids:
                errors.append(f"{step_prefix} ({step_id}): Duplicate step ID")
            else:
                step_ids.add(step_id)
            
            if step_id in self.reserved_fields:
                warnings.append(f"{step_prefix} ({step_id}): Using reserved field name")
            
            # Validate step type
            step_type = step.get('type')
            if not step_type:
                errors.append(f"{step_prefix} ({step_id}): Missing 'type' field")
                continue
            
            if step_type not in self.step_types:
                errors.append(f"{step_prefix} ({step_id}): Invalid step type '{step_type}'")
                continue
            
            type_info = self.step_types[step_type]
            
            # Check required fields for this step type
            for field in type_info['required_fields']:
                if field not in step:
                    errors.append(f"{step_prefix} ({step_id}): Missing required field '{field}' for type '{step_type}'")
            
            # Validate specific fields
            field_errors, field_warnings = self.validate_step_fields(step, step_prefix, step_id)
            errors.extend(field_errors)
            warnings.extend(field_warnings)
        
        return errors, warnings
    
    def validate_step_fields(self, step: Dict[str, Any], step_prefix: str, step_id: str) -> Tuple[List[str], List[str]]:
        """Validate individual step fields."""
        errors = []
        warnings = []
        
        # Validate message
        if 'message' in step:
            message = step['message']
            if not isinstance(message, str) or not message.strip():
                errors.append(f"{step_prefix} ({step_id}): 'message' must be a non-empty string")
        
        # Validate choices (for select type)
        if 'choices' in step:
            choices = step['choices']
            if not isinstance(choices, list):
                errors.append(f"{step_prefix} ({step_id}): 'choices' must be a list")
            elif len(choices) == 0:
                errors.append(f"{step_prefix} ({step_id}): 'choices' cannot be empty")
            else:
                for j, choice in enumerate(choices):
                    if not isinstance(choice, str):
                        errors.append(f"{step_prefix} ({step_id}): Choice {j+1} must be a string")
        
        # Validate default value
        if 'default' in step and step['default'] == '':
            warnings.append(f"{step_prefix} ({step_id}): Empty default value")
        
        # Validate validator
        if 'validate' in step:
            validator = step['validate']
            if validator not in self.validators:
                warnings.append(f"{step_prefix} ({step_id}): Unknown validator '{validator}'")
        
        # Validate compute expression
        if 'compute' in step:
            compute = step['compute']
            if not isinstance(compute, str) or not compute.strip():
                errors.append(f"{step_prefix} ({step_id}): 'compute' must be a non-empty string")
        
        # Validate when condition
        if 'when' in step:
            when = step['when']
            if not isinstance(when, str) or not when.strip():
                errors.append(f"{step_prefix} ({step_id}): 'when' must be a non-empty string")
        
        return errors, warnings
    
    def validate_output_mapping(self, output_mapping: Dict[str, str], steps: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Validate output mapping configuration."""
        errors = []
        warnings = []
        
        if not isinstance(output_mapping, dict):
            errors.append("Output mapping must be a dictionary")
            return errors, warnings
        
        step_ids = {step.get('id') for step in steps if step.get('id')}
        
        for source_id, target_path in output_mapping.items():
            if source_id not in step_ids:
                errors.append(f"Output mapping references unknown step ID: {source_id}")
            
            if not isinstance(target_path, str):
                errors.append(f"Output mapping target must be a string: {source_id} -> {target_path}")
            elif not target_path.strip():
                errors.append(f"Output mapping target cannot be empty: {source_id}")
        
        return errors, warnings
    
    def validate_directory(self, flows_dir: Path) -> Dict[str, Tuple[List[str], List[str]]]:
        """
        Validate all flow files in a directory.
        
        Returns:
            Dictionary mapping flow_id to (errors, warnings)
        """
        results = {}
        
        if not flows_dir.exists():
            return {"_directory_": ([f"Directory does not exist: {flows_dir}"], [])}
        
        flow_files = list(flows_dir.glob("*.yml"))
        if not flow_files:
            return {"_directory_": ([], ["No flow files found"])}
        
        for flow_file in flow_files:
            flow_id = flow_file.stem
            errors, warnings = self.validate_flow_file(flow_file)
            results[flow_id] = (errors, warnings)
        
        return results
    
    def print_validation_results(self, results: Dict[str, Tuple[List[str], List[str]]], verbose: bool = False):
        """Print validation results in a readable format."""
        total_errors = 0
        total_warnings = 0
        
        for flow_id, (errors, warnings) in results.items():
            total_errors += len(errors)
            total_warnings += len(warnings)
            
            if flow_id == "_directory_":
                if errors or warnings:
                    print("📁 Directory Issues:")
                    for error in errors:
                        print(f"   ❌ {error}")
                    for warning in warnings:
                        print(f"   ⚠️  {warning}")
                    print()
                continue
            
            if errors or warnings or verbose:
                print(f"📄 Flow: {flow_id}")
                
                if errors:
                    print("   ❌ Errors:")
                    for error in errors:
                        print(f"      • {error}")
                
                if warnings:
                    print("   ⚠️  Warnings:")
                    for warning in warnings:
                        print(f"      • {warning}")
                
                if not errors and not warnings:
                    print("   ✅ Valid")
                
                print()
        
        # Summary
        flow_count = len([k for k in results.keys() if k != "_directory_"])
        error_count = len([k for k, (e, w) in results.items() if e and k != "_directory_"])
        warning_count = len([k for k, (e, w) in results.items() if w and k != "_directory_"])
        
        print("📊 Summary:")
        print(f"   Flows validated: {flow_count}")
        print(f"   Flows with errors: {error_count}")
        print(f"   Flows with warnings: {warning_count}")
        print(f"   Total errors: {total_errors}")
        print(f"   Total warnings: {total_warnings}")
        
        if total_errors == 0 and total_warnings == 0:
            print("   🎉 All flows are valid!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate YAML flow definitions")
    parser.add_argument(
        'path',
        help='Path to flow file or directory containing flows'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show results for all flows, even if valid'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only show summary'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    validator = FlowValidator()
    
    if path.is_file():
        # Validate single file
        flow_id = path.stem
        errors, warnings = validator.validate_flow_file(path)
        results = {flow_id: (errors, warnings)}
    elif path.is_dir():
        # Validate directory
        results = validator.validate_directory(path)
    else:
        print(f"❌ Path does not exist: {path}")
        sys.exit(1)
    
    if not args.quiet:
        validator.print_validation_results(results, verbose=args.verbose)
    
    # Exit with error code if there are errors
    total_errors = sum(len(errors) for errors, warnings in results.values())
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()