from dataclasses import dataclass

from escalate.config import Settings


@dataclass(frozen=True)
class RoutingThresholds:
    security: float
    engineering: float
    high_impact: float
    high_urgency: float
    l3_complexity: float
    l2_complexity: float
    automatic_confidence: float
    confirmation_confidence: float

    @classmethod
    def from_settings(cls, settings: Settings) -> "RoutingThresholds":
        return cls(
            security=settings.routing_security_threshold,
            engineering=settings.routing_engineering_threshold,
            high_impact=settings.routing_high_impact_threshold,
            high_urgency=settings.routing_high_urgency_threshold,
            l3_complexity=settings.routing_l3_complexity_threshold,
            l2_complexity=settings.routing_l2_complexity_threshold,
            automatic_confidence=settings.auto_route_confidence,
            confirmation_confidence=settings.confirmation_confidence,
        )

