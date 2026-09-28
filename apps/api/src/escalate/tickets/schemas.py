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
    external_created_at: datetime | None = Field(default=None, alias="externalCreatedAt")
    # Ephemeral: feeds the decision model, never persisted on the ticket row.
    analysis_context: str | None = Field(
        default=None, alias="analysisContext", max_length=8000
    )


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
    # When the customer actually raised it; falls back to import time for local tickets.
    raised_at: datetime = Field(alias="raisedAt")

    @field_validator("created_at", "raised_at")
    @classmethod
    def ensure_created_at_utc(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class TicketPage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[TicketSummary]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class TicketFilters(BaseModel):
    owner_id: str | None = None
    status: str | None = None
    team: str | None = None
    tier: str | None = None
    q: str | None = None


class TicketStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int
    open: int
    needs_review: int = Field(alias="needsReview")
    auto_routed: int = Field(alias="autoRouted")
    by_status: dict[str, int] = Field(alias="byStatus")
    by_tier: dict[str, int] = Field(alias="byTier")
    by_team: dict[str, int] = Field(alias="byTeam")


class TicketMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    channel: str
    direction: str | None
    author: str | None
    subject: str | None
    body: str
    occurred_at: datetime = Field(alias="occurredAt")

    @field_validator("occurred_at")
    @classmethod
    def ensure_occurred_at_utc(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class TicketMessageCreate(BaseModel):
    external_id: str
    channel: str
    direction: str | None = None
    author: str | None = None
    subject: str | None = None
    body: str
    occurred_at: datetime


class TicketContextUpdate(BaseModel):
    owner_id: str | None = None
    owner_name: str | None = None
    owner_email: str | None = None
    contact_email: str | None = None
    messages: list[TicketMessageCreate] = Field(default_factory=list)


class TicketResult(TicketSummary):
    external_id: str | None = Field(alias="externalId")
    description: str
    updated_at: datetime = Field(alias="updatedAt")
    owner_name: str | None = Field(default=None, alias="ownerName")
    owner_email: str | None = Field(default=None, alias="ownerEmail")
    contact_email: str | None = Field(default=None, alias="contactEmail")
    messages: list[TicketMessage] = Field(default_factory=list)
    analysis: TicketAnalysis
    routing: RoutingDecision

    @field_validator("updated_at")
    @classmethod
    def ensure_updated_at_utc(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
