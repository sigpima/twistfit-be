"""create taxonomy_groups and taxonomy_values tables

Revision ID: 8d089c90d4fc
Revises: 3f56461f19fc
Create Date: 2026-09-18 00:26:04.668771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d089c90d4fc'
down_revision: Union[str, None] = '3f56461f19fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "taxonomy_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_table(
        "taxonomy_values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["taxonomy_groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "key", name="uq_taxonomy_values_group_id_key"),
    )
    op.create_index(op.f("ix_taxonomy_values_group_id"), "taxonomy_values", ["group_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_taxonomy_values_group_id"), table_name="taxonomy_values")
    op.drop_table("taxonomy_values")
    op.drop_table("taxonomy_groups")
