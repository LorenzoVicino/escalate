from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from escalate.db.base import Base


def now_utc() -> datetime:
    return datetime.now(UTC)


class TicketRecord(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_tickets_source_external_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    customer_name: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    assigned_tier: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    assigned_team: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    analyses: Mapped[list["TicketAnalysisRecord"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    routing_decisions: Mapped[list["RoutingDecisionRecord"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketAnalysisRecord(Base):
    __tablename__ = "ticket_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    category_confidence: Mapped[float] = mapped_column(Float)
    sentiment: Mapped[str] = mapped_column(String(32))
    sentiment_confidence: Mapped[float] = mapped_column(Float)
    urgency: Mapped[float] = mapped_column(Float)
    urgency_confidence: Mapped[float] = mapped_column(Float)
    customer_impact: Mapped[float] = mapped_column(Float)
    customer_impact_confidence: Mapped[float] = mapped_column(Float)
    technical_complexity: Mapped[float] = mapped_column(Float)
    technical_complexity_confidence: Mapped[float] = mapped_column(Float)
    requires_developer: Mapped[float] = mapped_column(Float)
    requires_developer_confidence: Mapped[float] = mapped_column(Float)
    security_risk: Mapped[float] = mapped_column(Float)
    security_risk_confidence: Mapped[float] = mapped_column(Float)
    suggested_team: Mapped[str] = mapped_column(String(32))
    suggested_team_confidence: Mapped[float] = mapped_column(Float)
    provider: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(255))
    processing_time_ms: Mapped[int] = mapped_column(Integer)
    provider_metadata: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    ticket: Mapped[TicketRecord] = relationship(back_populates="analyses")


class RoutingDecisionRecord(Base):
    __tablename__ = "routing_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), index=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("ticket_analyses.id"), index=True)
    support_tier: Mapped[str] = mapped_column(String(32), index=True)
    team: Mapped[str] = mapped_column(String(32), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    routing_mode: Mapped[str] = mapped_column(String(32), index=True)
    reasons: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    ticket: Mapped[TicketRecord] = relationship(back_populates="routing_decisions")
