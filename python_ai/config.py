"""
Configuration Management Module

This module handles all application configuration using pydantic-settings.
It loads configuration from environment variables and .env files, providing
type-safe access to configuration values throughout the application.

Why pydantic-settings?
- Type validation ensures configuration errors are caught early
- Environment variable parsing with defaults
- Easy to test and mock
- Self-documenting through type hints
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings

    This class defines all configuration parameters for the therapy bot.
    Values are loaded from environment variables or .env file.

    Best Practices:
    - All sensitive data (API keys) should be in environment variables
    - Use .env for local development only
    - Never commit .env to version control
    """

    # ==================== Application Configuration ====================
    app_name: str = "TherapyBot"
    app_version: str = "1.0.0"
    environment: str = "development"

    # ==================== Server Configuration ====================
    host: str = "0.0.0.0"
    port: int = 8000

    # ==================== Database Configuration ====================
    # Using SQLite with async support for development
    # In production, consider PostgreSQL: postgresql+asyncpg://user:pass@localhost/db
    database_url: str = "sqlite+aiosqlite:///./data/users.db"

    # ==================== Logging Configuration ====================
    log_level: str = "INFO"
    log_file: str = "logs/therapy_bot.log"

    # ==================== Safety Configuration ====================
    # CRITICAL: Crisis detection is essential for therapy applications
    # This enables detection of suicidal ideation, self-harm, abuse, etc.
    crisis_detection_enabled: bool = True

    # Crisis hotline number to provide to users in crisis
    # 988 is the US Suicide & Crisis Lifeline
    crisis_hotline: str = "988"

    # Optional: Email address to send crisis alerts
    # Leave empty to disable email alerts
    crisis_alert_email: Optional[str] = None

    # ==================== Model Configuration ====================
    # For demo purposes, we use mock/rule-based models
    # In production, set to False and provide API keys below
    use_mock_models: bool = True

    # API Keys for production AI models (optional)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Embedding model for semantic routing
    # all-MiniLM-L6-v2 is lightweight and good for similarity tasks
    # Alternatives: all-mpnet-base-v2 (better but slower)
    embedding_model: str = "all-MiniLM-L6-v2"

    # ==================== Rate Limiting ====================
    # Prevent abuse and manage system load
    max_messages_per_hour: int = 30

    # ==================== Pydantic Settings Configuration ====================
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file if present
        env_file_encoding="utf-8",
        case_sensitive=False,  # Environment variables are case-insensitive
        extra="ignore"  # Ignore extra environment variables
    )


# Global settings instance
# This is imported by other modules to access configuration
# Example: from config import settings
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency injection function for FastAPI

    This allows FastAPI endpoints to access settings via dependency injection:

    @app.get("/status")
    async def status(config: Settings = Depends(get_settings)):
        return {"app": config.app_name}

    Benefits:
    - Easy to mock in tests
    - Clear dependencies in endpoint signatures
    - Follows FastAPI best practices
    """
    return settings
