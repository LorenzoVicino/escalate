"""Track when a ticket was raised in the source system.

Revision ID: 20260923_0005
Revises: 20260922_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260923_0005"
down_revision: str | None = "20260922_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tickets", sa.Column("external_created_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index("ix_tickets_external_created_at", "tickets", ["external_created_at"])


def downgrade() -> None:
    op.drop_index("ix_tickets_external_created_at", table_name="tickets")
    op.drop_column("tickets", "external_created_at")
