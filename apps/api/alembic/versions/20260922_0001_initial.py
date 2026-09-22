"""Create tickets, analyses, and routing decisions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260922_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("assigned_tier", sa.String(32), nullable=True),
        sa.Column("assigned_team", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ["external_id", "source", "status", "assigned_tier", "assigned_team"]:
        op.create_index(f"ix_tickets_{column}", "tickets", [column])

    op.create_table(
        "ticket_analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("category_confidence", sa.Float(), nullable=False),
        sa.Column("sentiment", sa.String(32), nullable=False),
        sa.Column("sentiment_confidence", sa.Float(), nullable=False),
        sa.Column("urgency", sa.Float(), nullable=False),
        sa.Column("urgency_confidence", sa.Float(), nullable=False),
        sa.Column("customer_impact", sa.Float(), nullable=False),
        sa.Column("customer_impact_confidence", sa.Float(), nullable=False),
        sa.Column("technical_complexity", sa.Float(), nullable=False),
        sa.Column("technical_complexity_confidence", sa.Float(), nullable=False),
        sa.Column("requires_developer", sa.Float(), nullable=False),
        sa.Column("requires_developer_confidence", sa.Float(), nullable=False),
        sa.Column("security_risk", sa.Float(), nullable=False),
        sa.Column("security_risk_confidence", sa.Float(), nullable=False),
        sa.Column("suggested_team", sa.String(32), nullable=False),
        sa.Column("suggested_team_confidence", sa.Float(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(255), nullable=False),
        sa.Column("processing_time_ms", sa.Integer(), nullable=False),
        sa.Column("provider_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ticket_analyses_ticket_id", "ticket_analyses", ["ticket_id"])
    op.create_index("ix_ticket_analyses_category", "ticket_analyses", ["category"])

    op.create_table(
        "routing_decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("analysis_id", sa.String(36), sa.ForeignKey("ticket_analyses.id"), nullable=False),
        sa.Column("support_tier", sa.String(32), nullable=False),
        sa.Column("team", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("routing_mode", sa.String(32), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ["ticket_id", "analysis_id", "support_tier", "team", "routing_mode"]:
        op.create_index(f"ix_routing_decisions_{column}", "routing_decisions", [column])


def downgrade() -> None:
    op.drop_table("routing_decisions")
    op.drop_table("ticket_analyses")
    op.drop_table("tickets")

