"""create tryon_daily_quota table

Revision ID: 92aa18f3902b
Revises: d3f7a1b8c520
Create Date: 2026-09-19 09:25:02.394968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92aa18f3902b'
down_revision: Union[str, None] = 'd3f7a1b8c520'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tryon_daily_quota',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('quota_date', sa.Date(), nullable=False),
    sa.Column('used_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'quota_date', name='uq_tryon_daily_quota_user_date')
    )
    op.create_index(op.f('ix_tryon_daily_quota_user_id'), 'tryon_daily_quota', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tryon_daily_quota_user_id'), table_name='tryon_daily_quota')
    op.drop_table('tryon_daily_quota')
