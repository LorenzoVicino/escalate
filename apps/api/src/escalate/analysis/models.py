from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from escalate.tickets.domain import Team


class Category(StrEnum):
    ACCOUNT = "ACCOUNT"
    CONFIGURATION = "CONFIGURATION"
    HOW_TO = "HOW_TO"
    BUG = "BUG"
    INTEGRATION = "INTEGRATION"
    PRODUCTION_INCIDENT = "PRODUCTION_INCIDENT"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    DATA_ISSUE = "DATA_ISSUE"
    BILLING = "BILLING"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    OTHER = "OTHER"


class Sentiment(StrEnum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    VERY_NEGATIVE = "VERY_NEGATIVE"


T = TypeVar("T")


class ChoiceSignal(BaseModel, Generic[T]):
    value: T
    confidence: float = Field(ge=0, le=1)


class NumericSignal(BaseModel):
    value: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class TicketAnalysisInput(BaseModel):
    title: str
    description: str
    customer_name: str


class TicketAnalysis(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category: ChoiceSignal[Category]
    sentiment: ChoiceSignal[Sentiment]
    urgency: NumericSignal
    customer_impact: NumericSignal = Field(alias="customerImpact")
    technical_complexity: NumericSignal = Field(alias="technicalComplexity")
    requires_developer: NumericSignal = Field(alias="requiresDeveloper")
    security_risk: NumericSignal = Field(alias="securityRisk")
    suggested_team: ChoiceSignal[Team] = Field(alias="suggestedTeam")
    provider: str
    model: str
    processing_time_ms: int = Field(alias="processingTimeMs", ge=0)

    def signal_confidences(self) -> list[float]:
        return [
            self.category.confidence,
            self.urgency.confidence,
            self.customer_impact.confidence,
            self.technical_complexity.confidence,
            self.requires_developer.confidence,
            self.security_risk.confidence,
            self.suggested_team.confidence,
        ]
