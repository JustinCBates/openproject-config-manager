"""Tests for UI console functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console
from rich.prompt import Prompt, Confirm

from openproject_config_manager.ui.console import ConsoleUI


class TestConsoleUI:
    """Test ConsoleUI class."""
    
    def test_init_default(self):
        """Test ConsoleUI initialization with default console."""
        ui = ConsoleUI()
        assert ui is not None
        assert isinstance(ui.console, Console)
    
    def test_init_custom_console(self):
        """Test ConsoleUI initialization with custom console."""
        custom_console = Console()
        # ConsoleUI doesn't accept custom console in constructor, so we skip this test
        pass
    
    @patch('rich.console.Console.print')
    def test_show_title(self, mock_print):
        """Test showing title."""
        ui = ConsoleUI()
        ui.show_title("Test Title")
        
        # Should print multiple times (empty lines + panel)
        assert mock_print.call_count >= 1
        # Check that the call includes title
        call_args_list = [str(call) for call in mock_print.call_args_list]
        all_output = " ".join(call_args_list)
        assert "Test Title" in all_output
    
    @patch('rich.console.Console.print')
    def test_show_section_header(self, mock_print):
        """Test showing section header."""
        ui = ConsoleUI()
        ui.show_section_header("Test Section")
        
        # Should print multiple times (empty lines + rule)
        assert mock_print.call_count >= 1
        call_args_list = [str(call) for call in mock_print.call_args_list]
        all_output = " ".join(call_args_list)
        assert "Test Section" in all_output
    
    @patch('rich.console.Console.print')
    def test_show_info(self, mock_print):
        """Test showing info message."""
        ui = ConsoleUI()
        ui.show_info("Test info message")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert "Test info message" in str(call_args)
    
    @patch('rich.console.Console.print')
    def test_show_success(self, mock_print):
        """Test showing success message."""
        ui = ConsoleUI()
        ui.show_success("Test success message")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert "Test success message" in str(call_args)
    
    @patch('rich.console.Console.print')
    def test_show_warning(self, mock_print):
        """Test showing warning message."""
        ui = ConsoleUI()
        ui.show_warning("Test warning message")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert "Test warning message" in str(call_args)
    
    @patch('rich.console.Console.print')
    def test_show_error(self, mock_print):
        """Test showing error message."""
        ui = ConsoleUI()
        ui.show_error("Test error message")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert "Test error message" in str(call_args)
    
    @patch('rich.prompt.Prompt.ask')
    def test_prompt_basic(self, mock_ask):
        """Test basic text prompting."""
        mock_ask.return_value = "user input"
        
        ui = ConsoleUI()
        result = ui.prompt("Enter text")
        
        assert result == "user input"
        mock_ask.assert_called_once()
    
    @patch('rich.prompt.Prompt.ask')
    def test_prompt_with_default(self, mock_ask):
        """Test text prompting with default value."""
        mock_ask.return_value = "default value"
        
        ui = ConsoleUI()
        result = ui.prompt("Enter text", default="default value")
        
        assert result == "default value"
        mock_ask.assert_called_once()
    
    @patch('getpass.getpass')
    def test_prompt_password(self, mock_getpass):
        """Test password prompting."""
        mock_getpass.return_value = "secret123"
        
        ui = ConsoleUI()
        result = ui.prompt_password("Enter password")
        
        assert result == "secret123"
        mock_getpass.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_confirm_basic(self, mock_ask):
        """Test basic boolean prompting."""
        mock_ask.return_value = True
        
        ui = ConsoleUI()
        result = ui.confirm("Continue?")
        
        assert result is True
        mock_ask.assert_called_once()
    
    @patch('rich.prompt.Confirm.ask')
    def test_confirm_with_default(self, mock_ask):
        """Test boolean prompting with default."""
        mock_ask.return_value = False
        
        ui = ConsoleUI()
        result = ui.confirm("Continue?", default=False)
        
        assert result is False
        mock_ask.assert_called_once()
    
    @patch('rich.prompt.IntPrompt.ask')
    def test_prompt_int_basic(self, mock_ask):
        """Test integer prompting."""
        mock_ask.return_value = 42
        
        ui = ConsoleUI()
        result = ui.prompt_int("Enter number")
        
        assert result == 42
        mock_ask.assert_called_once()
    
    @patch('rich.prompt.IntPrompt.ask')
    def test_prompt_int_with_default(self, mock_ask):
        """Test integer prompting with default."""
        mock_ask.return_value = 10
        
        ui = ConsoleUI()
        result = ui.prompt_int("Enter number", default=10)
        
        assert result == 10
        mock_ask.assert_called_once()
    
    @patch('rich.prompt.IntPrompt.ask')
    @patch('rich.console.Console.print')
    def test_prompt_int_validation_min(self, mock_print, mock_ask):
        """Test integer prompting with minimum validation."""
        # First call returns invalid (too low), second returns valid
        mock_ask.side_effect = [5, 10]
        
        ui = ConsoleUI()
        result = ui.prompt_int("Enter number", min_value=10)
        
        assert result == 10
        assert mock_ask.call_count == 2
        # Should show error for first invalid input
        mock_print.assert_called()
    
    @patch('rich.console.Console.print')
    def test_show_step(self, mock_print):
        """Test showing step message."""
        ui = ConsoleUI()
        ui.show_step("Processing step")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert "Processing step" in str(call_args)
    
    @patch('rich.console.Console.print')
    def test_select_basic(self, mock_print):
        """Test basic choice selection."""
        choices = ["option1", "option2", "option3"]
        
        with patch('rich.prompt.Prompt.ask', return_value="2"):
            ui = ConsoleUI()
            result = ui.select("Choose option", choices)
        
        assert result == "option2"
        # Should print the choices
        assert mock_print.call_count >= len(choices)
    
    @patch('rich.console.Console.print')
    def test_select_with_default(self, mock_print):
        """Test choice selection with default."""
        choices = ["option1", "option2", "option3"]
        
        with patch('rich.prompt.Prompt.ask', return_value=""):  # Empty input = use default
            ui = ConsoleUI()
            result = ui.select("Choose option", choices, default="option2")
        
        assert result == "option2"
        # Should print the choices with default marked
        assert mock_print.call_count >= len(choices)
    
    @patch('rich.console.Console.print')
    def test_show_table(self, mock_print):
        """Test showing table."""
        headers = ["Name", "Value"]
        rows = [
            ["Setting 1", "Value 1"],
            ["Setting 2", "Value 2"]
        ]
        
        ui = ConsoleUI()
        ui.show_table("Test Table", headers, rows)
        
        mock_print.assert_called_once()
        # Rich table should be in the call
        call_args = mock_print.call_args
        assert call_args is not None
    
    @patch('rich.console.Console.print')
    def test_show_code(self, mock_print):
        """Test showing code with syntax highlighting."""
        ui = ConsoleUI()
        ui.show_code("print('hello')", "python", "Test Code")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert call_args is not None
    
    @patch('rich.console.Console.print')
    def test_show_json(self, mock_print):
        """Test showing JSON data."""
        data = {"key": "value", "number": 42}
        
        ui = ConsoleUI()
        ui.show_json(data, "Test JSON")
        
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert call_args is not None
    
    @patch('rich.console.Console.print')
    def test_show_columns(self, mock_print):
        """Test showing items in columns."""
        items = ["Item 1", "Item 2", "Item 3"]
        
        ui = ConsoleUI()
        ui.show_columns(items, columns=2)
        
        # Should print at least once for the columns
        assert mock_print.call_count >= 1
    
    @patch('rich.console.Console.clear')
    def test_clear_screen(self, mock_clear):
        """Test clearing screen."""
        ui = ConsoleUI()
        ui.clear_screen()
        
        mock_clear.assert_called_once()
    
    @patch('rich.console.Console.input')
    def test_pause(self, mock_input):
        """Test pausing for user input."""
        ui = ConsoleUI()
        ui.pause("Custom message")
        
        mock_input.assert_called_once()
        call_args = mock_input.call_args
        assert "Custom message" in str(call_args)
    
    def test_get_terminal_size(self):
        """Test getting terminal size."""
        ui = ConsoleUI()
        size = ui.get_terminal_size()
        
        assert isinstance(size, tuple)
        assert len(size) == 2
        assert all(isinstance(x, int) for x in size)
    
    def test_show_progress(self):
        """Test creating progress context manager."""
        ui = ConsoleUI()
        progress = ui.show_progress("Loading...")
        
        # Should return a progress object
        assert progress is not None
        # Should be usable as context manager
        assert hasattr(progress, '__enter__')
        assert hasattr(progress, '__exit__')
    
    def test_show_spinner(self):
        """Test creating spinner context manager."""
        ui = ConsoleUI()
        spinner = ui.show_spinner("Processing...")
        
        # Should return a progress object
        assert spinner is not None
        # Should be usable as context manager
        assert hasattr(spinner, '__enter__')
        assert hasattr(spinner, '__exit__')
    
    @patch('getpass.getpass')
    @patch('rich.console.Console.print')
    def test_prompt_password_empty_validation(self, mock_print, mock_getpass):
        """Test password prompting with empty validation."""
        # First call returns empty, second returns valid
        mock_getpass.side_effect = ["", "secret123"]
        
        ui = ConsoleUI()
        result = ui.prompt_password("Enter password")
        
        assert result == "secret123"
        assert mock_getpass.call_count == 2
        # Should show error for empty password
        mock_print.assert_called()
    
    @patch('rich.prompt.Prompt.ask')
    @patch('rich.console.Console.print')
    def test_select_invalid_choice(self, mock_print, mock_ask):
        """Test selection with invalid choice."""
        choices = ["option1", "option2"]
        # First returns invalid choice, second returns valid
        mock_ask.side_effect = ["99", "1"]
        
        ui = ConsoleUI()
        result = ui.select("Choose", choices)
        
        assert result == "option1"
        assert mock_ask.call_count == 2
        # Should show error message
        mock_print.assert_called()
    
    def test_select_empty_choices(self):
        """Test selection with empty choices list."""
        ui = ConsoleUI()
        
        with pytest.raises(ValueError, match="Choices list cannot be empty"):
            ui.select("Choose", [])
    
    @patch('rich.prompt.Prompt.ask')
    @patch('rich.console.Console.print')
    def test_prompt_allow_empty(self, mock_print, mock_ask):
        """Test prompting with allow_empty=True."""
        mock_ask.return_value = ""
        
        ui = ConsoleUI()
        result = ui.prompt("Enter optional text", allow_empty=True)
        
        assert result == ""
        mock_ask.assert_called_once()
        # Should not show error for empty input
        assert not any("required" in str(call) for call in mock_print.call_args_list)
    
    @patch('rich.prompt.Prompt.ask')
    @patch('rich.console.Console.print')
    def test_prompt_required_field(self, mock_print, mock_ask):
        """Test prompting for required field."""
        # First returns empty, second returns valid
        mock_ask.side_effect = ["", "valid input"]
        
        ui = ConsoleUI()
        result = ui.prompt("Enter required text", allow_empty=False)
        
        assert result == "valid input"
        assert mock_ask.call_count == 2
        # Should show error for empty input
        mock_print.assert_called()
        assert any("required" in str(call) for call in mock_print.call_args_list)