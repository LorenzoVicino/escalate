import structlog

from escalate.analysis.models import TicketAnalysis, TicketAnalysisInput
from escalate.analysis.service import AnalysisService
from escalate.db.models.ticket import (
    RoutingDecisionRecord,
    TicketAnalysisRecord,
    TicketMessageRecord,
    TicketRecord,
)
from escalate.routing.engine import RoutingDecisionEngine
from escalate.routing.models import RoutingDecision, RoutingMode
from escalate.tickets.domain import TicketStatus
from escalate.tickets.repository import TicketRepository
from escalate.tickets.schemas import (
    TicketContextUpdate,
    TicketCreate,
    TicketFilters,
    TicketPage,
    TicketResult,
    TicketStats,
    TicketSummary,
)

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
            external_created_at=data.external_created_at,
        )
        try:
            self._repository.add_ticket(ticket)
            analysis = await self._analysis.analyze(
                TicketAnalysisInput(
                    title=ticket.title,
                    description=ticket.description,
                    customer_name=ticket.customer_name,
                    context=data.analysis_context or "",
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

    async def create_if_missing(self, data: TicketCreate) -> tuple[TicketResult, bool]:
        if data.external_id is not None:
            existing = self._repository.get_by_external(data.source.value, data.external_id)
            if existing is not None:
                return (
                    self._result(
                        existing,
                        self._analysis_from_record(existing.analyses[-1]),
                        self._routing_from_record(existing.routing_decisions[-1]),
                    ),
                    False,
                )
        return await self.create(data), True

    def get(self, ticket_id: str) -> TicketResult:
        ticket = self._repository.get(ticket_id)
        if ticket is None or not ticket.analyses or not ticket.routing_decisions:
            raise TicketNotFoundError(ticket_id)
        return self._result(
            ticket,
            self._analysis_from_record(ticket.analyses[-1]),
            self._routing_from_record(ticket.routing_decisions[-1]),
        )

    def exists_external(self, source: str, external_id: str) -> bool:
        return self._repository.exists_external(source, external_id)

    def list(
        self, *, page: int = 1, page_size: int = 10, filters: TicketFilters | None = None
    ) -> TicketPage:
        tickets, total = self._repository.list(
            page=page, page_size=page_size, filters=filters
        )
        return TicketPage(
            items=[self._summary(ticket) for ticket in tickets],
            total=total,
            page=page,
            page_size=page_size,
        )

    def stats(self, filters: TicketFilters | None = None) -> TicketStats:
        by_status = self._repository.counts_by(TicketRecord.status, filters)
        by_tier = self._repository.counts_by(TicketRecord.assigned_tier, filters)
        by_team = self._repository.counts_by(TicketRecord.assigned_team, filters)
        return TicketStats(
            total=sum(by_status.values()),
            open=sum(
                count
                for status, count in by_status.items()
                if status != TicketStatus.RESOLVED.value
            ),
            needs_review=by_status.get(TicketStatus.WAITING_CONFIRMATION.value, 0)
            + by_status.get(TicketStatus.MANUAL_TRIAGE.value, 0),
            auto_routed=by_status.get(TicketStatus.ROUTED.value, 0),
            by_status=by_status,
            by_tier=by_tier,
            by_team=by_team,
        )

    def set_context(self, ticket_id: str, context: TicketContextUpdate) -> None:
        ticket = self._repository.get(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        ticket.owner_id = context.owner_id
        ticket.owner_name = context.owner_name
        ticket.owner_email = context.owner_email
        ticket.contact_email = context.contact_email
        try:
            for message in context.messages:
                self._repository.add_message(
                    TicketMessageRecord(
                        ticket_id=ticket_id,
                        external_id=message.external_id,
                        channel=message.channel,
                        direction=message.direction,
                        author=message.author,
                        subject=message.subject,
                        body=message.body,
                        occurred_at=message.occurred_at,
                    )
                )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

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
            "raisedAt": ticket.external_created_at or ticket.created_at,
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
            "ownerName": ticket.owner_name,
            "ownerEmail": ticket.owner_email,
            "contactEmail": ticket.contact_email,
            "messages": [
                {
                    "channel": message.channel,
                    "direction": message.direction,
                    "author": message.author,
                    "subject": message.subject,
                    "body": message.body,
                    "occurredAt": message.occurred_at,
                }
                for message in ticket.messages
            ],
            "analysis": analysis.model_dump(by_alias=True),
            "routing": routing.model_dump(by_alias=True),
        })
