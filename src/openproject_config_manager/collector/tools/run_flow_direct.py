#!/usr/bin/env python3
"""
Direct TUI Runner - Bypass hanging engine, immediate interactive prompts
"""

import sys
from pathlib import Path

import questionary
import yaml
from questionary import Style
from rich.console import Console
from rich.panel import Panel


def run_flow_direct(file_path):
    """Run flow directly with questionary, no hanging engine."""
    console = Console()

    # Load YAML
    with open(file_path, "r") as f:
        flow_data = yaml.safe_load(f)

    # Show header
    title = flow_data.get("title", "Configuration Flow")
    description = flow_data.get("description", "")
    icon = flow_data.get("icon", "🔧")

    console.print(Panel(f"{icon} {title}\n{description}", title="Flow Start", border_style="blue"))

    responses = {}
    steps = flow_data.get("steps", [])

    console.print(f"\n🎯 Starting interactive flow with {len(steps)} steps...")

    for i, step in enumerate(steps):
        step_id = step.get("id", f"step_{i+1}")
        step_type = step.get("type", "text")
        message = step.get("message", step.get("title", f"Step {i+1}"))
        instruction = step.get("instruction", "")
        default = step.get("default")

        # Skip conditional steps for now (to avoid hanging)
        if "condition" in step:
            console.print(f"⏭️  Skipping conditional step: {step_id}")
            continue

        # Show step info
        step_display = f"Step {i+1}/{len(steps)}: {message}"
        if instruction:
            step_display += f"\n💡 {instruction}"

        try:
            if step_type == "info":
                # Just show info and continue
                info_message = step.get("message", "")
                console.print(Panel(info_message, title=step.get("title", "Information")))
                questionary.press_any_key_to_continue("Press any key to continue...").ask()

            elif step_type == "text":
                response = questionary.text(step_display, default=default or "").ask()
                responses[step_id] = response

            elif step_type == "password":
                response = questionary.password(step_display).ask()
                responses[step_id] = response

            elif step_type == "confirm":
                response = questionary.confirm(
                    step_display, default=default if default is not None else True
                ).ask()
                responses[step_id] = response

            elif step_type == "select":
                choices = step.get("choices", [])
                if not choices:
                    console.print(f"❌ No choices for select step: {step_id}")
                    continue

                # Handle both string and dict choices
                choice_list = []
                for choice in choices:
                    if isinstance(choice, str):
                        choice_list.append(choice)
                    elif isinstance(choice, dict):
                        choice_list.append(choice.get("name", choice.get("value", str(choice))))

                response = questionary.select(
                    step_display,
                    choices=choice_list,
                    default=default if default in choice_list else None,
                ).ask()
                responses[step_id] = response

            else:
                console.print(f"⚠️  Unknown step type '{step_type}' for step: {step_id}")

        except KeyboardInterrupt:
            console.print("\n👋 Flow cancelled by user")
            return None
        except Exception as e:
            console.print(f"❌ Error in step {step_id}: {e}")
            continue

    # Show results
    console.print(
        Panel(
            f"🎉 Flow completed!\n📊 Collected {len(responses)} responses",
            title="Success",
            border_style="green",
        )
    )

    console.print("\n📋 Response Summary:")
    for key, value in responses.items():
        console.print(f"  {key}: {value}")

    return responses


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_flow_direct.py <yaml_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        responses = run_flow_direct(file_path)
        if responses:
            print(f"\nFlow completed with {len(responses)} responses")
        else:
            print("Flow was cancelled")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
