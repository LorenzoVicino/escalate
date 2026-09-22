from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from escalate.tickets.domain import SupportTier, Team


class RoutingMode(StrEnum):
    AUTOMATIC = "AUTOMATIC"
    REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
    MANUAL_TRIAGE = "MANUAL_TRIAGE"


class RoutingDecision(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    support_tier: SupportTier = Field(alias="supportTier")
    team: Team
    confidence: float = Field(ge=0, le=1)
    routing_mode: RoutingMode = Field(alias="routingMode")
    reasons: list[str]

