from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Escalate"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://escalate:escalate@localhost:5432/escalate"
    ai_provider: str = "mock"
    cors_origins: list[str] = ["http://localhost:5173"]

    hubspot_access_token: SecretStr | None = None
    hubspot_base_url: str = "https://api.hubapi.com"
    hubspot_tickets_path: str = "/crm/v3/objects/tickets"
    hubspot_timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    hubspot_sync_page_size: int = Field(default=100, ge=1, le=100)
    hubspot_title_property: str = "subject"
    hubspot_description_property: str = "content"
    hubspot_customer_name_property: str = ""

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
