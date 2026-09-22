from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Escalate"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://escalate:escalate@localhost:5432/escalate"
    ai_provider: str = "mock"
    cors_origins: list[str] = ["http://localhost:5173"]

    auto_route_confidence: float = Field(default=0.90, ge=0, le=1)
    confirmation_confidence: float = Field(default=0.70, ge=0, le=1)
    routing_security_threshold: float = Field(default=0.80, ge=0, le=1)
    routing_engineering_threshold: float = Field(default=0.80, ge=0, le=1)
    routing_high_impact_threshold: float = Field(default=0.85, ge=0, le=1)
    routing_high_urgency_threshold: float = Field(default=0.80, ge=0, le=1)
    routing_l3_complexity_threshold: float = Field(default=0.65, ge=0, le=1)
    routing_l2_complexity_threshold: float = Field(default=0.35, ge=0, le=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()

