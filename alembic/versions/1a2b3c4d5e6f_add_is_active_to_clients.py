"""add is_active to clients

Revision ID: 1a2b3c4d5e6f
Revises: None
Create Date: 2025-09-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1a2b3c4d5e6f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "clients",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("clients", "is_active", server_default=None)


def downgrade():
    op.drop_column("clients", "is_active")
