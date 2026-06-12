"""create financial entries

Revision ID: 20260612_0002
Revises: 20260609_0001
Create Date: 2026-06-12 00:02:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260612_0002"
down_revision: str | None = "20260609_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "financial_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=80), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
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
    op.create_index(op.f("ix_financial_entries_id"), "financial_entries", ["id"], unique=False)
    op.create_index(
        op.f("ix_financial_entries_company_id"),
        "financial_entries",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_financial_entries_entry_date"),
        "financial_entries",
        ["entry_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_financial_entries_type"),
        "financial_entries",
        ["type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_financial_entries_type"), table_name="financial_entries")
    op.drop_index(op.f("ix_financial_entries_entry_date"), table_name="financial_entries")
    op.drop_index(op.f("ix_financial_entries_company_id"), table_name="financial_entries")
    op.drop_index(op.f("ix_financial_entries_id"), table_name="financial_entries")
    op.drop_table("financial_entries")
