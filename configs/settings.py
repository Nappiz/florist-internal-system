from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: SecretStr | None = None
    app_env: Literal["production", "development"] = "production"
    allowed_origins: list[str] = Field(default_factory=list)
    allowed_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    seed_superadmin_password: SecretStr | None = None

    @model_validator(mode="after")
    def validate_origins(self):
        if any(origin == "*" or not origin.startswith(("https://", "http://")) for origin in self.allowed_origins):
            raise ValueError("ALLOWED_ORIGINS must contain explicit HTTP(S) origins.")
        if self.app_env == "production" and any(not origin.startswith("https://") for origin in self.allowed_origins):
            raise ValueError("Production ALLOWED_ORIGINS must use HTTPS.")
        if "*" in self.allowed_hosts:
            raise ValueError("ALLOWED_HOSTS cannot allow every host.")
        return self

    @property
    def session_cookie_name(self) -> str:
        return "__Host-florist_session" if self.app_env == "production" else "florist_session"


@lru_cache
def get_settings() -> Settings:
    return Settings()
