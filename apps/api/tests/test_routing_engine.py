from escalate.analysis.models import (
    Category,
    ChoiceSignal,
    NumericSignal,
    Sentiment,
    TicketAnalysis,
)
from escalate.routing.engine import RoutingDecisionEngine
from escalate.routing.models import RoutingMode
from escalate.routing.rules import RoutingThresholds
from escalate.tickets.domain import SupportTier, Team

THRESHOLDS = RoutingThresholds(
    security=0.80,
    engineering=0.80,
    high_impact=0.85,
    high_urgency=0.80,
    l3_complexity=0.65,
    l2_complexity=0.35,
    automatic_confidence=0.90,
    confirmation_confidence=0.70,
)


def analysis(
    *,
    security: float = 0,
    impact: float = 0.2,
    urgency: float = 0.2,
    developer: float = 0.2,
    complexity: float = 0.2,
    confidence: float = 0.95,
    team: Team = Team.BACKEND,
) -> TicketAnalysis:
    return TicketAnalysis(
        category=ChoiceSignal(value=Category.OTHER, confidence=confidence),
        sentiment=ChoiceSignal(value=Sentiment.NEUTRAL, confidence=confidence),
        urgency=NumericSignal(value=urgency, confidence=confidence),
        customerImpact=NumericSignal(value=impact, confidence=confidence),
        technicalComplexity=NumericSignal(value=complexity, confidence=confidence),
        requiresDeveloper=NumericSignal(value=developer, confidence=confidence),
        securityRisk=NumericSignal(value=security, confidence=confidence),
        suggestedTeam=ChoiceSignal(value=team, confidence=confidence),
        provider="test",
        model="test",
        processingTimeMs=1,
    )


def test_security_at_exact_threshold_goes_to_security_engineering() -> None:
    decision = RoutingDecisionEngine(THRESHOLDS).decide(analysis(security=0.80))
    assert decision.support_tier is SupportTier.ENGINEERING
    assert decision.team is Team.SECURITY


def test_high_impact_incident_goes_directly_to_engineering() -> None:
    decision = RoutingDecisionEngine(THRESHOLDS).decide(
        analysis(impact=0.85, urgency=0.80, developer=0.70, team=Team.PLATFORM)
    )
    assert decision.support_tier is SupportTier.ENGINEERING
    assert decision.team is Team.PLATFORM
    assert len(decision.reasons) == 3


def test_complexity_boundaries_are_inclusive() -> None:
    engine = RoutingDecisionEngine(THRESHOLDS)
    assert engine.decide(analysis(complexity=0.35)).support_tier is SupportTier.L2
    assert engine.decide(analysis(complexity=0.65)).support_tier is SupportTier.L3


def test_confidence_gate_boundaries() -> None:
    engine = RoutingDecisionEngine(THRESHOLDS)
    assert engine.decide(analysis(confidence=0.90)).routing_mode is RoutingMode.AUTOMATIC
    assert (
        engine.decide(analysis(confidence=0.70)).routing_mode
        is RoutingMode.REQUIRES_CONFIRMATION
    )
    assert engine.decide(analysis(confidence=0.699)).routing_mode is RoutingMode.MANUAL_TRIAGE

