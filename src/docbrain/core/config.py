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

    database_url: str = "postgresql+psycopg://docbrain:docbrain@localhost:5432/docbrain"
    redis_url: str = "redis://localhost:6379/0"
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_bucket: str = "docbrain-local"


@lru_cache
def get_settings() -> Settings:
    return Settings()

