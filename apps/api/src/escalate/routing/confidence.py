from statistics import fmean

from escalate.analysis.models import TicketAnalysis
from escalate.routing.models import RoutingMode
from escalate.routing.rules import RoutingThresholds


def routing_confidence(analysis: TicketAnalysis) -> float:
    return round(fmean(analysis.signal_confidences()), 4)


def confidence_mode(confidence: float, thresholds: RoutingThresholds) -> RoutingMode:
    if confidence >= thresholds.automatic_confidence:
        return RoutingMode.AUTOMATIC
    if confidence >= thresholds.confirmation_confidence:
        return RoutingMode.REQUIRES_CONFIRMATION
    return RoutingMode.MANUAL_TRIAGE

