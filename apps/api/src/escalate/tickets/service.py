import structlog

from escalate.analysis.models import TicketAnalysis, TicketAnalysisInput
from escalate.analysis.service import AnalysisService
from escalate.db.models.ticket import RoutingDecisionRecord, TicketAnalysisRecord, TicketRecord
from escalate.routing.engine import RoutingDecisionEngine
from escalate.routing.models import RoutingDecision, RoutingMode
from escalate.tickets.domain import TicketStatus
from escalate.tickets.repository import TicketRepository
from escalate.tickets.schemas import TicketCreate, TicketResult, TicketSummary

logger = structlog.get_logger()


class TicketNotFoundError(Exception):
    pass


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        analysis_service: AnalysisService,
        routing_engine: RoutingDecisionEngine,
    ) -> None:
        self._repository = repository
        self._analysis = analysis_service
        self._routing = routing_engine

    async def create(self, data: TicketCreate) -> TicketResult:
        ticket = TicketRecord(
            external_id=data.external_id,
            title=data.title,
            description=data.description,
            customer_name=data.customer_name,
            source=data.source.value,
            status=TicketStatus.OPEN.value,
        )
        try:
            self._repository.add_ticket(ticket)
            analysis = await self._analysis.analyze(
                TicketAnalysisInput(
                    title=ticket.title,
                    description=ticket.description,
                    customer_name=ticket.customer_name,
                )
            )
            analysis_record = self._analysis_record(ticket.id, analysis)
            self._repository.add_analysis(analysis_record)
            routing = self._routing.decide(analysis)
            self._repository.add_routing_decision(
                RoutingDecisionRecord(
                    ticket_id=ticket.id,
                    analysis_id=analysis_record.id,
                    support_tier=routing.support_tier.value,
                    team=routing.team.value,
                    confidence=routing.confidence,
                    routing_mode=routing.routing_mode.value,
                    reasons=routing.reasons,
                )
            )
            self._apply_routing(ticket, routing)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

        logger.info(
            "ticket_routed",
            ticket_id=ticket.id,
            analysis_provider=analysis.provider,
            analysis_duration_ms=analysis.processing_time_ms,
            routing_result=f"{routing.support_tier.value}/{routing.team.value}",
            routing_confidence=routing.confidence,
            routing_mode=routing.routing_mode.value,
        )
        return self._result(ticket, analysis, routing)

    def get(self, ticket_id: str) -> TicketResult:
        ticket = self._repository.get(ticket_id)
        if ticket is None or not ticket.analyses or not ticket.routing_decisions:
            raise TicketNotFoundError(ticket_id)
        return self._result(
            ticket,
            self._analysis_from_record(ticket.analyses[-1]),
            self._routing_from_record(ticket.routing_decisions[-1]),
        )

    def list(self) -> list[TicketSummary]:
        return [self._summary(ticket) for ticket in self._repository.list()]

    @staticmethod
    def _apply_routing(ticket: TicketRecord, routing: RoutingDecision) -> None:
        if routing.routing_mode is RoutingMode.AUTOMATIC:
            ticket.assigned_tier = routing.support_tier.value
            ticket.assigned_team = routing.team.value
            ticket.status = TicketStatus.ROUTED.value
        elif routing.routing_mode is RoutingMode.REQUIRES_CONFIRMATION:
            ticket.status = TicketStatus.WAITING_CONFIRMATION.value
        else:
            ticket.status = TicketStatus.MANUAL_TRIAGE.value

    @staticmethod
    def _analysis_record(ticket_id: str, a: TicketAnalysis) -> TicketAnalysisRecord:
        return TicketAnalysisRecord(
            ticket_id=ticket_id,
            category=a.category.value.value,
            category_confidence=a.category.confidence,
            sentiment=a.sentiment.value.value,
            sentiment_confidence=a.sentiment.confidence,
            urgency=a.urgency.value,
            urgency_confidence=a.urgency.confidence,
            customer_impact=a.customer_impact.value,
            customer_impact_confidence=a.customer_impact.confidence,
            technical_complexity=a.technical_complexity.value,
            technical_complexity_confidence=a.technical_complexity.confidence,
            requires_developer=a.requires_developer.value,
            requires_developer_confidence=a.requires_developer.confidence,
            security_risk=a.security_risk.value,
            security_risk_confidence=a.security_risk.confidence,
            suggested_team=a.suggested_team.value.value,
            suggested_team_confidence=a.suggested_team.confidence,
            provider=a.provider,
            model=a.model,
            processing_time_ms=a.processing_time_ms,
        )

    @staticmethod
    def _analysis_from_record(r: TicketAnalysisRecord) -> TicketAnalysis:
        return TicketAnalysis.model_validate({
            "category": {"value": r.category, "confidence": r.category_confidence},
            "sentiment": {"value": r.sentiment, "confidence": r.sentiment_confidence},
            "urgency": {"value": r.urgency, "confidence": r.urgency_confidence},
            "customerImpact": {
                "value": r.customer_impact,
                "confidence": r.customer_impact_confidence,
            },
            "technicalComplexity": {
                "value": r.technical_complexity,
                "confidence": r.technical_complexity_confidence,
            },
            "requiresDeveloper": {
                "value": r.requires_developer,
                "confidence": r.requires_developer_confidence,
            },
            "securityRisk": {"value": r.security_risk, "confidence": r.security_risk_confidence},
            "suggestedTeam": {"value": r.suggested_team, "confidence": r.suggested_team_confidence},
            "provider": r.provider,
            "model": r.model,
            "processingTimeMs": r.processing_time_ms,
        })

    @staticmethod
    def _routing_from_record(r: RoutingDecisionRecord) -> RoutingDecision:
        return RoutingDecision.model_validate({
            "supportTier": r.support_tier,
            "team": r.team,
            "confidence": r.confidence,
            "routingMode": r.routing_mode,
            "reasons": r.reasons,
        })

    @staticmethod
    def _summary(ticket: TicketRecord) -> TicketSummary:
        return TicketSummary.model_validate({
            "id": ticket.id,
            "title": ticket.title,
            "customerName": ticket.customer_name,
            "source": ticket.source,
            "status": ticket.status,
            "assignedTier": ticket.assigned_tier,
            "assignedTeam": ticket.assigned_team,
            "createdAt": ticket.created_at,
        })

    @classmethod
    def _result(
        cls, ticket: TicketRecord, analysis: TicketAnalysis, routing: RoutingDecision
    ) -> TicketResult:
        summary = cls._summary(ticket)
        return TicketResult.model_validate({
            **summary.model_dump(by_alias=True),
            "externalId": ticket.external_id,
            "description": ticket.description,
            "updatedAt": ticket.updated_at,
            "analysis": analysis.model_dump(by_alias=True),
            "routing": routing.model_dump(by_alias=True),
        })
