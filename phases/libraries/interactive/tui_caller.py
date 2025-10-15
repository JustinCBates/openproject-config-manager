#!/usr/bin/env python3
"""
TUI Form Caller Unit

Reusable unit for executing TUI forms and collecting user input.
Encapsulates the TUI Form Engine integration logic.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class TUIFormCaller:
    """
    Unit for calling TUI forms and collecting user responses.
    
    This unit provides a standardized interface for:
    - Loading TUI layout files
    - Loading defaults files
    - Executing TUI forms (with optional mock responses)
    - Saving responses to JSON
    
    Usage:
        caller = TUIFormCaller()
        responses = caller.execute_form(
            layout_path="path/to/layout.yml",
            defaults_path="path/to/defaults.yml",
            output_path="path/to/responses.json"
        )
    """
    
    def __init__(self):
        """Initialize TUI Form Caller."""
        # Lazy import to avoid dependency if not used
        self._renderer = None
    
    @property
    def renderer(self):
        """Lazy-load TUI Form Renderer."""
        if self._renderer is None:
            try:
                from tui_form_engine.renderer import FormRenderer
                self._renderer = FormRenderer()
            except ImportError:
                raise ImportError(
                    "TUI Form Engine not available. "
                    "Install with: pip install tui-form-designer"
                )
        return self._renderer
    
    def execute_form(
        self,
        layout_path: str,
        defaults_path: Optional[str] = None,
        output_path: Optional[str] = None,
        mock_responses: Optional[Dict[str, Any]] = None,
        quiet: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a TUI form and collect user responses.
        
        Args:
            layout_path: Path to the .layout.yml file
            defaults_path: Path to the defaults YAML file (optional, for info only)
            output_path: Path to save responses JSON (optional)
            mock_responses: Mock responses for testing (optional)
            quiet: Suppress output messages
            
        Returns:
            Dictionary containing user responses
            
        Raises:
            FileNotFoundError: If layout file doesn't exist
            ValueError: If layout/defaults files are invalid
            
        Note:
            The defaults_path parameter is informational only.
            The TUI Form Engine loads defaults from the layout's defaults_file field.
        """
        layout_path = Path(layout_path)
        
        # Validate layout file exists
        if not layout_path.exists():
            raise FileNotFoundError(f"Layout file not found: {layout_path}")
        
        # Execute TUI form
        if not quiet:
            print(f"📋 Executing TUI form: {layout_path.name}")
        
        try:
            flow_response = self.renderer.render_flow(
                flow_path=str(layout_path),
                mock_responses=mock_responses,
                output_file=str(output_path) if output_path else None,
                quiet=quiet
            )
            
            responses = flow_response.get("responses", {})
            
        except Exception as e:
            raise ValueError(f"TUI form execution failed: {e}")
        
        # Note: output is already saved by render_flow if output_file was provided
        if output_path and not quiet:
            print(f"💾 Responses saved: {output_path}")
        
        return responses
    
    def load_layout(self, layout_path: str) -> Dict[str, Any]:
        """
        Load and parse a TUI layout file.
        
        Args:
            layout_path: Path to the .layout.yml file
            
        Returns:
            Dictionary containing layout definition
            
        Raises:
            FileNotFoundError: If layout file doesn't exist
            ValueError: If YAML is invalid
        """
        layout_path = Path(layout_path)
        
        if not layout_path.exists():
            raise FileNotFoundError(f"Layout file not found: {layout_path}")
        
        try:
            with open(layout_path, 'r') as f:
                layout = yaml.safe_load(f)
            return layout
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in layout file: {e}")
    
    def load_defaults(self, defaults_path: str) -> Dict[str, Any]:
        """
        Load and parse a defaults file.
        
        Args:
            defaults_path: Path to the defaults YAML file
            
        Returns:
            Dictionary containing default values
            
        Raises:
            FileNotFoundError: If defaults file doesn't exist
            ValueError: If YAML is invalid
        """
        defaults_path = Path(defaults_path)
        
        if not defaults_path.exists():
            raise FileNotFoundError(f"Defaults file not found: {defaults_path}")
        
        try:
            with open(defaults_path, 'r') as f:
                defaults = yaml.safe_load(f)
            return defaults
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in defaults file: {e}")
    
    def validate_responses(
        self,
        responses: Dict[str, Any],
        required_fields: Optional[list] = None
    ) -> bool:
        """
        Validate that responses contain required fields.
        
        Args:
            responses: Dictionary of user responses
            required_fields: List of required field IDs (optional)
            
        Returns:
            True if valid, False otherwise
        """
        if not required_fields:
            return True
        
        missing_fields = [
            field for field in required_fields
            if field not in responses
        ]
        
        if missing_fields:
            print(f"⚠️  Missing required fields: {', '.join(missing_fields)}")
            return False
        
        return True
