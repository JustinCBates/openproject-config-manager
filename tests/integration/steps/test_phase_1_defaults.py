#!/usr/bin/env python3
"""Test script to demonstrate enhanced defaults generation."""

import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from openproject_config_manager.core.manager import ConfigurationManager

    print("=" * 60)
    print("TESTING ENHANCED DEFAULTS GENERATION")
    print("=" * 60)

    # Create manager instance
    manager = ConfigurationManager(verbose=True)

    # Run discovery phase to populate discovered_data
    print("\n1. Running Discovery Phase...")
    discovered_data = manager.run_discovery_phase()

    print(f"\nDiscovered data keys: {list(discovered_data.keys())}")

    # Generate enhanced defaults
    print("\n2. Generating Enhanced Defaults...")
    enhanced_defaults = manager._generate_enhanced_defaults()

    # Show the concrete product
    print("\n" + "=" * 60)
    print("CONCRETE ENHANCED DEFAULTS OUTPUT")
    print("=" * 60)

    print(json.dumps(enhanced_defaults, indent=2, default=str))

    print("\n" + "=" * 60)
    print("METADATA SECTION")
    print("=" * 60)
    for key, value in enhanced_defaults.get("metadata", {}).items():
        print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("DEFAULTS SECTION")
    print("=" * 60)
    for key, value in enhanced_defaults.get("defaults", {}).items():
        print(f"\n{key}:")
        for sub_key, sub_value in value.items():
            print(f"  {sub_key}: {sub_value}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
