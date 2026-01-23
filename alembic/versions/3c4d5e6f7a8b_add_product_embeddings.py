"""add product embeddings table

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2025-09-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "3c4d5e6f7a8b"
down_revision = "2b3c4d5e6f7a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "product_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )
    op.create_index("ix_product_embeddings_id", "product_embeddings", ["id"])
    op.create_index("ix_product_embeddings_tenant_id", "product_embeddings", ["tenant_id"])
    op.create_index("ix_product_embeddings_product_id", "product_embeddings", ["product_id"])
    op.create_index(
        "uq_product_embeddings_tenant_product",
        "product_embeddings",
        ["tenant_id", "product_id"],
        unique=True,
    )


def downgrade():
    op.drop_index("uq_product_embeddings_tenant_product", table_name="product_embeddings")
    op.drop_index("ix_product_embeddings_product_id", table_name="product_embeddings")
    op.drop_index("ix_product_embeddings_tenant_id", table_name="product_embeddings")
    op.drop_index("ix_product_embeddings_id", table_name="product_embeddings")
    op.drop_table("product_embeddings")
