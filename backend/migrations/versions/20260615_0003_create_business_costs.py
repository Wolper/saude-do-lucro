"""create business costs

Revision ID: 20260615_0003
Revises: 20260612_0002
Create Date: 2026-06-15 00:03:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260615_0003"
down_revision: str | None = "20260612_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "business_costs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_business_costs_id"), "business_costs", ["id"], unique=False)
    op.create_index(
        op.f("ix_business_costs_company_id"),
        "business_costs",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_business_costs_is_active"),
        "business_costs",
        ["is_active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_business_costs_is_active"), table_name="business_costs")
    op.drop_index(op.f("ix_business_costs_company_id"), table_name="business_costs")
    op.drop_index(op.f("ix_business_costs_id"), table_name="business_costs")
    op.drop_table("business_costs")
