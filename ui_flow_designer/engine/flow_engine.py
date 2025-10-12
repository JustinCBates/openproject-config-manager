"""Flow engine for executing YAML-defined flows using Questionary."""

import questionary
from questionary import Style, form
import yaml
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import re


class FlowEngine:
    """Execute YAML-defined flows using Questionary."""
    
    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        self.style = Style([
            ('question', 'bold blue'),
            ('answer', 'fg:#ff9d00 bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
            ('selected', 'fg:#cc5454'),
            ('instruction', 'italic'),
        ])
        self.validators = self._load_validators()
    
    def get_available_flows(self) -> List[str]:
        """Get list of available flow IDs."""
        if not self.flows_dir.exists():
            return []
        
        flows = []
        for flow_file in self.flows_dir.glob("*.yml"):
            flows.append(flow_file.stem)
        return flows
    
    def execute_flow(self, flow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a flow by ID with optional context."""
        flow_def = self._load_flow(flow_id)
        context = context or {}
        
        # Show flow header
        questionary.print(f"\n{flow_def.get('icon', '🔧')} {flow_def['title']}", style="bold blue")
        if flow_def.get('description'):
            questionary.print(f"   {flow_def['description']}", style="italic")
        
        # Execute steps sequentially to handle conditional logic
        answers = {}
        
        for step in flow_def['steps']:
            if step['type'] == 'computed':
                # Handle computed values
                if 'compute' in step:
                    computed_value = self._evaluate_expression(step['compute'], {**context, **answers})
                    answers[step['id']] = computed_value
                continue
                
            # Check if step should be shown
            if not self._should_show_step(step, {**context, **answers}):
                continue
                
            # Build and ask question
            question = self._build_question(step, {**context, **answers})
            if question:
                answer = question.ask()
                answers[step['id']] = answer
                
                # Show preview if defined
                if 'preview' in step:
                    preview_text = self._format_preview(step['preview'], {**context, **answers})
                    questionary.print(f"   📋 {preview_text}", style="bold green")
        
        # Apply output mapping if specified
        if 'output_mapping' in flow_def:
            return self._apply_output_mapping(answers, flow_def['output_mapping'])
        
        return answers
    
    def _build_question(self, step: Dict[str, Any], context: Dict[str, Any]):
        """Build a questionary question from step definition."""
        
        if step['type'] == 'select':
            choices = []
            for choice in step['choices']:
                if isinstance(choice, dict):
                    choices.append(choice['name'])
                else:
                    choices.append(choice)
            
            return questionary.select(
                step['message'],
                choices=choices,
                default=step.get('default'),
                instruction=step.get('instruction')
            )
        
        elif step['type'] == 'text':
            # Build text question with validation
            if 'validate' in step:
                validator_name = step['validate']
                validator_func = self.validators.get(validator_name)
                return questionary.text(
                    step['message'],
                    default=step.get('default', ''),
                    instruction=step.get('instruction'),
                    validate=validator_func
                )
            else:
                return questionary.text(
                    step['message'],
                    default=step.get('default', ''),
                    instruction=step.get('instruction')
                )
        
        elif step['type'] == 'confirm':
            return questionary.confirm(
                step['message'],
                default=step.get('default', True)
            )
        
        return None
    
    def _should_show_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if a step should be shown based on conditions."""
        if 'when' not in step:
            return True
        
        condition = step['when']
        return self._evaluate_expression(condition, context)
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """Evaluate a simple expression against context."""
        # Simple expression evaluator for conditions like "uri_namespace_enabled == true"
        # This is a basic implementation - could be enhanced with a proper expression parser
        
        # Handle simple equality checks
        if '==' in expression:
            left, right = expression.split('==', 1)
            left = left.strip()
            right = right.strip().strip("'\"")
            
            # Convert string boolean values
            if right.lower() == 'true':
                right = True
            elif right.lower() == 'false':
                right = False
            
            left_value = self._get_nested_value(context, left)
            return left_value == right
        
        # Handle simple boolean checks
        if expression in context:
            return bool(context[expression])
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get nested value using dot notation."""
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
    
    def _format_preview(self, preview_template: str, context: Dict[str, Any]) -> str:
        """Format preview text with context variables."""
        # Simple template formatting - replace {variable} with context values
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            value = self._get_nested_value(context, var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        
        return re.sub(r'\{([^}]+)\}', replace_var, preview_template)
    
    def _load_flow(self, flow_id: str) -> Dict[str, Any]:
        """Load flow definition from YAML file."""
        flow_path = self.flows_dir / f"{flow_id}.yml"
        if not flow_path.exists():
            raise FileNotFoundError(f"Flow definition not found: {flow_path}")
        
        with open(flow_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _apply_output_mapping(self, answers: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Apply output mapping to transform answers."""
        result = {}
        for answer_key, answer_value in answers.items():
            if answer_key in mapping:
                output_key = mapping[answer_key]
                # Handle nested output keys like "configuration.uri_namespace"
                if '.' in output_key:
                    parts = output_key.split('.')
                    current = result
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = answer_value
                else:
                    result[output_key] = answer_value
            else:
                result[answer_key] = answer_value
        return result
    
    def _load_validators(self) -> Dict[str, Callable]:
        """Load built-in validators."""
        def namespace_path_validator(value: str) -> bool:
            """Validate namespace path format."""
            if not value:
                raise questionary.ValidationError(message="Path cannot be empty")
            if not value.startswith('/'):
                raise questionary.ValidationError(message="Path must start with '/'")
            if value.endswith('/') and value != '/':
                raise questionary.ValidationError(message="Path should not end with '/'")
            if len(value) > 50:
                raise questionary.ValidationError(message="Path too long (max 50 characters)")
            # Check for valid characters
            if not re.match(r'^/[a-zA-Z0-9/_-]*$', value):
                raise questionary.ValidationError(message="Path contains invalid characters")
            return True
        
        def domain_validator(value: str) -> bool:
            """Validate domain format."""
            if not value:
                raise questionary.ValidationError(message="Domain cannot be empty")
            if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                raise questionary.ValidationError(message="Invalid domain format")
            return True
        
        return {
            'namespace_path': namespace_path_validator,
            'domain': domain_validator,
        }