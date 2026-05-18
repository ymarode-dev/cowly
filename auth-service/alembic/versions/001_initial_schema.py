"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-18
"""

from alembic import op
from sqlmodel import SQLModel

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    import app.database  # noqa: F401 — registers SQLModel metadata

    bind = op.get_bind()
    SQLModel.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    SQLModel.metadata.drop_all(bind=bind)
