"""
Step: Transform Defaults to TUI Format
Load enhanced defaults and mapping config, apply transformations, write TUI defaults file

Migrated from src/openproject_config_manager/transformer/
"""

from pathlib import Path
from typing import Dict, Any
import logging
import yaml
import json
import sys


logger = logging.getLogger(__name__)


class DefaultsTransformer:
    """Transforms enhanced defaults to TUI-compatible format."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def transform_enhanced_defaults(
        self, enhanced_defaults: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform enhanced defaults structure to TUI-compatible format.

        Args:
            enhanced_defaults: Enhanced defaults from discovery phase containing
                metadata and defaults with confidence scoring

        Returns:
            Transformed defaults suitable for TUI consumption
        """
        logger.info("Transforming enhanced defaults to TUI format")

        # Load mapping configuration
        mapping_config = self._load_defaults_mapping()

        # Apply field mappings
        tui_defaults = self._apply_field_mapping(enhanced_defaults, mapping_config)

        # Create output structure
        result = {
            "defaults": tui_defaults,
            "metadata": {
                "source": "discovery_phase",
                "original_metadata": enhanced_defaults.get("metadata", {}),
            },
        }

        logger.info(f"Transformed {len(tui_defaults)} defaults for TUI")
        return result

    def flatten_enhanced_defaults(
        self, enhanced_defaults: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Flatten enhanced defaults structure for simple consumption.
        Extracts just the 'value' from each default entry.

        Args:
            enhanced_defaults: Enhanced defaults with value/reason/confidence structure

        Returns:
            Flattened defaults with simple key-value pairs
        """
        flattened = {}

        defaults_section = enhanced_defaults.get("defaults", {})
        for key, value_dict in defaults_section.items():
            if isinstance(value_dict, dict) and "value" in value_dict:
                # Extract just the value for TUI consumption
                flattened[key] = value_dict["value"]
            else:
                # Pass through simple values
                flattened[key] = value_dict

        logger.debug(f"Flattened {len(flattened)} defaults")
        return flattened

    def _load_defaults_mapping(self) -> Dict[str, Any]:
        """Load the defaults mapping configuration."""
        # Try to find defaults_map.json in multiple locations
        search_paths = [
            self.project_root
            / "src"
            / "openproject_config_manager"
            / "core"
            / "defaults_map.json",
            self.project_root / "config" / "defaults_map.json",
            Path(__file__).parent / "defaults_map.json",
        ]

        for mapping_path in search_paths:
            if mapping_path.exists():
                logger.info(f"Loading defaults mapping from {mapping_path}")
                with open(mapping_path, "r") as f:
                    return json.load(f)

        logger.warning("Defaults mapping file not found, using fallback mapping")
        # Return basic fallback mapping
        return {
            "field_mappings": {
                "domain": {
                    "source_path": "defaults.domain.value",
                    "target_key": "domain",
                    "fallback": "openproject.local",
                },
                "port": {
                    "source_path": "defaults.port.value",
                    "target_key": "port",
                    "fallback": "8080",
                },
                "memory_limit": {
                    "source_path": "defaults.memory_limit.value",
                    "target_key": "memory_limit",
                    "fallback": "2GB",
                },
                "database_setup": {
                    "source_path": "defaults.database_setup.value",
                    "target_key": "database_setup",
                    "fallback": "container",
                },
                "ssl_configuration": {
                    "source_path": "defaults.ssl_configuration.value",
                    "target_key": "ssl_configuration",
                    "fallback": "Self-signed certificate",
                },
            },
            "output_format": {
                "header_comments": [
                    "# Configuration defaults for TUI layout",
                    "# Generated from discovery output via defaults mapping",
                ]
            },
        }

    def _apply_field_mapping(
        self, enhanced_defaults: Dict[str, Any], mapping_config: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Apply field mapping configuration to transform enhanced defaults.

        Args:
            enhanced_defaults: Enhanced defaults structure
            mapping_config: Mapping configuration with field_mappings

        Returns:
            Mapped defaults as simple key-value pairs
        """
        field_mappings = mapping_config.get("field_mappings", {})
        result = {}

        for field_name, mapping in field_mappings.items():
            source_path = mapping.get("source_path", "")
            target_key = mapping.get("target_key", field_name)
            fallback = mapping.get("fallback", "")

            # Navigate source path (e.g., "defaults.domain.value")
            value = enhanced_defaults
            try:
                for key in source_path.split("."):
                    value = value[key]
                result[target_key] = str(value)
                logger.debug(f"Mapped {source_path} → {target_key}: {value}")
            except (KeyError, TypeError):
                logger.warning(
                    f"Could not find {source_path} in enhanced defaults, using fallback: {fallback}"
                )
                result[target_key] = fallback

        return result

    def write_tui_defaults_file(
        self, tui_defaults: Dict[str, Any], output_path: Path
    ) -> str:
        """
        Write TUI-compatible defaults file.

        Args:
            tui_defaults: Transformed defaults ready for TUI
            output_path: Path to write the output file

        Returns:
            Path to the written file as string
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            yaml.dump(tui_defaults, f, default_flow_style=False, sort_keys=False)

        logger.info(f"TUI defaults written to {output_path}")
        return str(output_path)


def execute_transform_defaults(
    context: Dict[str, Any], phase_dir: Path
) -> Dict[str, Any]:
    """
    Transform Defaults to TUI Format
    Status: IMPLEMENTED

    Load enhanced defaults and mapping config, apply transformations, write TUI defaults file

    Args:
        context: Execution context containing:
            - enhanced_defaults_file: Path to enhanced defaults from Phase 1
            - enhanced_defaults: Enhanced defaults structure (optional)
        phase_dir: Phase directory path

    Returns:
        Dict with step results including:
            - tui_defaults_file: Path to transformed defaults file
            - tui_defaults: Transformed defaults structure
            - transformation_summary: Summary of transformation
    """
    logger.info("Executing step: Transform Defaults to TUI Format")

    # Get enhanced defaults from context
    enhanced_defaults_file = context.get("enhanced_defaults_file")
    enhanced_defaults = context.get("enhanced_defaults")

    # Load enhanced defaults if not in context
    if not enhanced_defaults and enhanced_defaults_file:
        logger.info(f"Loading enhanced defaults from {enhanced_defaults_file}")
        with open(enhanced_defaults_file, "r") as f:
            enhanced_defaults = yaml.safe_load(f)

    if not enhanced_defaults:
        raise ValueError("No enhanced defaults found in context or file")

    # Get project root (5 levels up from phase step directory)
    project_root = phase_dir.parent.parent

    # Transform defaults using the transformer
    transformer = DefaultsTransformer(project_root)
    tui_defaults = transformer.transform_enhanced_defaults(enhanced_defaults)

    # Write to output file
    output_dir = phase_dir / "outputs" / "tui"
    output_file = output_dir / "tui_defaults.yml"
    transformer.write_tui_defaults_file(tui_defaults, output_file)

    # Create transformation summary
    transformation_summary = {
        "source_defaults_count": len(enhanced_defaults.get("defaults", {})),
        "transformed_defaults_count": len(tui_defaults.get("defaults", {})),
        "metadata_preserved": "metadata" in tui_defaults,
        "transformation_successful": True,
    }

    logger.info(
        f"Transformation complete: {transformation_summary['transformed_defaults_count']} defaults mapped"
    )

    result = {
        "step": "transform_defaults",
        "status": "completed",
        "tui_defaults_file": str(output_file),
        "tui_defaults": tui_defaults,
        "transformation_summary": transformation_summary,
    }

    logger.info("Step Transform Defaults to TUI Format completed")
    return result


def main():
    """Standalone entry point for testing this step."""
    import argparse

    parser = argparse.ArgumentParser(description="Transform Defaults to TUI Format")
    parser.add_argument(
        "--enhanced-defaults", required=True, help="Path to enhanced_defaults.yml"
    )
    parser.add_argument("--output-dir", help="Output directory", default=None)
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Setup paths
    phase_dir = Path(__file__).parent.parent

    try:
        # Build context
        context = {"enhanced_defaults_file": args.enhanced_defaults}

        # Execute step
        result = execute_transform_defaults(context, phase_dir)

        print("\n" + "=" * 70)
        print(f"✅ Step completed: {result.get('status', 'unknown')}")
        print("=" * 70)
        print(f"\n📊 Transformation Results:")

        if "transformation_summary" in result:
            summary = result["transformation_summary"]
            print(f"  • Source defaults: {summary.get('source_defaults_count', 0)}")
            print(
                f"  • Transformed defaults: {summary.get('transformed_defaults_count', 0)}"
            )
            print(f"  • TUI defaults file: {result.get('tui_defaults_file', 'N/A')}")

        return 0 if result.get("status") == "completed" else 1

    except Exception as e:
        print(f"\n❌ Step failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())


class TransformDefaultsStep:
    """Wrapper class for transform_defaults step."""

    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_2_tui_mapping"

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute transform_defaults step.

        Args:
            context: Execution context

        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_transform_defaults(context, self.phase_dir)

        # Return in expected format
        return {
            "artifacts": (
                result_data if isinstance(result_data, dict) else {"data": result_data}
            )
        }
