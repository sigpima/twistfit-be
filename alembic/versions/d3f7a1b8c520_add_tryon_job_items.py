"""add tryon job items

Revision ID: d3f7a1b8c520
Revises: c4d8e6f2a917
Create Date: 2026-09-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f7a1b8c520'
down_revision: Union[str, None] = 'c4d8e6f2a917'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tryon_job_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tryon_job_id', sa.Integer(), nullable=False),
        sa.Column('wardrobe_item_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['tryon_job_id'], ['tryon_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['wardrobe_item_id'], ['wardrobe_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tryon_job_items_tryon_job_id'), 'tryon_job_items', ['tryon_job_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tryon_job_items_tryon_job_id'), table_name='tryon_job_items')
    op.drop_table('tryon_job_items')
