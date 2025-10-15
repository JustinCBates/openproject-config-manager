"""Configuration validation with comprehensive checks and live testing."""

import logging
import os
import re
import socket
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.config import Configuration

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def add_recommendation(self, message: str):
        """Add a recommendation."""
        self.recommendations.append(message)


class ConfigurationValidator:
    """Comprehensive configuration validator with live testing capabilities."""

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_configuration(
        self, configuration: Configuration, discovered_data: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a configuration comprehensively.

        Args:
            configuration: Configuration to validate
            discovered_data: Optional discovered environment data

        Returns:
            ValidationResult with validation details
        """
        logger.info("Starting configuration validation")

        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        discovered_data = discovered_data or {}

        # Core validation
        self._validate_core_settings(configuration, result)

        # Database validation
        self._validate_database_config(configuration.database, result, discovered_data)

        # Proxy validation
        self._validate_proxy_config(configuration.proxy, result)

        # Storage validation
        self._validate_storage_config(configuration.storage, result)

        # Email validation
        self._validate_email_config(configuration, result)

        # Performance validation
        self._validate_performance_config(configuration, result, discovered_data)

        # Security validation
        self._validate_security_config(configuration, result)

        # Cross-validation checks
        self._validate_configuration_consistency(configuration, result)

        # Environment-specific validation
        self._validate_environment_compatibility(configuration, result, discovered_data)

        logger.info(f"Validation completed: {'PASSED' if result.is_valid else 'FAILED'}")
        logger.info(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

        return result

    def _validate_core_settings(self, configuration: Configuration, result: ValidationResult):
        """Validate core OpenProject settings."""
        # Secret key validation
        if not configuration.secret_key_base:
            result.add_error("SECRET_KEY_BASE is required")
        elif len(configuration.secret_key_base) < 64:
            result.add_warning("SECRET_KEY_BASE should be at least 64 characters for security")

        # Rails environment validation
        if configuration.rails_env not in ["production", "development"]:
            result.add_error(f"Invalid RAILS_ENV: {configuration.rails_env}")

        if configuration.rails_env == "development":
            result.add_warning("Development environment is not recommended for production use")

        # Cache store validation
        if configuration.rails_cache_store not in ["memcache", "redis", "file_store"]:
            result.add_error(f"Invalid RAILS_CACHE_STORE: {configuration.rails_cache_store}")

    def _validate_database_config(
        self, db_config, result: ValidationResult, discovered_data: Dict[str, Any]
    ):
        """Validate database configuration."""
        # Adapter validation
        if db_config.adapter not in ["postgresql", "mysql"]:
            result.add_error(f"Unsupported database adapter: {db_config.adapter}")

        # Host validation
        if not db_config.host:
            result.add_error("Database host is required")
        else:
            # Check if host is reachable (if not localhost/container name)
            if not self._is_container_or_localhost(db_config.host):
                if not self._test_host_connectivity(db_config.host, db_config.port):
                    result.add_warning(
                        f"Cannot reach database host {db_config.host}:{db_config.port}"
                    )

        # Port validation
        if not (1 <= db_config.port <= 65535):
            result.add_error(f"Invalid database port: {db_config.port}")

        # Standard ports check
        if db_config.adapter == "postgresql" and db_config.port != 5432:
            result.add_recommendation(
                f"Non-standard PostgreSQL port {db_config.port} (standard is 5432)"
            )
        elif db_config.adapter == "mysql" and db_config.port != 3306:
            result.add_recommendation(
                f"Non-standard MySQL port {db_config.port} (standard is 3306)"
            )

        # Database name validation
        if not db_config.name:
            result.add_error("Database name is required")
        elif not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", db_config.name):
            result.add_warning(
                "Database name should start with a letter and contain only alphanumeric characters and underscores"
            )

        # Username validation
        if not db_config.username:
            result.add_error("Database username is required")

        # Password validation
        if not db_config.password:
            result.add_error("Database password is required")
        elif len(db_config.password) < 8:
            result.add_warning("Database password should be at least 8 characters")

        # Check for existing database containers
        docker_data = discovered_data.get("docker", {})
        db_containers = docker_data.get("database_containers", [])

        if db_containers:
            # Check if specified host matches an existing container
            matching_containers = [c for c in db_containers if c["name"] == db_config.host]
            if matching_containers:
                container = matching_containers[0]
                container_type = container.get("database_type", "unknown")

                if db_config.adapter == "postgresql" and "postgres" not in container_type:
                    result.add_warning(
                        f"Container {db_config.host} appears to be {container_type}, but PostgreSQL adapter is configured"
                    )
                elif db_config.adapter == "mysql" and "mysql" not in container_type:
                    result.add_warning(
                        f"Container {db_config.host} appears to be {container_type}, but MySQL adapter is configured"
                    )

    def _validate_proxy_config(self, proxy_config, result: ValidationResult):
        """Validate proxy and SSL configuration."""
        # Domain validation
        if not proxy_config.domain:
            result.add_error("Primary domain is required")
        else:
            if not self._is_valid_domain(proxy_config.domain):
                result.add_error(f"Invalid domain format: {proxy_config.domain}")

            # Check for localhost/development domains
            if proxy_config.domain in ["localhost", "127.0.0.1"] or proxy_config.domain.endswith(
                ".local"
            ):
                result.add_warning("Using localhost/local domain - not suitable for production")

        # Additional domains validation
        for domain in proxy_config.additional_domains:
            if not self._is_valid_domain(domain):
                result.add_warning(f"Invalid additional domain format: {domain}")

        # SSL configuration validation
        if proxy_config.ssl_enabled:
            if proxy_config.lets_encrypt:
                # Let's Encrypt validation
                if not proxy_config.lets_encrypt_email:
                    result.add_error(
                        "Let's Encrypt email is required when Let's Encrypt is enabled"
                    )
                elif not self._is_valid_email(proxy_config.lets_encrypt_email):
                    result.add_error(
                        f"Invalid Let's Encrypt email format: {proxy_config.lets_encrypt_email}"
                    )

                # Check domain compatibility with Let's Encrypt
                if proxy_config.domain.endswith(".local") or proxy_config.domain in [
                    "localhost",
                    "127.0.0.1",
                ]:
                    result.add_error(
                        "Let's Encrypt cannot issue certificates for localhost/local domains"
                    )
            else:
                # Custom SSL certificate validation
                if proxy_config.ssl_cert_path:
                    if not Path(proxy_config.ssl_cert_path).exists():
                        result.add_warning(
                            f"SSL certificate file not found: {proxy_config.ssl_cert_path}"
                        )
                else:
                    result.add_warning("SSL enabled but no certificate path specified")

                if proxy_config.ssl_key_path:
                    if not Path(proxy_config.ssl_key_path).exists():
                        result.add_warning(
                            f"SSL private key file not found: {proxy_config.ssl_key_path}"
                        )
                else:
                    result.add_warning("SSL enabled but no private key path specified")
        else:
            result.add_warning("SSL is disabled - not recommended for production")

    def _validate_storage_config(self, storage_config, result: ValidationResult):
        """Validate storage and backup configuration."""
        # Volume names validation
        if not storage_config.data_volume:
            result.add_error("Data volume name is required")
        elif not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", storage_config.data_volume):
            result.add_warning(
                "Data volume name should start with a letter and contain only alphanumeric characters, hyphens, and underscores"
            )

        if not storage_config.logs_volume:
            result.add_error("Logs volume name is required")
        elif not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", storage_config.logs_volume):
            result.add_warning(
                "Logs volume name should start with a letter and contain only alphanumeric characters, hyphens, and underscores"
            )

        # Backup configuration validation
        if storage_config.backup_enabled:
            # Backup schedule validation (cron format)
            if not self._is_valid_cron_schedule(storage_config.backup_schedule):
                result.add_error(
                    f"Invalid backup schedule format: {storage_config.backup_schedule}"
                )

            # Backup retention validation
            if storage_config.backup_retention_days < 1:
                result.add_error("Backup retention must be at least 1 day")
            elif storage_config.backup_retention_days > 365:
                result.add_warning("Backup retention over 1 year may consume significant storage")

            # Backup location validation
            if not storage_config.backup_location:
                result.add_error("Backup location is required when backups are enabled")
            else:
                backup_path = Path(storage_config.backup_location)
                if backup_path.is_absolute():
                    # Check if parent directory exists
                    if not backup_path.parent.exists():
                        result.add_warning(
                            f"Backup location parent directory does not exist: {backup_path.parent}"
                        )
                else:
                    # Relative path - check if it makes sense
                    if not backup_path.name:
                        result.add_warning("Backup location should be a valid directory path")

    def _validate_email_config(self, configuration: Configuration, result: ValidationResult):
        """Validate email configuration."""
        if configuration.email_delivery_method not in ["smtp", "sendmail", "letter_opener"]:
            result.add_error(
                f"Invalid email delivery method: {configuration.email_delivery_method}"
            )

        if configuration.email_delivery_method == "smtp":
            # SMTP configuration validation
            if not configuration.smtp_address:
                result.add_error("SMTP address is required for SMTP delivery")
            else:
                # Test SMTP host reachability
                if not self._test_host_connectivity(
                    configuration.smtp_address, configuration.smtp_port
                ):
                    result.add_warning(
                        f"Cannot reach SMTP server {configuration.smtp_address}:{configuration.smtp_port}"
                    )

            # Port validation
            if not (1 <= configuration.smtp_port <= 65535):
                result.add_error(f"Invalid SMTP port: {configuration.smtp_port}")

            # Standard SMTP ports check
            standard_ports = [25, 465, 587, 2525]
            if configuration.smtp_port not in standard_ports:
                result.add_recommendation(
                    f"Non-standard SMTP port {configuration.smtp_port} (standard ports: {standard_ports})"
                )

            # Domain validation
            if configuration.smtp_domain and not self._is_valid_domain(configuration.smtp_domain):
                result.add_warning(f"Invalid SMTP domain format: {configuration.smtp_domain}")

            # Authentication check
            if configuration.smtp_user_name and not configuration.smtp_password:
                result.add_warning("SMTP username provided but no password set")

        elif configuration.email_delivery_method == "letter_opener":
            result.add_warning(
                "Letter opener is for development only - not suitable for production"
            )

    def _validate_performance_config(
        self,
        configuration: Configuration,
        result: ValidationResult,
        discovered_data: Dict[str, Any],
    ):
        """Validate performance configuration."""
        # Web concurrency validation
        if configuration.web_concurrency < 1:
            result.add_error("Web concurrency must be at least 1")
        elif configuration.web_concurrency > 16:
            result.add_warning("Very high web concurrency may cause resource issues")

        # Check against system resources
        system_data = discovered_data.get("system", {})
        hardware_info = system_data.get("hardware", {})

        if "cpu_count" in hardware_info:
            cpu_count = hardware_info["cpu_count"]
            if configuration.web_concurrency > cpu_count * 2:
                result.add_warning(
                    f"Web concurrency ({configuration.web_concurrency}) is high for {cpu_count} CPU cores"
                )

        if "memory" in hardware_info and "total_gb" in hardware_info["memory"]:
            memory_gb = hardware_info["memory"]["total_gb"]
            estimated_memory_per_worker = 0.5  # GB
            estimated_total = configuration.web_concurrency * estimated_memory_per_worker

            if estimated_total > memory_gb * 0.8:  # 80% of available memory
                result.add_warning(
                    f"High memory usage expected: {estimated_total:.1f}GB for {configuration.web_concurrency} workers"
                )

        # Timeout validation
        if configuration.web_timeout < 30:
            result.add_warning("Very short web timeout may cause request failures")
        elif configuration.web_timeout > 300:
            result.add_warning("Very long web timeout may cause resource issues")

        # Max requests validation
        if configuration.web_max_requests < 100:
            result.add_warning(
                "Very low max requests per worker may cause frequent worker restarts"
            )
        elif configuration.web_max_requests > 10000:
            result.add_warning("Very high max requests per worker may cause memory leaks")

        # Cache configuration validation
        if configuration.rails_cache_store == "memcache":
            if not configuration.memcached_server:
                result.add_error("Memcached server is required for memcache store")
            else:
                # Test memcached connectivity
                host, port = self._parse_server_address(configuration.memcached_server, 11211)
                if not self._test_host_connectivity(host, port):
                    result.add_warning(f"Cannot reach Memcached server {host}:{port}")

        elif configuration.rails_cache_store == "redis":
            if not configuration.redis_url:
                result.add_error("Redis URL is required for redis cache store")
            else:
                # Parse and validate Redis URL
                if not self._is_valid_redis_url(configuration.redis_url):
                    result.add_error(f"Invalid Redis URL format: {configuration.redis_url}")

    def _validate_security_config(self, configuration: Configuration, result: ValidationResult):
        """Validate security configuration."""
        # SSL enforcement
        if not configuration.force_ssl and configuration.rails_env == "production":
            result.add_warning("SSL enforcement disabled in production - security risk")

        # Session cookie security
        if not configuration.session_cookie_secure and configuration.proxy.ssl_enabled:
            result.add_warning("Session cookies should be secure when SSL is enabled")

        # Secret key entropy check
        if configuration.secret_key_base:
            if self._is_weak_secret_key(configuration.secret_key_base):
                result.add_warning("Secret key appears to have low entropy - consider regenerating")

    def _validate_configuration_consistency(
        self, configuration: Configuration, result: ValidationResult
    ):
        """Validate configuration consistency across components."""
        # SSL consistency checks
        if configuration.proxy.ssl_enabled and not configuration.force_ssl:
            result.add_recommendation("Consider enabling force_ssl when SSL is configured")

        if configuration.proxy.ssl_enabled and not configuration.session_cookie_secure:
            result.add_recommendation(
                "Consider enabling secure session cookies when SSL is configured"
            )

        # Environment consistency
        if configuration.rails_env == "development":
            if configuration.proxy.ssl_enabled and configuration.proxy.lets_encrypt:
                result.add_warning(
                    "Let's Encrypt with development environment may not work as expected"
                )

        # Cache consistency
        if configuration.rails_cache_store == "memcache" and not configuration.memcached_server:
            result.add_error("Memcache store selected but no memcached server configured")

        if configuration.rails_cache_store == "redis" and not configuration.redis_url:
            result.add_error("Redis store selected but no Redis URL configured")

        # Database adapter consistency
        if configuration.database.adapter == "postgresql" and configuration.database.port == 3306:
            result.add_warning(
                "PostgreSQL adapter with MySQL default port - possible misconfiguration"
            )
        elif configuration.database.adapter == "mysql" and configuration.database.port == 5432:
            result.add_warning(
                "MySQL adapter with PostgreSQL default port - possible misconfiguration"
            )

    def _validate_environment_compatibility(
        self,
        configuration: Configuration,
        result: ValidationResult,
        discovered_data: Dict[str, Any],
    ):
        """Validate configuration against discovered environment."""
        # Docker compatibility
        docker_data = discovered_data.get("docker", {})
        if not docker_data.get("docker_available"):
            result.add_error("Docker is not available but required for deployment")

        # System resources check
        system_data = discovered_data.get("system", {})
        hardware_info = system_data.get("hardware", {})

        # Memory check
        if "memory" in hardware_info and "total_gb" in hardware_info["memory"]:
            memory_gb = hardware_info["memory"]["total_gb"]
            if memory_gb < 2:
                result.add_warning(
                    f"Low system memory ({memory_gb:.1f}GB) - consider upgrading for production"
                )
            elif memory_gb < 4:
                result.add_recommendation(
                    f"Moderate system memory ({memory_gb:.1f}GB) - 4GB+ recommended for production"
                )

        # Disk space check
        if "disk" in hardware_info and "free_gb" in hardware_info["disk"]:
            free_gb = hardware_info["disk"]["free_gb"]
            if free_gb < 10:
                result.add_warning(
                    f"Low disk space ({free_gb:.1f}GB free) - ensure adequate space for data and backups"
                )

        # Network connectivity for external services
        if configuration.proxy.lets_encrypt:
            # Check if we can reach Let's Encrypt
            if not self._test_host_connectivity("acme-v02.api.letsencrypt.org", 443):
                result.add_warning(
                    "Cannot reach Let's Encrypt servers - check internet connectivity"
                )

    # Helper methods

    def _is_container_or_localhost(self, host: str) -> bool:
        """Check if host is likely a container name or localhost."""
        localhost_variants = ["localhost", "127.0.0.1", "::1"]
        return host in localhost_variants or not ("." in host and len(host.split(".")) >= 2)

    def _test_host_connectivity(self, host: str, port: int, timeout: int = 5) -> bool:
        """Test if a host:port is reachable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain name format."""
        if not domain or len(domain) > 253:
            return False

        # Basic domain validation
        domain_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        return re.match(domain_pattern, domain) is not None

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email) is not None

    def _is_valid_cron_schedule(self, schedule: str) -> bool:
        """Validate cron schedule format."""
        if not schedule:
            return False

        parts = schedule.split()
        if len(parts) != 5:
            return False

        # Basic validation of cron fields
        ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]  # min, hour, day, month, weekday

        for i, (part, (min_val, max_val)) in enumerate(zip(parts, ranges)):
            if part == "*":
                continue

            try:
                # Handle ranges and lists
                if "," in part:
                    values = part.split(",")
                elif "-" in part:
                    start, end = part.split("-", 1)
                    values = [start, end]
                else:
                    values = [part]

                for value in values:
                    if "/" in value:
                        value = value.split("/")[0]

                    num = int(value)
                    if not (min_val <= num <= max_val):
                        return False
            except ValueError:
                return False

        return True

    def _parse_server_address(self, address: str, default_port: int) -> Tuple[str, int]:
        """Parse server address into host and port."""
        if ":" in address:
            host, port_str = address.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                return address, default_port
            return host, port
        return address, default_port

    def _is_valid_redis_url(self, url: str) -> bool:
        """Validate Redis URL format."""
        redis_pattern = r"^redis://([^:@]+:[^:@]+@)?[^:/]+:\d+(/\d+)?$"
        return re.match(redis_pattern, url) is not None

    def _is_weak_secret_key(self, secret_key: str) -> bool:
        """Check if secret key has low entropy."""
        if len(secret_key) < 64:
            return True

        # Check for repeated patterns
        if len(set(secret_key)) < len(secret_key) * 0.5:
            return True

        # Check for simple patterns
        weak_patterns = ["123456", "abcdef", "password", "secret"]
        for pattern in weak_patterns:
            if pattern in secret_key.lower():
                return True

        return False
