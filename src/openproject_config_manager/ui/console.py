"""Rich-based console UI for the configuration manager."""

import sys
from typing import List, Optional, Any
import getpass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.syntax import Syntax
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule


class ConsoleUI:
    """Rich-based console user interface for configuration management."""
    
    def __init__(self):
        """Initialize the console UI."""
        self.console = Console()
        
    def show_title(self, title: str):
        """Show the main application title."""
        title_text = Text(title, style="bold bright_blue")
        title_panel = Panel(
            Align.center(title_text),
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print()
        self.console.print(title_panel)
        self.console.print()
    
    def show_phase_header(self, phase: str, description: str = ""):
        """Show a phase header with optional description."""
        phase_text = Text(f"Phase: {phase}", style="bold bright_green")
        if description:
            content = f"{phase_text}\\n{description}"
        else:
            content = phase_text
        
        phase_panel = Panel(
            content,
            border_style="bright_green",
            padding=(0, 1)
        )
        self.console.print()
        self.console.print(phase_panel)
    
    def show_section_header(self, section: str):
        """Show a section header."""
        self.console.print()
        self.console.print(Rule(f"[bold cyan]{section}[/bold cyan]"))
        self.console.print()
    
    def show_step(self, message: str):
        """Show a step message."""
        self.console.print(f"[bright_yellow]→[/bright_yellow] {message}")
    
    def show_success(self, message: str):
        """Show a success message."""
        self.console.print(f"[bright_green]✓[/bright_green] {message}")
    
    def show_error(self, message: str):
        """Show an error message."""
        self.console.print(f"[bright_red]✗[/bright_red] {message}")
    
    def show_warning(self, message: str):
        """Show a warning message."""
        self.console.print(f"[bright_yellow]⚠[/bright_yellow] {message}")
    
    def show_info(self, message: str):
        """Show an info message."""
        self.console.print(f"[bright_blue]ℹ[/bright_blue] {message}")
    
    def prompt(self, message: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
        """
        Prompt user for input.
        
        Args:
            message: Prompt message
            default: Default value
            allow_empty: Whether to allow empty input
            
        Returns:
            User input string
        """
        if default is not None:
            prompt_text = f"{message} [{default}]"
        else:
            prompt_text = message
        
        while True:
            try:
                result = Prompt.ask(prompt_text, default=default, console=self.console)
                if not allow_empty and not result:
                    self.show_error("This field is required")
                    continue
                return result
            except KeyboardInterrupt:
                self.show_error("\\nOperation cancelled by user")
                sys.exit(1)
    
    def prompt_int(self, message: str, default: Optional[int] = None, 
                   min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """
        Prompt user for integer input.
        
        Args:
            message: Prompt message
            default: Default value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            User input integer
        """
        if default is not None:
            prompt_text = f"{message} [{default}]"
        else:
            prompt_text = message
        
        while True:
            try:
                result = IntPrompt.ask(prompt_text, default=default, console=self.console)
                
                if min_value is not None and result < min_value:
                    self.show_error(f"Value must be at least {min_value}")
                    continue
                    
                if max_value is not None and result > max_value:
                    self.show_error(f"Value must be at most {max_value}")
                    continue
                    
                return result
            except KeyboardInterrupt:
                self.show_error("\\nOperation cancelled by user")
                sys.exit(1)
    
    def prompt_password(self, message: str = "Password") -> str:
        """
        Prompt user for password input (hidden).
        
        Args:
            message: Prompt message
            
        Returns:
            User input password
        """
        while True:
            try:
                password = getpass.getpass(f"{message}: ")
                if not password:
                    self.show_error("Password cannot be empty")
                    continue
                return password
            except KeyboardInterrupt:
                self.show_error("\\nOperation cancelled by user")
                sys.exit(1)
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Prompt user for yes/no confirmation.
        
        Args:
            message: Confirmation message
            default: Default value (True for yes, False for no)
            
        Returns:
            User confirmation boolean
        """
        try:
            return Confirm.ask(message, default=default, console=self.console)
        except KeyboardInterrupt:
            self.show_error("\\nOperation cancelled by user")
            sys.exit(1)
    
    def select(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        """
        Prompt user to select from a list of choices.
        
        Args:
            message: Selection message
            choices: List of available choices
            default: Default choice
            
        Returns:
            Selected choice
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")
        
        # Show choices
        self.console.print(f"\\n[bold]{message}[/bold]")
        for i, choice in enumerate(choices, 1):
            if choice == default:
                self.console.print(f"  {i}. [bright_green]{choice}[/bright_green] (default)")
            else:
                self.console.print(f"  {i}. {choice}")
        
        while True:
            try:
                # Get user input
                if default:
                    prompt_text = f"Select option (1-{len(choices)}) [{choices.index(default) + 1}]"
                    user_input = Prompt.ask(prompt_text, console=self.console)
                    
                    if not user_input:
                        return default
                else:
                    prompt_text = f"Select option (1-{len(choices)})"
                    user_input = Prompt.ask(prompt_text, console=self.console)
                
                # Validate input
                try:
                    choice_index = int(user_input) - 1
                    if 0 <= choice_index < len(choices):
                        return choices[choice_index]
                    else:
                        self.show_error(f"Please select a number between 1 and {len(choices)}")
                except ValueError:
                    self.show_error("Please enter a valid number")
                    
            except KeyboardInterrupt:
                self.show_error("\\nOperation cancelled by user")
                sys.exit(1)
    
    def show_progress(self, description: str = "Working..."):
        """
        Create and return a progress context manager.
        
        Args:
            description: Progress description
            
        Returns:
            Progress context manager
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
    
    def show_table(self, title: str, headers: List[str], rows: List[List[str]], 
                   show_header: bool = True):
        """
        Display a formatted table.
        
        Args:
            title: Table title
            headers: Column headers
            rows: Table rows
            show_header: Whether to show headers
        """
        table = Table(title=title, show_header=show_header, header_style="bold magenta")
        
        # Add columns
        for header in headers:
            table.add_column(header, style="cyan")
        
        # Add rows
        for row in rows:
            table.add_row(*row)
        
        self.console.print(table)
    
    def show_code(self, code: str, language: str = "bash", title: Optional[str] = None):
        """
        Display syntax-highlighted code.
        
        Args:
            code: Code to display
            language: Programming language for syntax highlighting
            title: Optional title for the code block
        """
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        
        if title:
            panel = Panel(syntax, title=title, border_style="bright_blue")
            self.console.print(panel)
        else:
            self.console.print(syntax)
    
    def show_json(self, data: dict, title: Optional[str] = None):
        """
        Display formatted JSON data.
        
        Args:
            data: Dictionary to display as JSON
            title: Optional title
        """
        import json
        json_str = json.dumps(data, indent=2, default=str)
        self.show_code(json_str, "json", title)
    
    def show_columns(self, items: List[str], columns: int = 3):
        """
        Display items in columns.
        
        Args:
            items: Items to display
            columns: Number of columns
        """
        # Create panels for each item
        panels = [Panel(item, expand=True) for item in items]
        
        # Group into columns
        column_groups = []
        for i in range(0, len(panels), columns):
            column_groups.append(panels[i:i + columns])
        
        # Display each group
        for group in column_groups:
            self.console.print(Columns(group, equal=True, expand=True))
    
    def clear_screen(self):
        """Clear the console screen."""
        self.console.clear()
    
    def pause(self, message: str = "Press Enter to continue..."):
        """
        Pause execution and wait for user input.
        
        Args:
            message: Message to display
        """
        try:
            self.console.input(f"\\n[dim]{message}[/dim]")
        except KeyboardInterrupt:
            self.show_error("\\nOperation cancelled by user")
            sys.exit(1)
    
    def show_spinner(self, message: str):
        """
        Show a spinner with message.
        
        Args:
            message: Message to display with spinner
            
        Returns:
            Progress context manager for spinner
        """
        return Progress(
            SpinnerColumn(),
            TextColumn(message),
            console=self.console,
            transient=True
        )
    
    def get_terminal_size(self) -> tuple:
        """
        Get terminal size.
        
        Returns:
            Tuple of (width, height)
        """
        return self.console.size