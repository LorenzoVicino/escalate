from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from escalate.analysis.models import TicketAnalysis
from escalate.routing.models import RoutingDecision
from escalate.tickets.domain import SupportTier, Team, TicketSource, TicketStatus


class TicketCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    external_id: str | None = Field(default=None, alias="externalId", max_length=255)
    title: str = Field(min_length=3, max_length=300)
    description: str = Field(min_length=5, max_length=20_000)
    customer_name: str = Field(alias="customerName", min_length=1, max_length=200)
    source: TicketSource = TicketSource.WEB


class TicketSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    customer_name: str = Field(alias="customerName")
    source: TicketSource
    status: TicketStatus
    assigned_tier: SupportTier | None = Field(alias="assignedTier")
    assigned_team: Team | None = Field(alias="assignedTeam")
    created_at: datetime = Field(alias="createdAt")

    @field_validator("created_at")
    @classmethod
    def ensure_created_at_utc(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class TicketResult(TicketSummary):
    external_id: str | None = Field(alias="externalId")
    description: str
    updated_at: datetime = Field(alias="updatedAt")
    analysis: TicketAnalysis
    routing: RoutingDecision

    @field_validator("updated_at")
    @classmethod
    def ensure_updated_at_utc(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
