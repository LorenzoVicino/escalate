"""Add ticket owner id for ownership filtering.

Revision ID: 20260922_0004
Revises: 20260922_0003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260922_0004"
down_revision: str | None = "20260922_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("owner_id", sa.String(64), nullable=True))
    op.create_index("ix_tickets_owner_id", "tickets", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_tickets_owner_id", table_name="tickets")
    op.drop_column("tickets", "owner_id")
