#!/usr/bin/env python3
"""
Enhanced TUI Engine with Intelligent Defaults System
Demonstrates loading and processing defaults_file specification
"""

from pathlib import Path
from typing import Any, Dict, Optional

import questionary
import yaml
from rich.console import Console
from rich.panel import Panel


class IntelligentDefaultsEngine:
    """TUI Engine with intelligent defaults support."""

    def __init__(self):
        self.console = Console()
        self.responses = {}
        self.probe_defaults = None

    def load_layout_and_defaults(
        self, layout_path: str
    ) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """Load layout file and associated defaults file."""

        # Load main layout
        with open(layout_path, "r") as f:
            layout_data = yaml.safe_load(f)

        # Check for defaults_file specification
        defaults_file = layout_data.get("metadata", {}).get("defaults_file")
        probe_defaults = None

        if defaults_file:
            # Resolve defaults file path (relative to layout file)
            layout_dir = Path(layout_path).parent
            defaults_path = layout_dir / defaults_file

            if defaults_path.exists():
                self.console.print(f"🔍 Loading intelligent defaults from: {defaults_file}")
                with open(defaults_path, "r") as f:
                    probe_defaults = yaml.safe_load(f)
                self._show_probe_info(probe_defaults)
            else:
                self.console.print(f"⚠️  Defaults file not found: {defaults_file}")

        return layout_data, probe_defaults

    def _show_probe_info(self, probe_defaults: Dict[str, Any]):
        """Display probe information to user."""
        if not probe_defaults:
            return

        metadata = probe_defaults.get("metadata", {})
        system_info = metadata.get("system_info", {})

        if system_info:
            info_text = f"""System detected: {system_info.get('os', 'Unknown')} ({system_info.get('arch', 'Unknown')})
Memory: {system_info.get('memory_total_gb', '?')}GB, CPU: {system_info.get('cpu_cores', '?')} cores
Network: {metadata.get('network_info', {}).get('public_ip', 'No public IP')}
Generated: {metadata.get('generated_at', 'Unknown time')}"""

            self.console.print(
                Panel(info_text, title="🧠 Intelligent Defaults Loaded", border_style="blue")
            )

    def resolve_default_value(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve default value with intelligent precedence."""
        step_id = step.get("id")

        # 1. Check for dynamic defaults based on previous responses
        if "dynamic_defaults" in step:
            for dynamic_rule in step["dynamic_defaults"]:
                condition = dynamic_rule["condition"]
                if self._evaluate_condition(condition, self.responses):
                    return {
                        "value": dynamic_rule["value"],
                        "source": "dynamic",
                        "reason": dynamic_rule.get("reason", "Based on previous selections"),
                        "condition": condition,
                    }

        # 2. Check probe defaults from defaults_file
        if self.probe_defaults and step_id in self.probe_defaults.get("defaults", {}):
            probe_default = self.probe_defaults["defaults"][step_id]
            return {
                "value": probe_default["value"],
                "source": "probe",
                "reason": probe_default.get("reason", "Based on system detection"),
                "confidence": probe_default.get("confidence", "unknown"),
                "probe_source": probe_default.get("probe_source", "system"),
            }

        # 3. Fall back to static default in layout
        if "default" in step:
            return {"value": step["default"], "source": "static", "reason": "Layout default"}

        # 4. Type-based defaults
        type_defaults = {"text": "", "password": "", "confirm": True, "select": None}

        return {
            "value": type_defaults.get(step["type"], ""),
            "source": "type",
            "reason": "Engine default",
        }

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Simple condition evaluator for dynamic defaults."""
        # Basic implementation - could be enhanced with proper expression parser
        try:
            # Replace variables with values from context
            for key, value in context.items():
                if isinstance(value, str):
                    condition = condition.replace(key, f"'{value}'")
                else:
                    condition = condition.replace(key, str(value))

            # Simple evaluation (in production, use safer evaluation)
            return eval(condition)
        except:
            return False

    def run_flow_with_intelligent_defaults(self, layout_path: str):
        """Run flow with intelligent defaults system."""

        # Load layout and defaults
        layout_data, self.probe_defaults = self.load_layout_and_defaults(layout_path)

        # Show welcome
        title = layout_data.get("title", "Configuration Flow")
        description = layout_data.get("description", "")
        icon = layout_data.get("icon", "🔧")

        self.console.print(
            Panel(f"{icon} {title}\n{description}", title="Flow Start", border_style="blue")
        )

        steps = layout_data.get("steps", [])
        self.console.print(f"\n🎯 Starting intelligent flow with {len(steps)} steps...")

        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i+1}")
            step_type = step.get("type", "text")
            message = step.get("message", step.get("title", f"Step {i+1}"))
            instruction = step.get("instruction", "")

            # Skip info steps and conditional steps for this demo
            if step_type == "info":
                self.console.print(
                    Panel(step.get("message", ""), title=step.get("title", "Information"))
                )
                questionary.press_any_key_to_continue("Press any key to continue...").ask()
                continue

            if "condition" in step:
                self.console.print(f"⏭️  Skipping conditional step: {step_id}")
                continue

            # Resolve intelligent default
            default_info = self.resolve_default_value(step)
            default_value = default_info["value"]

            # Show default source information
            source_info = f"💡 {instruction}"
            if default_info["source"] != "type":
                source_emoji = {"dynamic": "🔄", "probe": "🧠", "static": "📋"}
                source_info += (
                    f"\n{source_emoji.get(default_info['source'], '🔧')} {default_info['reason']}"
                )

            # Build step display
            step_display = f"Step {i+1}/{len(steps)}: {message}"
            if source_info:
                step_display += f"\n{source_info}"

            try:
                if step_type == "text":
                    response = questionary.text(
                        step_display, default=str(default_value) if default_value else ""
                    ).ask()

                elif step_type == "password":
                    response = questionary.password(step_display).ask()

                elif step_type == "confirm":
                    response = questionary.confirm(step_display, default=bool(default_value)).ask()

                elif step_type == "select":
                    choices = step.get("choices", [])
                    choice_list = []
                    for choice in choices:
                        if isinstance(choice, str):
                            choice_list.append(choice)
                        elif isinstance(choice, dict):
                            choice_list.append(choice.get("name", choice.get("value", str(choice))))

                    response = questionary.select(
                        step_display,
                        choices=choice_list,
                        default=default_value if default_value in choice_list else None,
                    ).ask()

                else:
                    self.console.print(f"⚠️  Unknown step type: {step_type}")
                    continue

                # Store response for future dynamic defaults
                self.responses[step_id] = response

            except KeyboardInterrupt:
                self.console.print("\n👋 Flow cancelled by user")
                return None
            except Exception as e:
                self.console.print(f"❌ Error in step {step_id}: {e}")
                continue

        # Show completion
        self.console.print(
            Panel(
                f"🎉 Flow completed!\n📊 Collected {len(self.responses)} responses\n🧠 Used intelligent defaults system",
                title="Success",
                border_style="green",
            )
        )

        return self.responses


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python intelligent_defaults_demo.py <layout_file>")
        sys.exit(1)

    engine = IntelligentDefaultsEngine()
    responses = engine.run_flow_with_intelligent_defaults(sys.argv[1])

    if responses:
        print(f"\nCompleted with {len(responses)} responses using intelligent defaults!")
        for key, value in responses.items():
            print(f"  {key}: {value}")
    else:
        print("Flow was cancelled")
