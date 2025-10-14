"""
Utility helpers for Phase 5 Export
"""

from typing import Dict, Any


def convert_dot_notation_to_nested(dot_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert flat dot notation dict to nested dict.
    
    Example:
        {'project.name': 'Test'} -> {'project': {'name': 'Test'}}
    
    Args:
        dot_dict: Dictionary with dot-notation keys
        
    Returns:
        Nested dictionary
    """
    result = {}
    for key, value in dot_dict.items():
        parts = key.split('.')
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result
