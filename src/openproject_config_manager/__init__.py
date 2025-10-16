"""OpenProject Configuration Manager

Interactive configuration management for Docker Compose projects with intelligent
discovery and live validation.

Supports dual-mode operation:
- Development Mode: Auto-detected via .git directory, uses local paths
- Production Mode: Receives paths from orchestrator, works as pip package
"""

__version__ = "2.0.0"
__author__ = "OpenProject Contributors"

from .core.config import Configuration
from .core.manager import ConfigurationManager

__all__ = ["Configuration", "ConfigurationManager", "__version__"]
