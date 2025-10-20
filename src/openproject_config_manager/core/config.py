"""Core configuration data models and types."""

import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConfigurationVariable(BaseModel):
    """Represents a single configuration variable."""

    name: str = Field(..., description="Variable name")
    value: Optional[str] = Field(None, description="Current value")
    default: Optional[str] = Field(None, description="Default value")
    description: str = Field(..., description="Human-readable description")
    category: str = Field(..., description="Variable category")
    required: bool = Field(True, description="Whether this variable is required")
    sensitive: bool = Field(False, description="Whether this is sensitive data")
    validation_pattern: Optional[str] = Field(
        None, description="Regex validation pattern"
    )
    choices: Optional[List[str]] = Field(None, description="Valid choices if limited")
    depends_on: Optional[List[str]] = Field(
        None, description="Dependencies on other variables"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Ensure variable name is valid."""
        if not v or not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Variable name must be alphanumeric with underscores/hyphens"
            )
        return v.upper()

    @property
    def effective_value(self) -> Optional[str]:
        """Get the effective value (value or default)."""
        return self.value if self.value is not None else self.default

    def is_valid(self) -> bool:
        """Check if current value is valid."""
        if self.required and not self.effective_value:
            return False

        if self.choices and self.effective_value:
            return self.effective_value in self.choices

        # Additional validation can be added here
        return True


class DatabaseConfig(BaseModel):
    """Database configuration section."""

    adapter: str = Field(
        default="postgresql", json_schema_extra={"choices": ["postgresql", "mysql"]}
    )
    host: str = Field(default="db")
    port: int = Field(default=5432)
    name: str = Field(default="openproject")
    username: str = Field(default="openproject")
    password: str = Field(..., description="Database password")
    encoding: str = Field(default="utf8")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class ProxyConfig(BaseModel):
    """Proxy and security configuration section."""

    domain: str = Field(..., description="Primary domain")
    additional_domains: Optional[List[str]] = Field(default_factory=list)
    ssl_enabled: bool = Field(default=True)
    ssl_cert_path: Optional[str] = Field(None)
    ssl_key_path: Optional[str] = Field(None)
    lets_encrypt: bool = Field(default=True)
    lets_encrypt_email: Optional[str] = Field(None)
    reverse_proxy_enabled: bool = Field(default=True)

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        if not v or "." not in v:
            raise ValueError("Domain must be a valid domain name")
        return v.lower()


class StorageConfig(BaseModel):
    """Storage and backup configuration section."""

    data_volume: str = Field(default="openproject_data")
    logs_volume: str = Field(default="openproject_logs")
    backup_enabled: bool = Field(default=True)
    backup_schedule: str = Field(default="0 2 * * *")  # Daily at 2 AM
    backup_retention_days: int = Field(default=30)
    backup_location: str = Field(default="./backups")

    @field_validator("backup_retention_days")
    @classmethod
    def validate_retention(cls, v):
        if v < 1:
            raise ValueError("Backup retention must be at least 1 day")
        return v


class Configuration(BaseModel):
    """Main configuration model containing all settings."""

    # Core OpenProject Settings
    secret_key_base: str = Field(..., description="OpenProject secret key")
    rails_env: str = Field(
        default="production",
        json_schema_extra={"choices": ["production", "development"]},
    )
    rails_cache_store: str = Field(default="memcache")

    # Database Configuration
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    # Proxy Configuration
    proxy: ProxyConfig

    # Storage Configuration
    storage: StorageConfig = Field(default_factory=StorageConfig)

    # Email Configuration
    email_delivery_method: str = Field(
        default="smtp",
        json_schema_extra={"choices": ["smtp", "sendmail", "letter_opener"]},
    )
    smtp_address: Optional[str] = Field(None)
    smtp_port: Optional[int] = Field(default=587)
    smtp_domain: Optional[str] = Field(None)
    smtp_user_name: Optional[str] = Field(None)
    smtp_password: Optional[str] = Field(None)
    smtp_enable_starttls_auto: bool = Field(default=True)

    # Cache Configuration
    memcached_server: str = Field(default="cache:11211")
    redis_url: Optional[str] = Field(None)

    # Performance Settings
    web_concurrency: int = Field(default=2)
    web_timeout: int = Field(default=60)
    web_max_requests: int = Field(default=1000)

    # Security Settings
    force_ssl: bool = Field(default=True)
    session_cookie_secure: bool = Field(default=True)

    # Feature Flags
    attachments_storage: str = Field(
        default="file", json_schema_extra={"choices": ["file", "fog"]}
    )
    fog_credentials: Optional[Dict[str, Any]] = Field(None)

    # Logging
    log_level: str = Field(
        default="info",
        json_schema_extra={"choices": ["debug", "info", "warn", "error"]},
    )
    rails_log_to_stdout: bool = Field(default=True)

    # Custom Variables (for extensions)
    custom_variables: Dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow", validate_assignment=True  # Allow additional fields
    )

    def to_cfg_format(self) -> str:
        """Export configuration to .cfg file format."""
        lines = []
        lines.append("# OpenProject Configuration")
        lines.append("# Generated by OpenProject Configuration Manager")
        lines.append("")

        # Core settings
        lines.append("# Core OpenProject Settings")
        lines.append(f'SECRET_KEY_BASE="{self.secret_key_base}"')
        lines.append(f'RAILS_ENV="{self.rails_env}"')
        lines.append(f'RAILS_CACHE_STORE="{self.rails_cache_store}"')
        lines.append("")

        # Database settings
        lines.append("# Database Configuration")
        lines.append(f'DATABASE_ADAPTER="{self.database.adapter}"')
        lines.append(f'DATABASE_HOST="{self.database.host}"')
        lines.append(f'DATABASE_PORT="{self.database.port}"')
        lines.append(f'DATABASE_NAME="{self.database.name}"')
        lines.append(f'DATABASE_USERNAME="{self.database.username}"')
        lines.append(f'DATABASE_PASSWORD="{self.database.password}"')
        lines.append(f'DATABASE_ENCODING="{self.database.encoding}"')
        lines.append("")

        # Proxy settings
        lines.append("# Proxy and Security Configuration")
        lines.append(f'DOMAIN="{self.proxy.domain}"')
        if self.proxy.additional_domains:
            lines.append(
                f'ADDITIONAL_DOMAINS="{",".join(self.proxy.additional_domains)}"'
            )
        lines.append(f'SSL_ENABLED="{str(self.proxy.ssl_enabled).lower()}"')
        if self.proxy.ssl_cert_path:
            lines.append(f'SSL_CERT_PATH="{self.proxy.ssl_cert_path}"')
        if self.proxy.ssl_key_path:
            lines.append(f'SSL_KEY_PATH="{self.proxy.ssl_key_path}"')
        lines.append(f'LETS_ENCRYPT="{str(self.proxy.lets_encrypt).lower()}"')
        if self.proxy.lets_encrypt_email:
            lines.append(f'LETS_ENCRYPT_EMAIL="{self.proxy.lets_encrypt_email}"')
        lines.append("")

        # Storage settings
        lines.append("# Storage Configuration")
        lines.append(f'DATA_VOLUME="{self.storage.data_volume}"')
        lines.append(f'LOGS_VOLUME="{self.storage.logs_volume}"')
        lines.append(f'BACKUP_ENABLED="{str(self.storage.backup_enabled).lower()}"')
        lines.append(f'BACKUP_SCHEDULE="{self.storage.backup_schedule}"')
        lines.append(f'BACKUP_RETENTION_DAYS="{self.storage.backup_retention_days}"')
        lines.append(f'BACKUP_LOCATION="{self.storage.backup_location}"')
        lines.append("")

        # Email settings
        lines.append("# Email Configuration")
        lines.append(f'EMAIL_DELIVERY_METHOD="{self.email_delivery_method}"')
        if self.smtp_address:
            lines.append(f'SMTP_ADDRESS="{self.smtp_address}"')
            lines.append(f'SMTP_PORT="{self.smtp_port}"')
            if self.smtp_domain:
                lines.append(f'SMTP_DOMAIN="{self.smtp_domain}"')
            if self.smtp_user_name:
                lines.append(f'SMTP_USER_NAME="{self.smtp_user_name}"')
            if self.smtp_password:
                lines.append(f'SMTP_PASSWORD="{self.smtp_password}"')
            lines.append(
                f'SMTP_ENABLE_STARTTLS_AUTO="{str(self.smtp_enable_starttls_auto).lower()}"'
            )
        lines.append("")

        # Cache settings
        lines.append("# Cache Configuration")
        lines.append(f'MEMCACHED_SERVER="{self.memcached_server}"')
        if self.redis_url:
            lines.append(f'REDIS_URL="{self.redis_url}"')
        lines.append("")

        # Performance settings
        lines.append("# Performance Settings")
        lines.append(f'WEB_CONCURRENCY="{self.web_concurrency}"')
        lines.append(f'WEB_TIMEOUT="{self.web_timeout}"')
        lines.append(f'WEB_MAX_REQUESTS="{self.web_max_requests}"')
        lines.append("")

        # Security settings
        lines.append("# Security Settings")
        lines.append(f'FORCE_SSL="{str(self.force_ssl).lower()}"')
        lines.append(
            f'SESSION_COOKIE_SECURE="{str(self.session_cookie_secure).lower()}"'
        )
        lines.append("")

        # URL Configuration
        lines.append("# URL Configuration")
        lines.append(
            f'URI_NAMESPACE_ENABLED="{str(getattr(self, "uri_namespace_enabled", False)).lower()}"'
        )
        lines.append(f'URI_NAMESPACE="{getattr(self, "uri_namespace", "")}"')
        lines.append("")

        # Feature settings
        lines.append("# Feature Configuration")
        lines.append(f'ATTACHMENTS_STORAGE="{self.attachments_storage}"')
        lines.append("")

        # Logging settings
        lines.append("# Logging Configuration")
        lines.append(f'LOG_LEVEL="{self.log_level}"')
        lines.append(f'RAILS_LOG_TO_STDOUT="{str(self.rails_log_to_stdout).lower()}"')
        lines.append("")

        # Custom variables
        if self.custom_variables:
            lines.append("# Custom Variables")
            for key, value in self.custom_variables.items():
                lines.append(f'{key}="{value}"')
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_cfg_file(cls, filepath: Union[str, Path]) -> "Configuration":
        """Load configuration from .cfg file."""
        config_data = {}

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    config_data[key.strip()] = value

        # Convert flat config to nested structure
        database_config = DatabaseConfig(
            adapter=config_data.get("DATABASE_ADAPTER", "postgresql"),
            host=config_data.get("DATABASE_HOST", "db"),
            port=int(config_data.get("DATABASE_PORT", 5432)),
            name=config_data.get("DATABASE_NAME", "openproject"),
            username=config_data.get("DATABASE_USERNAME", "openproject"),
            password=config_data.get("DATABASE_PASSWORD", ""),
            encoding=config_data.get("DATABASE_ENCODING", "utf8"),
        )

        proxy_config = ProxyConfig(
            domain=config_data.get("DOMAIN", ""),
            additional_domains=(
                config_data.get("ADDITIONAL_DOMAINS", "").split(",")
                if config_data.get("ADDITIONAL_DOMAINS")
                else []
            ),
            ssl_enabled=config_data.get("SSL_ENABLED", "true").lower() == "true",
            ssl_cert_path=config_data.get("SSL_CERT_PATH"),
            ssl_key_path=config_data.get("SSL_KEY_PATH"),
            lets_encrypt=config_data.get("LETS_ENCRYPT", "true").lower() == "true",
            lets_encrypt_email=config_data.get("LETS_ENCRYPT_EMAIL"),
            reverse_proxy_enabled=config_data.get(
                "REVERSE_PROXY_ENABLED", "true"
            ).lower()
            == "true",
        )

        storage_config = StorageConfig(
            data_volume=config_data.get("DATA_VOLUME", "openproject_data"),
            logs_volume=config_data.get("LOGS_VOLUME", "openproject_logs"),
            backup_enabled=config_data.get("BACKUP_ENABLED", "true").lower() == "true",
            backup_schedule=config_data.get("BACKUP_SCHEDULE", "0 2 * * *"),
            backup_retention_days=int(config_data.get("BACKUP_RETENTION_DAYS", 30)),
            backup_location=config_data.get("BACKUP_LOCATION", "./backups"),
        )

        return cls(
            secret_key_base=config_data.get("SECRET_KEY_BASE", ""),
            rails_env=config_data.get("RAILS_ENV", "production"),
            rails_cache_store=config_data.get("RAILS_CACHE_STORE", "memcache"),
            database=database_config,
            proxy=proxy_config,
            storage=storage_config,
            email_delivery_method=config_data.get("EMAIL_DELIVERY_METHOD", "smtp"),
            smtp_address=config_data.get("SMTP_ADDRESS"),
            smtp_port=(
                int(config_data.get("SMTP_PORT", 587))
                if config_data.get("SMTP_PORT")
                else 587
            ),
            smtp_domain=config_data.get("SMTP_DOMAIN"),
            smtp_user_name=config_data.get("SMTP_USER_NAME"),
            smtp_password=config_data.get("SMTP_PASSWORD"),
            smtp_enable_starttls_auto=config_data.get(
                "SMTP_ENABLE_STARTTLS_AUTO", "true"
            ).lower()
            == "true",
            memcached_server=config_data.get("MEMCACHED_SERVER", "cache:11211"),
            redis_url=config_data.get("REDIS_URL"),
            web_concurrency=int(config_data.get("WEB_CONCURRENCY", 2)),
            web_timeout=int(config_data.get("WEB_TIMEOUT", 60)),
            web_max_requests=int(config_data.get("WEB_MAX_REQUESTS", 1000)),
            force_ssl=config_data.get("FORCE_SSL", "true").lower() == "true",
            session_cookie_secure=config_data.get(
                "SESSION_COOKIE_SECURE", "true"
            ).lower()
            == "true",
            attachments_storage=config_data.get("ATTACHMENTS_STORAGE", "file"),
            log_level=config_data.get("LOG_LEVEL", "info"),
            rails_log_to_stdout=config_data.get("RAILS_LOG_TO_STDOUT", "true").lower()
            == "true",
            uri_namespace_enabled=config_data.get(
                "URI_NAMESPACE_ENABLED", "false"
            ).lower()
            == "true",
            uri_namespace=config_data.get("URI_NAMESPACE", ""),
        )
