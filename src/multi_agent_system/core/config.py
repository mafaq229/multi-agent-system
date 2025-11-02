"""
Configuration management using pydantic-settings.

This module handles all application configuration from environment variables,
.env files, and provides validation and type safety.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    TODO: Implement complete settings class with all configuration parameters

    Requirements:
    1. Use pydantic-settings for automatic env var loading
    2. Provide sensible defaults for development
    3. Validate critical settings (e.g., API keys, URLs)
    4. Support multiple environments (dev, staging, prod)
    5. Use Field() for documentation and validation

    Example Implementation:
    ```python

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    ```

    Expected Input: Environment variables or .env file
    Expected Output: Validated settings object
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application Settings
    app_name: str = Field(default="multi-agent-system", description="Application Name")
    environment: str = Field(default="development", description="Environment Name")
    debug: bool = Field(default=False, description="Debug Mode")
    log_level: str = Field(default="INFO", description="Logging Level")

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API Host")
    api_port: int = Field(default=8000, description="API Port", ge=1, le=65535)
    api_workers: int = Field(default=4, description="Number of Workers", ge=1)

    # OpenAI Settings
    openai_api_key: str = Field(..., description="OpenAI API Key") # ... means required
    openai_model: str = Field(default="gpt-5", description="Model to Use")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API Base URL"
    )

    # Database Settings
    database_url: str = Field(
        default="sqlite:///./munder_difflin.db",
        description="Database Connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL Queries")

    # Redis Settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis Connection URL"
    )
    cache_ttl: int = Field(default=3600, description="Cache TTL in Seconds")

    # Security
    secret_key: str = Field(default="", description="Secret Key for Signing")  # TODO: Make required in production
    allowed_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed Hosts"
    )

    # Agent Settings
    agent_timeout: int = Field(default=30, description="Agent Timeout in Seconds")
    agent_max_retries: int = Field(default=3, description="Max Retries")

    # Business Logic
    default_inventory_coverage: float = Field(
        default=0.4,
        description="Default Inventory Coverage",
        ge=0.0,
        le=1.0
    )
    quote_validity_days: int = Field(
        default=30,
        description="Quote Validity in Days"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            msg = f"Environment must be one of: {allowed}"
            raise ValueError(msg)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            msg = f"Log level must be one of: {allowed}"
            raise ValueError(msg)
        return v.upper()


@lru_cache
def get_settings() -> Settings:
    """
    Get a globally cached Settings instance.

    Uses functools.lru_cache so that no matter how many times this function
    is called across your system (or from different modules), the Settings
    object is only loaded, parsed, and validated once per process. This
    ensures consistent configuration and improved performance by avoiding
    repeated file or environment variable loading.

    Returns:
        Settings: Application-wide settings (singleton per process)
    """
    return Settings()  # type: ignore
