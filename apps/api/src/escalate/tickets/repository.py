from typing import Any, cast

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import InstrumentedAttribute, Session, selectinload

from escalate.db.models.ticket import (
    RoutingDecisionRecord,
    TicketAnalysisRecord,
    TicketMessageRecord,
    TicketRecord,
)
from escalate.tickets.schemas import TicketFilters

_DETAIL_OPTIONS = (
    selectinload(TicketRecord.analyses),
    selectinload(TicketRecord.routing_decisions),
    selectinload(TicketRecord.messages),
)


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

    def add_message(self, message: TicketMessageRecord) -> None:
        self._session.add(message)
        self._session.flush()

    def get(self, ticket_id: str) -> TicketRecord | None:
        statement = (
            select(TicketRecord).where(TicketRecord.id == ticket_id).options(*_DETAIL_OPTIONS)
        )
        return self._session.scalar(statement)

    def get_by_external(self, source: str, external_id: str) -> TicketRecord | None:
        statement = (
            select(TicketRecord)
            .where(
                TicketRecord.source == source,
                TicketRecord.external_id == external_id,
            )
            .options(*_DETAIL_OPTIONS)
        )
        return self._session.scalar(statement)

    def exists_external(self, source: str, external_id: str) -> bool:
        statement = select(func.count()).select_from(TicketRecord).where(
            TicketRecord.source == source,
            TicketRecord.external_id == external_id,
        )
        return bool(self._session.scalar(statement))

    @staticmethod
    def _conditions(filters: TicketFilters | None) -> list[ColumnElement[bool]]:
        if filters is None:
            return []
        conditions: list[ColumnElement[bool]] = []
        if filters.owner_id:
            conditions.append(TicketRecord.owner_id == filters.owner_id)
        if filters.status:
            conditions.append(TicketRecord.status == filters.status)
        if filters.team:
            conditions.append(TicketRecord.assigned_team == filters.team)
        if filters.tier:
            conditions.append(TicketRecord.assigned_tier == filters.tier)
        if filters.q:
            pattern = f"%{filters.q}%"
            conditions.append(
                or_(
                    TicketRecord.title.ilike(pattern),
                    TicketRecord.description.ilike(pattern),
                    TicketRecord.customer_name.ilike(pattern),
                )
            )
        return conditions

    def list(
        self, *, page: int, page_size: int, filters: TicketFilters | None = None
    ) -> tuple[list[TicketRecord], int]:
        conditions = self._conditions(filters)
        total = (
            self._session.scalar(
                select(func.count()).select_from(TicketRecord).where(*conditions)
            )
            or 0
        )
        # Order by when the ticket was raised, not when we happened to import it.
        raised_at = func.coalesce(TicketRecord.external_created_at, TicketRecord.created_at)
        statement = (
            select(TicketRecord)
            .where(*conditions)
            .order_by(raised_at.desc(), TicketRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self._session.scalars(statement)), total

    def counts_by(
        self, column: InstrumentedAttribute[Any], filters: TicketFilters | None = None
    ) -> dict[str, int]:
        statement = (
            select(column, func.count())
            .where(*self._conditions(filters))
            .group_by(column)
        )
        rows = self._session.execute(statement).all()
        return {str(key): cast(int, count) for key, count in rows if key is not None}

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
