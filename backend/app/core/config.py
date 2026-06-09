from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Saúde do Lucro API"
    service_name: str = "saude-do-lucro-api"
    version: str = "0.1.0"
    database_url: str = Field(
        default="postgresql://saude_user:saude_password@localhost:5432/saude_do_lucro",
        alias="DATABASE_URL",
    )
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
