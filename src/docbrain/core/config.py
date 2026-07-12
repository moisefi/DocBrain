from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DocBrain"
    app_version: str = "0.1.0"
    environment: str = Field(default="local", min_length=1)
    enable_docs: bool = True
    jwt_secret: str = Field(
        default="change-me-in-production-with-32-bytes",
        min_length=32,
    )
    jwt_issuer: str = "docbrain"
    access_token_ttl_seconds: int = Field(default=900, ge=60, le=3600)
    refresh_token_ttl_seconds: int = Field(
        default=60 * 60 * 24 * 30,
        ge=3600,
    )

    database_url: str = "postgresql+psycopg://docbrain:docbrain@localhost:5432/docbrain"
    redis_url: str = "redis://localhost:6379/0"
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_bucket: str = "docbrain-local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
