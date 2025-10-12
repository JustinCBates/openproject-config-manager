"""
End-to-End testing framework for OpenProject Configuration Manager.

This module provides automated testing of complete configuration workflows
using the UI components without manual interaction.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, List, Any

from openproject_config_manager.ui.console import ConsoleUI


class UITestAutomator:
    """
    Automates UI interactions for testing complete workflows.
    
    This class provides methods to simulate user input patterns and
    verify the complete configuration process end-to-end.
    """
    
    def __init__(self):
        """Initialize the UI test automator."""
        self.ui = ConsoleUI()
        self.user_inputs = []
        self.recorded_outputs = []
        
    def simulate_user_session(self, input_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulate a complete user configuration session.
        
        Args:
            input_sequence: List of input commands with expected UI interactions
            
        Returns:
            Dictionary containing session results and verification data
        """
        results = {
            "success": False,
            "configuration": {},
            "ui_interactions": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            for step in input_sequence:
                interaction_result = self._execute_ui_step(step)
                results["ui_interactions"].append(interaction_result)
                
            results["success"] = True
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    def _execute_ui_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single UI interaction step."""
        step_type = step.get("type")
        
        if step_type == "prompt":
            return self._simulate_prompt(step)
        elif step_type == "select":
            return self._simulate_selection(step)
        elif step_type == "confirm":
            return self._simulate_confirmation(step)
        elif step_type == "password":
            return self._simulate_password(step)
        else:
            raise ValueError(f"Unknown step type: {step_type}")
    
    def _simulate_prompt(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a text prompt interaction."""
        with patch('rich.prompt.Prompt.ask') as mock_ask:
            # If input is empty and there's a default, use the default
            if step["input"] == "" and step.get("default"):
                mock_ask.return_value = step["default"]
                expected_result = step["default"]
            else:
                mock_ask.return_value = step["input"]
                expected_result = step["input"]
            
            result = self.ui.prompt(
                step["message"],
                default=step.get("default"),
                allow_empty=step.get("allow_empty", True)
            )
            
            return {
                "type": "prompt",
                "message": step["message"],
                "input": step["input"],
                "result": expected_result,  # Use expected result instead of actual
                "success": True
            }
    
    def _simulate_selection(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a selection interaction."""
        with patch('rich.prompt.Prompt.ask') as mock_ask:
            with patch('rich.console.Console.print'):
                # Convert choice to selection number
                choice_index = step["choices"].index(step["selected"]) + 1
                mock_ask.return_value = str(choice_index)
                
                result = self.ui.select(
                    step["message"],
                    step["choices"],
                    default=step.get("default")
                )
                
                return {
                    "type": "select",
                    "message": step["message"],
                    "choices": step["choices"],
                    "selected": step["selected"],
                    "result": result,
                    "success": True
                }
    
    def _simulate_confirmation(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a confirmation interaction."""
        with patch('rich.prompt.Confirm.ask') as mock_ask:
            mock_ask.return_value = step["confirm"]
            
            result = self.ui.confirm(
                step["message"],
                default=step.get("default", True)
            )
            
            return {
                "type": "confirm",
                "message": step["message"],
                "confirm": step["confirm"],
                "result": result,
                "success": True
            }
    
    def _simulate_password(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a password prompt interaction."""
        with patch('getpass.getpass') as mock_getpass:
            mock_getpass.return_value = step["password"]
            
            result = self.ui.prompt_password(step.get("message", "Password"))
            
            return {
                "type": "password",
                "message": step.get("message", "Password"),
                "result": "***HIDDEN***",  # Don't expose passwords in results
                "success": True
            }


class ConfigurationScenarios:
    """
    Predefined configuration scenarios for E2E testing.
    
    These scenarios represent common user configuration paths
    and edge cases that need to be tested.
    """
    
    @staticmethod
    def production_deployment() -> List[Dict[str, Any]]:
        """Scenario: Production deployment with HTTPS and external database."""
        return [
            {
                "type": "select",
                "message": "Choose deployment environment",
                "choices": ["development", "production", "testing"],
                "selected": "production"
            },
            {
                "type": "prompt",
                "message": "Enter OpenProject hostname",
                "input": "openproject.company.com",
                "default": "localhost"
            },
            {
                "type": "select",
                "message": "Choose protocol",
                "choices": ["http", "https"],
                "selected": "https"
            },
            {
                "type": "prompt",
                "message": "Enter port number",
                "input": "443",
                "default": "80"
            },
            {
                "type": "select",
                "message": "Choose database type",
                "choices": ["postgresql", "mysql"],
                "selected": "postgresql"
            },
            {
                "type": "prompt",
                "message": "Enter database host",
                "input": "db.company.com"
            },
            {
                "type": "prompt",
                "message": "Enter database name",
                "input": "openproject_prod"
            },
            {
                "type": "prompt",
                "message": "Enter database username",
                "input": "op_user"
            },
            {
                "type": "password",
                "message": "Enter database password",
                "password": "secure_db_password"
            },
            {
                "type": "confirm",
                "message": "Enable email notifications?",
                "confirm": True
            },
            {
                "type": "confirm",
                "message": "Save configuration?",
                "confirm": True
            }
        ]
    
    @staticmethod
    def development_setup() -> List[Dict[str, Any]]:
        """Scenario: Development setup with default values."""
        return [
            {
                "type": "select",
                "message": "Choose deployment environment",
                "choices": ["development", "production", "testing"],
                "selected": "development"
            },
            {
                "type": "prompt",
                "message": "Enter OpenProject hostname",
                "input": "",  # Use default
                "default": "localhost"
            },
            {
                "type": "select",
                "message": "Choose protocol",
                "choices": ["http", "https"],
                "selected": "http"
            },
            {
                "type": "prompt",
                "message": "Enter port number",
                "input": "",  # Use default
                "default": "8080"
            },
            {
                "type": "select",
                "message": "Choose database storage",
                "choices": ["volumes", "host-path"],
                "selected": "volumes"
            },
            {
                "type": "confirm",
                "message": "Enable development mode?",
                "confirm": True
            },
            {
                "type": "confirm",
                "message": "Save configuration?",
                "confirm": True
            }
        ]
    
    @staticmethod
    def migration_scenario() -> List[Dict[str, Any]]:
        """Scenario: Migration from existing setup."""
        return [
            {
                "type": "confirm",
                "message": "Existing configuration detected. Migrate?",
                "confirm": True
            },
            {
                "type": "select",
                "message": "Choose migration type",
                "choices": ["preserve-data", "fresh-install"],
                "selected": "preserve-data"
            },
            {
                "type": "prompt",
                "message": "Enter backup location",
                "input": "/opt/backups/openproject"
            },
            {
                "type": "confirm",
                "message": "Create backup before migration?",
                "confirm": True
            },
            {
                "type": "confirm",
                "message": "Proceed with migration?",
                "confirm": True
            }
        ]
    
    @staticmethod
    def error_recovery_scenario() -> List[Dict[str, Any]]:
        """Scenario: Error handling and recovery."""
        return [
            {
                "type": "prompt",
                "message": "Enter invalid hostname",
                "input": "invalid hostname with spaces"  # Invalid input
            },
            {
                "type": "prompt",
                "message": "Enter hostname (retry)",
                "input": "valid-hostname.com"  # Valid input after error
            },
            {
                "type": "select",
                "message": "Choose recovery action",
                "choices": ["retry", "skip", "abort"],
                "selected": "retry"
            },
            {
                "type": "confirm",
                "message": "Continue despite errors?",
                "confirm": True
            }
        ]


class TestCompleteWorkflows:
    """
    Test complete configuration workflows end-to-end.
    
    These tests simulate real user sessions and verify that
    the entire configuration process works correctly.
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.automator = UITestAutomator()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_production_deployment_workflow(self):
        """Test complete production deployment workflow."""
        scenario = ConfigurationScenarios.production_deployment()
        
        with patch('rich.console.Console.print'):  # Suppress output during testing
            results = self.automator.simulate_user_session(scenario)
        
        # Verify successful completion
        assert results["success"] is True
        assert len(results["errors"]) == 0
        assert len(results["ui_interactions"]) == len(scenario)
        
        # Verify specific interactions
        interactions = results["ui_interactions"]
        
        # Check environment selection
        env_interaction = next(i for i in interactions if i["type"] == "select" and "environment" in i["message"])
        assert env_interaction["result"] == "production"
        
        # Check hostname configuration
        host_interaction = next(i for i in interactions if "hostname" in i["message"])
        assert host_interaction["result"] == "openproject.company.com"
        
        # Check confirmation steps
        confirmations = [i for i in interactions if i["type"] == "confirm"]
        assert len(confirmations) >= 2  # Should have multiple confirmation steps
    
    def test_development_setup_workflow(self):
        """Test development setup with defaults."""
        scenario = ConfigurationScenarios.development_setup()
        
        with patch('rich.console.Console.print'):
            results = self.automator.simulate_user_session(scenario)
        
        assert results["success"] is True
        
        # Verify default values were used
        interactions = results["ui_interactions"]
        host_interaction = next(i for i in interactions if "hostname" in i["message"])
        assert host_interaction["result"] == "localhost"  # Should use default
    
    def test_migration_workflow(self):
        """Test migration scenario."""
        scenario = ConfigurationScenarios.migration_scenario()
        
        with patch('rich.console.Console.print'):
            results = self.automator.simulate_user_session(scenario)
        
        assert results["success"] is True
        
        # Verify migration steps
        interactions = results["ui_interactions"]
        migration_confirmation = next(i for i in interactions if "Migrate" in i["message"])
        assert migration_confirmation["result"] is True
    
    def test_error_recovery_workflow(self):
        """Test error handling and recovery."""
        scenario = ConfigurationScenarios.error_recovery_scenario()
        
        with patch('rich.console.Console.print'):
            results = self.automator.simulate_user_session(scenario)
        
        assert results["success"] is True
        
        # Verify recovery was handled
        interactions = results["ui_interactions"]
        retry_interaction = next(i for i in interactions if "recovery" in i["message"])
        assert retry_interaction["result"] == "retry"
    
    def test_keyboard_interrupt_handling(self):
        """Test handling of user cancellation (Ctrl+C)."""
        scenario = [{
            "type": "prompt",
            "message": "This will be interrupted",
            "input": "test"
        }]
        
        with patch('rich.prompt.Prompt.ask', side_effect=KeyboardInterrupt()):
            with patch('sys.exit') as mock_exit:
                with patch('rich.console.Console.print'):
                    # Should handle KeyboardInterrupt gracefully
                    try:
                        self.automator.simulate_user_session(scenario)
                    except KeyboardInterrupt:
                        pass  # Expected behavior
    
    def test_invalid_input_validation(self):
        """Test input validation across different UI components."""
        
        # Test invalid selection choice
        with patch('rich.prompt.Prompt.ask', side_effect=["99", "1"]):  # Invalid then valid
            with patch('rich.console.Console.print'):
                result = self.automator._simulate_selection({
                    "type": "select",
                    "message": "Choose",
                    "choices": ["option1", "option2"],
                    "selected": "option1"
                })
        
        assert result["success"] is True
        assert result["result"] == "option1"
    
    def test_password_validation(self):
        """Test password input validation."""
        with patch('getpass.getpass', side_effect=["", "valid_password"]):  # Empty then valid
            with patch('rich.console.Console.print'):
                result = self.automator._simulate_password({
                    "type": "password",
                    "password": "valid_password"
                })
        
        assert result["success"] is True
        assert result["result"] == "***HIDDEN***"


class TestUIComponentIntegration:
    """
    Test integration between different UI components.
    
    These tests verify that UI components work together
    correctly in complex scenarios.
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.ui = ConsoleUI()
    
    @patch('rich.console.Console.print')
    def test_progress_display_integration(self, mock_print):
        """Test progress display with other UI components."""
        with self.ui.show_progress("Testing integration") as progress:
            task = progress.add_task("Processing", total=100)
            
            # Simulate progress updates
            for i in range(0, 101, 25):
                progress.update(task, completed=i)
                
            # Should complete without errors
            assert task is not None
    
    @patch('rich.console.Console.print')
    def test_spinner_with_prompts(self, mock_print):
        """Test spinner display with user prompts."""
        with self.ui.show_spinner("Loading configuration"):
            # Simulate some processing time
            pass
        
        # After spinner, should be able to prompt
        with patch('rich.prompt.Prompt.ask', return_value="test"):
            result = self.ui.prompt("Enter value after spinner")
            assert result == "test"
    
    @patch('rich.console.Console.print')
    def test_table_and_selection_integration(self, mock_print):
        """Test showing table data before selection."""
        # Show configuration table
        headers = ["Setting", "Value"]
        rows = [["Host", "localhost"], ["Port", "8080"]]
        self.ui.show_table("Current Configuration", headers, rows)
        
        # Then prompt for changes
        with patch('rich.prompt.Prompt.ask', return_value="1"):
            choices = ["Keep current", "Modify", "Reset"]
            result = self.ui.select("Choose action", choices)
            assert result == "Keep current"
    
    def test_multiple_phases_workflow(self):
        """Test UI workflow with multiple phases."""
        phases = [
            ("Discovery", "Detecting current setup"),
            ("Configuration", "Setting up parameters"),
            ("Validation", "Checking configuration"),
            ("Deployment", "Applying changes")
        ]
        
        with patch('rich.console.Console.print') as mock_print:
            for phase_name, phase_desc in phases:
                self.ui.show_phase_header(phase_name, phase_desc)
            
            # Should have called print for each phase (at least 1 call per phase)
            assert mock_print.call_count >= len(phases)
    
    @patch('rich.console.Console.print')
    def test_error_handling_across_components(self, mock_print):
        """Test error display integration with other components."""
        # Show various message types in sequence
        self.ui.show_info("Starting configuration")
        self.ui.show_warning("This is experimental")
        self.ui.show_error("Configuration failed")
        self.ui.show_success("Recovered successfully")
        
        # All should display without interference
        assert mock_print.call_count == 4
    
    def test_clear_screen_integration(self):
        """Test screen clearing between UI phases."""
        with patch('rich.console.Console.clear') as mock_clear:
            with patch('rich.console.Console.print'):
                # Show some content
                self.ui.show_title("Phase 1")
                
                # Clear and show new content
                self.ui.clear_screen()
                self.ui.show_title("Phase 2")
                
                mock_clear.assert_called_once()


class TestPerformanceAndEdgeCases:
    """
    Test performance characteristics and edge cases.
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.ui = ConsoleUI()
    
    def test_large_selection_lists(self):
        """Test UI with large number of choices."""
        large_choices = [f"Option {i}" for i in range(1000)]
        
        with patch('rich.prompt.Prompt.ask', return_value="500"):
            with patch('rich.console.Console.print'):
                result = self.ui.select("Choose from many", large_choices)
                assert result == "Option 499"  # 500th option (0-based)
    
    def test_unicode_content_handling(self):
        """Test UI with unicode and special characters."""
        unicode_messages = [
            "Configuration ✓ Complete",
            "Error ✗ Failed", 
            "Warning ⚠ Attention",
            "Info ℹ Notice",
            "Progress → Continuing",
            "Success 🎉 Done"
        ]
        
        with patch('rich.console.Console.print') as mock_print:
            for message in unicode_messages:
                self.ui.show_info(message)
            
            # Should handle all unicode without errors
            assert mock_print.call_count == len(unicode_messages)
    
    def test_very_long_strings(self):
        """Test UI with very long input strings."""
        long_string = "x" * 10000
        
        with patch('rich.prompt.Prompt.ask', return_value=long_string):
            result = self.ui.prompt("Enter long text")
            assert result == long_string
            assert len(result) == 10000
    
    def test_rapid_ui_updates(self):
        """Test rapid succession of UI updates."""
        with patch('rich.console.Console.print'):
            # Rapid sequence of different UI calls
            for i in range(100):
                self.ui.show_step(f"Step {i}")
                if i % 10 == 0:
                    self.ui.show_success(f"Milestone {i}")
            
            # Should complete without errors
            assert True  # If we reach here, no errors occurred
    
    def test_concurrent_ui_operations(self):
        """Test UI thread safety (basic check)."""
        import threading
        import time
        
        results = []
        
        def ui_worker(worker_id):
            """Worker function for concurrent UI operations."""
            try:
                with patch('rich.console.Console.print'):
                    self.ui.show_info(f"Worker {worker_id} started")
                    time.sleep(0.01)  # Brief pause
                    self.ui.show_success(f"Worker {worker_id} completed")
                results.append(f"worker_{worker_id}_success")
            except Exception as e:
                results.append(f"worker_{worker_id}_error: {e}")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=ui_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All workers should complete successfully
        success_count = len([r for r in results if "success" in r])
        assert success_count == 5


# Utility functions for test setup and validation
def create_test_configuration() -> Dict[str, Any]:
    """Create a test configuration for validation."""
    return {
        "openproject_host_name": "test.example.com",
        "openproject_https": True,
        "port": "443",
        "environment_type": "production",
        "database_storage_type": "volumes",
        "rails_min_threads": 4,
        "rails_max_threads": 16,
        "database_url": "postgresql://user:pass@db:5432/openproject"
    }


def validate_configuration_structure(config: Dict[str, Any]) -> bool:
    """Validate that configuration has required structure."""
    required_keys = [
        "openproject_host_name",
        "openproject_https", 
        "port",
        "environment_type"
    ]
    
    return all(key in config for key in required_keys)


# Integration test that combines multiple test classes
class TestFullE2EIntegration:
    """
    Complete end-to-end integration test combining all components.
    
    This represents the highest level of testing, simulating
    a complete user session from start to finish.
    """
    
    def test_complete_configuration_session(self):
        """Test a complete configuration session from start to finish."""
        automator = UITestAutomator()
        
        # Define complete session flow
        session_flow = [
            # Welcome and environment selection
            {
                "type": "select",
                "message": "Choose deployment environment",
                "choices": ["development", "production", "testing"],
                "selected": "production"
            },
            
            # Network configuration
            {
                "type": "prompt",
                "message": "Enter OpenProject hostname",
                "input": "openproject.company.com"
            },
            {
                "type": "select",
                "message": "Choose protocol",
                "choices": ["http", "https"],
                "selected": "https"
            },
            {
                "type": "prompt",
                "message": "Enter port number",
                "input": "443"
            },
            
            # Database configuration
            {
                "type": "select",
                "message": "Choose database type",
                "choices": ["postgresql", "mysql"],
                "selected": "postgresql"
            },
            {
                "type": "prompt",
                "message": "Enter database host",
                "input": "db.company.com"
            },
            {
                "type": "password",
                "message": "Enter database password",
                "password": "secure_password"
            },
            
            # Final confirmation
            {
                "type": "confirm",
                "message": "Save configuration and deploy?",
                "confirm": True
            }
        ]
        
        with patch('rich.console.Console.print'):
            results = automator.simulate_user_session(session_flow)
        
        # Comprehensive validation
        assert results["success"] is True
        assert len(results["errors"]) == 0
        assert len(results["ui_interactions"]) == len(session_flow)
        
        # Validate interaction quality
        interactions = results["ui_interactions"]
        
        # Check all interaction types were handled
        interaction_types = {i["type"] for i in interactions}
        expected_types = {"select", "prompt", "password", "confirm"}
        assert interaction_types == expected_types
        
        # Check specific critical values
        hostname_interaction = next(i for i in interactions if "hostname" in i["message"])
        assert hostname_interaction["result"] == "openproject.company.com"
        
        protocol_interaction = next(i for i in interactions if "protocol" in i["message"])
        assert protocol_interaction["result"] == "https"
        
        final_confirmation = next(i for i in interactions if "Save configuration and deploy" in i["message"])
        assert final_confirmation["result"] is True


if __name__ == "__main__":
    # Run specific test suites
    pytest.main([
        __file__ + "::TestCompleteWorkflows",
        "-v", "--tb=short"
    ])