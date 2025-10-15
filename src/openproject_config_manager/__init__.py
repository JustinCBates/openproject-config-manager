"""OpenProject Configuration Manager

Interactive configuration management for Docker Compose projects with intelligent
discovery and live validation.
"""

__version__ = "0.1.0"
__author__ = "OpenProject Contributors"

from .core.config import Configuration
from .core.manager import ConfigurationManager

__all__ = ["Configuration", "ConfigurationManager", "__version__"]
