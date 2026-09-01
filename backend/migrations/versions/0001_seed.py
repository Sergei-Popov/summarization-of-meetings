"""Создать маркер версии схемы.

Revision ID: 0001_seed
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_seed"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "schema_metadata",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.String(length=255), nullable=False),
    )
    op.execute("INSERT INTO schema_metadata (key, value) VALUES ('seed', '1')")


def downgrade() -> None:
    op.drop_table("schema_metadata")
