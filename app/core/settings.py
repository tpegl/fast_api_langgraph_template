import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fast API LangGraph Template"
    debug: bool = False
    log_level: str = "DEBUG"
    environment: str = "dev"

    secret_key: str = os.getenv("SECRET_KEY", "")

    cors_origins: list[str] = ["http://localhost:5173"]

    # LangGraph service configuration
    langsmith_url: str = "http://localhost:2024"  # Default for local development
    langsmith_api_key: str = ""
    langsmith_project: str = ""

    google_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate that secret key is set and secure in production."""
        if not v or v == "your-secret-key-here":
            # In production, this should fail
            environment = info.data.get("environment", "dev")
            debug = info.data.get("debug", False)
            if environment != "dev" and not debug:
                raise ValueError(
                    "SECRET_KEY must be set to a secure value in production. "
                    "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'"
                )
            # Generate a temporary key for development
            if not v:
                import secrets

                v = secrets.token_hex(32)
        return v


@lru_cache
def get_settings():
    return Settings()
