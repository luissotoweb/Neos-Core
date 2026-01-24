"""add tenant categories and active modules

Revision ID: 4d5e6f7a8b9c
Revises: 3c4d5e6f7a8b
Create Date: 2025-09-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d5e6f7a8b9c"
down_revision = "3c4d5e6f7a8b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenant_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.UniqueConstraint("tenant_id", "name", name="uq_tenant_categories_tenant_name"),
    )
    op.create_index("ix_tenant_categories_id", "tenant_categories", ["id"])
    op.create_index("ix_tenant_categories_tenant_id", "tenant_categories", ["tenant_id"])
    op.alter_column("tenant_categories", "is_active", server_default=None)

    op.create_table(
        "tenant_active_modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("module_key", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.UniqueConstraint("tenant_id", "module_key", name="uq_tenant_modules_tenant_key"),
    )
    op.create_index("ix_tenant_active_modules_id", "tenant_active_modules", ["id"])
    op.create_index("ix_tenant_active_modules_tenant_id", "tenant_active_modules", ["tenant_id"])
    op.alter_column("tenant_active_modules", "is_active", server_default=None)


def downgrade():
    op.drop_index("ix_tenant_active_modules_tenant_id", table_name="tenant_active_modules")
    op.drop_index("ix_tenant_active_modules_id", table_name="tenant_active_modules")
    op.drop_table("tenant_active_modules")

    op.drop_index("ix_tenant_categories_tenant_id", table_name="tenant_categories")
    op.drop_index("ix_tenant_categories_id", table_name="tenant_categories")
    op.drop_table("tenant_categories")
