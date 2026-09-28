"""Add ticket owner/contact fields and conversation thread.

Revision ID: 20260922_0003
Revises: 20260922_0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260922_0003"
down_revision: str | None = "20260922_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("owner_name", sa.String(200), nullable=True))
    op.add_column("tickets", sa.Column("owner_email", sa.String(320), nullable=True))
    op.add_column("tickets", sa.Column("contact_email", sa.String(320), nullable=True))

    op.create_table(
        "ticket_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("direction", sa.String(16), nullable=True),
        sa.Column("author", sa.String(200), nullable=True),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("ticket_id", "external_id", name="uq_ticket_messages_ticket_external_id"),
    )
    op.create_index("ix_ticket_messages_ticket_id", "ticket_messages", ["ticket_id"])


def downgrade() -> None:
    op.drop_index("ix_ticket_messages_ticket_id", table_name="ticket_messages")
    op.drop_table("ticket_messages")
    op.drop_column("tickets", "contact_email")
    op.drop_column("tickets", "owner_email")
    op.drop_column("tickets", "owner_name")
