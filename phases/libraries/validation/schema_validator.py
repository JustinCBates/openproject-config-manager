"""
Step: Schema Validation
Validate against configuration schema

Migrated from src/openproject_config_manager/validator/
"""

from pathlib import Path
from typing import Dict, List, Any
import logging
import yaml
import re
from dataclasses import dataclass
import sys


logger = logging.getLogger(__name__)


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""

    errors: List[str]
    warnings: List[str]
    passed: bool

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)


class SchemaValidator:
    """Validates configuration against schema requirements."""

    def __init__(self):
        """Initialize the schema validator."""
        pass

    def validate(self, configuration: Dict[str, Any]) -> SchemaValidationResult:
        """
        Validate configuration against schema.

        Args:
            configuration: Configuration dictionary to validate

        Returns:
            SchemaValidationResult with validation details
        """
        logger.info("Starting schema validation")

        result = SchemaValidationResult(errors=[], warnings=[], passed=True)

        # Extract user responses
        user_responses = configuration.get("user_responses", {})

        # Validate required sections
        self._validate_required_sections(user_responses, result)

        # Validate field types and formats
        self._validate_project_section(user_responses.get("project", {}), result)
        self._validate_admin_section(user_responses.get("admin", {}), result)
        self._validate_database_section(user_responses.get("database", {}), result)
        self._validate_network_section(user_responses.get("network", {}), result)

        logger.info(
            f"Schema validation completed: {'PASSED' if result.passed else 'FAILED'}"
        )
        logger.info(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

        return result

    def _validate_required_sections(
        self, user_responses: Dict[str, Any], result: SchemaValidationResult
    ):
        """Validate that all required sections exist."""
        required_sections = ["project", "admin", "database", "network"]

        for section in required_sections:
            if section not in user_responses:
                result.add_error(f"Required section '{section}' is missing")

    def _validate_project_section(
        self, project: Dict[str, Any], result: SchemaValidationResult
    ):
        """Validate project configuration."""
        # Project name validation
        if not project.get("name"):
            result.add_error("Project name is required")
        else:
            name = project["name"]
            if not re.match(r"^[a-z][a-z0-9-]*$", name):
                result.add_error(
                    "Project name must start with lowercase letter and contain only lowercase letters, numbers, and hyphens"
                )
            if len(name) < 3:
                result.add_error("Project name must be at least 3 characters")
            if len(name) > 50:
                result.add_error("Project name must be less than 50 characters")

        # Environment validation
        if not project.get("environment"):
            result.add_error("Project environment is required")
        elif project["environment"] not in ["development", "production"]:
            result.add_error(
                f"Invalid environment: {project['environment']}. Must be 'development' or 'production'"
            )

        if project.get("environment") == "development":
            result.add_warning(
                "Development environment is not recommended for production use"
            )

    def _validate_admin_section(
        self, admin: Dict[str, Any], result: SchemaValidationResult
    ):
        """Validate admin configuration."""
        # Email validation
        if not admin.get("email"):
            result.add_error("Admin email is required")
        elif not self._is_valid_email(admin["email"]):
            result.add_error(f"Invalid admin email format: {admin['email']}")

        # Password validation
        if not admin.get("password"):
            result.add_error("Admin password is required")
        elif len(admin["password"]) < 8:
            result.add_warning(
                "Admin password should be at least 8 characters for security"
            )

    def _validate_database_section(
        self, database: Dict[str, Any], result: SchemaValidationResult
    ):
        """Validate database configuration."""
        # Database type validation
        if not database.get("type"):
            result.add_error("Database type is required")
        elif database["type"] not in ["postgresql", "mysql"]:
            result.add_error(
                f"Unsupported database type: {database['type']}. Must be 'postgresql' or 'mysql'"
            )

        # Setup type validation
        if not database.get("setup"):
            result.add_error("Database setup type is required")
        elif database["setup"] not in ["container", "external"]:
            result.add_error(
                f"Invalid database setup: {database['setup']}. Must be 'container' or 'external'"
            )

        # External database requires host
        if database.get("setup") == "external":
            if not database.get("host"):
                result.add_error("External database requires host specification")

            if database.get("port"):
                port = database["port"]
                if not (1 <= port <= 65535):
                    result.add_error(f"Invalid database port: {port}")

    def _validate_network_section(
        self, network: Dict[str, Any], result: SchemaValidationResult
    ):
        """Validate network configuration."""
        # Domain validation
        if not network.get("domain"):
            result.add_error("Domain is required")
        else:
            domain = network["domain"]
            if not self._is_valid_domain(domain):
                result.add_error(f"Invalid domain format: {domain}")

            # Check for localhost/development domains
            if domain in ["localhost", "127.0.0.1"] or domain.endswith(".local"):
                result.add_warning(
                    "Using localhost/local domain - not suitable for production"
                )

    def _is_valid_email(self, email: str) -> bool:
        """Check if email format is valid."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain format is valid."""
        # Allow localhost and IP addresses
        if domain in ["localhost", "127.0.0.1"]:
            return True

        # Domain pattern
        pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        return bool(re.match(pattern, domain))


def execute_schema_validation(
    context: Dict[str, Any], phase_dir: Path
) -> Dict[str, Any]:
    """
    Schema Validation
    Status: IMPLEMENTED

    Validate against configuration schema

    Args:
        context: Execution context containing user_configuration_file
        phase_dir: Phase directory path

    Returns:
        Dict with step results including errors and warnings
    """
    logger.info("Executing step: Schema Validation")

    # Load collected configuration from Phase 3
    user_config_file = context.get("user_configuration_file")
    if not user_config_file:
        raise ValueError("user_configuration_file not found in context")

    with open(user_config_file, "r") as f:
        configuration = yaml.safe_load(f)

    # Run schema validation
    validator = SchemaValidator()
    validation_result = validator.validate(configuration)

    result = {
        "step": "schema_validation",
        "status": "completed",
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "passed": validation_result.passed,
    }

    logger.info(
        f"Schema validation completed: {'PASSED' if validation_result.passed else 'FAILED'}"
    )
    logger.info(
        f"Errors: {len(validation_result.errors)}, Warnings: {len(validation_result.warnings)}"
    )

    return result


def main():
    """Standalone entry point for testing this step."""
    import argparse

    parser = argparse.ArgumentParser(description="Schema Validation")
    parser.add_argument(
        "--user-config", required=True, help="Path to user_configuration.yml"
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
        context = {"user_configuration_file": args.user_config}

        # Execute step
        result = execute_schema_validation(context, phase_dir)

        print("\n" + "=" * 70)
        if result.get("passed", False):
            print("✅ Schema Validation PASSED")
        else:
            print("❌ Schema Validation FAILED")
        print("=" * 70)
        print(f"\n📊 Validation Results:")
        print(f"  • Errors: {len(result.get('errors', []))}")
        print(f"  • Warnings: {len(result.get('warnings', []))}")

        if result.get("errors"):
            print(f"\n❌ Errors:")
            for error in result["errors"]:
                print(f"    - {error}")

        if result.get("warnings"):
            print(f"\n⚠️  Warnings:")
            for warning in result["warnings"]:
                print(f"    - {warning}")

        return 0 if result.get("passed", False) else 1

    except Exception as e:
        print(f"\n❌ Step failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())


class SchemaValidationStep:
    """Wrapper class for schema_validation step."""

    def __init__(self, project_root: Path, ui=None):
        self.project_root = project_root
        self.ui = ui
        self.phase_dir = project_root / "phases/phase_4_validation"

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute schema_validation step.

        Args:
            context: Execution context

        Returns:
            Dict with artifacts
        """
        # Call existing function
        result_data = execute_schema_validation(context, self.phase_dir)

        # Return in expected format
        return {
            "artifacts": (
                result_data if isinstance(result_data, dict) else {"data": result_data}
            )
        }
