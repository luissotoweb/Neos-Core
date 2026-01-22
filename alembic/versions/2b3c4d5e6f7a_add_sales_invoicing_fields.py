"""add sales invoicing fields

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2025-09-08 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b3c4d5e6f7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("sales", sa.Column("exchange_rate", sa.Numeric(10, 4), nullable=True))
    op.add_column("sales", sa.Column("invoice_type", sa.String(50), nullable=True))
    op.add_column("sales", sa.Column("cae", sa.String(50), nullable=True))
    op.add_column("sales", sa.Column("cae_expiration", sa.DateTime(), nullable=True))
    op.add_column("sales", sa.Column("invoice_number", sa.String(50), nullable=True))


def downgrade():
    op.drop_column("sales", "invoice_number")
    op.drop_column("sales", "cae_expiration")
    op.drop_column("sales", "cae")
    op.drop_column("sales", "invoice_type")
    op.drop_column("sales", "exchange_rate")
