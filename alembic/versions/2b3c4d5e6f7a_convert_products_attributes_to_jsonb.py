"""convert products.attributes to jsonb and add gin index

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2025-09-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "2b3c4d5e6f7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "products",
        "attributes",
        type_=postgresql.JSONB(),
        postgresql_using="attributes::jsonb",
        existing_type=sa.JSON(),
        existing_nullable=True,
    )
    op.create_index(
        "ix_products_attributes_gin",
        "products",
        ["attributes"],
        postgresql_using="gin",
    )


def downgrade():
    op.drop_index("ix_products_attributes_gin", table_name="products")
    op.alter_column(
        "products",
        "attributes",
        type_=sa.JSON(),
        postgresql_using="attributes::json",
        existing_type=postgresql.JSONB(),
        existing_nullable=True,
    )
