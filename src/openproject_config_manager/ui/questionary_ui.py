"""Questionary-based UI replacement for Rich ConsoleUI."""

import sys
from typing import Any, Dict, List, Optional

import questionary
from questionary import Style, confirm, form
from questionary import print as qprint
from questionary import prompt, select, text


class QuestionaryUI:
    """Questionary-based UI replacement for ConsoleUI."""

    def __init__(self):
        self.style = Style(
            [
                ("question", "bold blue"),
                ("answer", "fg:#ff9d00 bold"),
                ("pointer", "fg:#673ab7 bold"),
                ("highlighted", "fg:#673ab7 bold"),
                ("selected", "fg:#cc5454"),
                ("instruction", "italic"),
                ("text", ""),
                ("disabled", "fg:#858585 italic"),
                ("separator", "fg:#cc5454"),
                ("skipped", "fg:#858585 italic"),
            ]
        )

    def show_title(self, title: str):
        """Show a main title with styling."""
        qprint(f"\n🚀 {title}", style="bold blue")
        qprint("=" * (len(title) + 4), style="blue")

    def show_phase_header(self, phase: str, description: str = ""):
        """Show a phase header with description."""
        qprint(f"\n📋 {phase}", style="bold green")
        if description:
            qprint(f"   {description}", style="italic")
        qprint("-" * 50, style="dim")

    def show_section_header(self, section: str, icon: str = "🔧"):
        """Show a section header."""
        qprint(f"\n{icon} {section}", style="bold yellow")

    def show_success(self, message: str):
        """Show a success message."""
        qprint(f"✅ {message}", style="bold green")

    def show_error(self, message: str):
        """Show an error message."""
        qprint(f"❌ {message}", style="bold red")

    def show_warning(self, message: str):
        """Show a warning message."""
        qprint(f"⚠️  {message}", style="bold yellow")

    def show_info(self, message: str):
        """Show an info message."""
        qprint(f"ℹ️  {message}", style="bold")

    def show_step(self, message: str):
        """Show a step message."""
        qprint(f"   → {message}", style="dim")

    def confirm(self, message: str, default: bool = True) -> bool:
        """Prompt user for yes/no confirmation."""
        try:
            return confirm(message, default=default, style=self.style).ask()
        except KeyboardInterrupt:
            self.show_error("Operation cancelled by user")
            sys.exit(1)

    def prompt(self, message: str, default: str = "", allow_empty: bool = False) -> str:
        """Prompt user for text input."""
        try:
            while True:
                result = text(message, default=default, style=self.style).ask()
                if not allow_empty and not result:
                    self.show_error("This field is required")
                    continue
                return result
        except KeyboardInterrupt:
            self.show_error("Operation cancelled by user")
            sys.exit(1)

    def prompt_int(
        self,
        message: str,
        default: Optional[int] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> int:
        """Prompt user for integer input."""
        try:
            while True:
                try:
                    default_str = str(default) if default is not None else ""
                    result_str = text(
                        f"{message} (number)", default=default_str, style=self.style
                    ).ask()

                    result = int(result_str)

                    if min_value is not None and result < min_value:
                        self.show_error(f"Value must be at least {min_value}")
                        continue
                    if max_value is not None and result > max_value:
                        self.show_error(f"Value must be at most {max_value}")
                        continue

                    return result
                except ValueError:
                    self.show_error("Please enter a valid number")
        except KeyboardInterrupt:
            self.show_error("Operation cancelled by user")
            sys.exit(1)

    def prompt_password(self, message: str = "Password") -> str:
        """Prompt user for password input."""
        try:
            while True:
                password = questionary.password(f"{message}:", style=self.style).ask()
                if not password:
                    self.show_error("Password cannot be empty")
                    continue
                return password
        except KeyboardInterrupt:
            self.show_error("Operation cancelled by user")
            sys.exit(1)

    def select(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        """Prompt user to select from choices."""
        try:
            if not choices:
                raise ValueError("Choices list cannot be empty")

            return select(message, choices=choices, default=default, style=self.style).ask()
        except KeyboardInterrupt:
            self.show_error("Operation cancelled by user")
            sys.exit(1)

    def pause(self, message: str = "Press Enter to continue..."):
        """Pause execution and wait for user input."""
        try:
            questionary.press_any_key_to_continue(message).ask()
        except KeyboardInterrupt:
            self.show_error("Operation cancelled by user")
            sys.exit(1)
