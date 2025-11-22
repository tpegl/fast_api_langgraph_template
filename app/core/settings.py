from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fast API LangGraph Template"
    debug: bool = False
    log_level: str = "DEBUG"
    environment: str = "dev"

    cors_origins: list[str] = ["http://localhost:5173"]

    # LangGraph service configuration
    langsmith_url: str = "http://localhost:2024"  # Default for local development
    langsmith_api_key: str = ""
    langsmith_project: str = ""

    google_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
