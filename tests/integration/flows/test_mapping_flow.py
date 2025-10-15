#!/usr/bin/env python3
"""Test script for the new mapping phase."""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from openproject_config_manager.core.manager import ConfigurationManager

    print("=" * 60)
    print("TESTING DISCOVERY → TUI MAPPING PIPELINE")
    print("=" * 60)

    # Create manager instance
    manager = ConfigurationManager(verbose=True)

    # Run discovery phase (will write enhanced_defaults.yml)
    print("\n1. Running Discovery Phase...")
    discovered_data = manager.run_discovery_phase()

    # Run TUI mapping phase (will read enhanced_defaults.yml and write config_tui.defaults.yml)
    print("\n2. Running TUI Mapping Phase...")
    tui_defaults_path = manager.run_tui_mapping_phase()

    # Show the results
    print("\n" + "=" * 60)
    print("PIPELINE RESULTS")
    print("=" * 60)

    # Check enhanced defaults file
    enhanced_path = Path("outputs/discovery/enhanced_defaults.yml")
    if enhanced_path.exists():
        print(f"✅ Enhanced defaults file created: {enhanced_path}")
        print(f"   Size: {enhanced_path.stat().st_size} bytes")
    else:
        print("❌ Enhanced defaults file not found")

    # Check TUI defaults file
    tui_path = Path(tui_defaults_path)
    if tui_path.exists():
        print(f"✅ TUI defaults file created: {tui_path}")
        print(f"   Size: {tui_path.stat().st_size} bytes")

        # Show content preview
        with open(tui_path, "r") as f:
            content = f.read()
            print(f"\nTUI Defaults Content Preview:")
            print("-" * 40)
            print(content[:400] + "..." if len(content) > 400 else content)
    else:
        print("❌ TUI defaults file not found")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
