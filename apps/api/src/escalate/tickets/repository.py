from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from escalate.db.models.ticket import RoutingDecisionRecord, TicketAnalysisRecord, TicketRecord


class TicketRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_ticket(self, ticket: TicketRecord) -> None:
        self._session.add(ticket)
        self._session.flush()

    def add_analysis(self, analysis: TicketAnalysisRecord) -> None:
        self._session.add(analysis)
        self._session.flush()

    def add_routing_decision(self, decision: RoutingDecisionRecord) -> None:
        self._session.add(decision)
        self._session.flush()

    def get(self, ticket_id: str) -> TicketRecord | None:
        statement = (
            select(TicketRecord)
            .where(TicketRecord.id == ticket_id)
            .options(
                selectinload(TicketRecord.analyses),
                selectinload(TicketRecord.routing_decisions),
            )
        )
        return self._session.scalar(statement)

    def list(self) -> list[TicketRecord]:
        statement = select(TicketRecord).order_by(TicketRecord.created_at.desc())
        return list(self._session.scalars(statement))

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

