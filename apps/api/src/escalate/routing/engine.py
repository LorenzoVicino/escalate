from escalate.analysis.models import TicketAnalysis
from escalate.routing.confidence import confidence_mode, routing_confidence
from escalate.routing.models import RoutingDecision
from escalate.routing.rules import RoutingThresholds
from escalate.tickets.domain import SupportTier, Team


class RoutingDecisionEngine:
    def __init__(self, thresholds: RoutingThresholds) -> None:
        self._t = thresholds

    def decide(self, analysis: TicketAnalysis) -> RoutingDecision:
        tier, team, reasons = self._destination(analysis)
        confidence = routing_confidence(analysis)
        mode = confidence_mode(confidence, self._t)
        if mode.value != "AUTOMATIC":
            reasons.append(
                f"Human review required because routing confidence is {confidence:.0%}"
            )
        return RoutingDecision(
            support_tier=tier,
            team=team,
            confidence=confidence,
            routing_mode=mode,
            reasons=reasons,
        )

    def _destination(
        self, analysis: TicketAnalysis
    ) -> tuple[SupportTier, Team, list[str]]:
        a = analysis
        if a.security_risk.value >= self._t.security:
            return (
                SupportTier.ENGINEERING,
                Team.SECURITY,
                ["Security risk exceeds the engineering escalation threshold"],
            )
        if (
            a.customer_impact.value >= self._t.high_impact
            and a.urgency.value >= self._t.high_urgency
            and a.requires_developer.value >= 0.70
        ):
            return (
                SupportTier.ENGINEERING,
                self._engineering_team(a),
                [
                    "Large customer impact detected",
                    "High urgency detected",
                    "Developer intervention probability is high",
                ],
            )
        if (
            a.customer_impact.value >= self._t.high_impact
            and a.urgency.value >= self._t.high_urgency
        ):
            return SupportTier.L3, a.suggested_team.value, [
                "High-impact urgent incident requires specialist investigation"
            ]
        if a.requires_developer.value >= self._t.engineering:
            return SupportTier.ENGINEERING, self._engineering_team(a), [
                "Developer intervention probability exceeds the engineering threshold"
            ]
        if a.technical_complexity.value >= self._t.l3_complexity:
            return SupportTier.L3, a.suggested_team.value, [
                "Technical complexity requires specialist investigation"
            ]
        if a.technical_complexity.value >= self._t.l2_complexity:
            return SupportTier.L2, Team.SUPPORT, [
                "Technical complexity requires technical support"
            ]
        return SupportTier.L1, Team.SUPPORT, [
            "Issue fits standard customer support handling"
        ]

    @staticmethod
    def _engineering_team(analysis: TicketAnalysis) -> Team:
        return (
            Team.BACKEND
            if analysis.suggested_team.value in {Team.SUPPORT, Team.UNKNOWN}
            else analysis.suggested_team.value
        )
