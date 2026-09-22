"""Make external ticket ingestion idempotent.

Revision ID: 20260922_0002
Revises: 20260922_0001
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260922_0002"
down_revision: str | None = "20260922_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_tickets_source_external_id",
        "tickets",
        ["source", "external_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_tickets_source_external_id", "tickets", type_="unique")

