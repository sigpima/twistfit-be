"""add quiz attempt axis scores

Revision ID: b7e4f2a9c1d6
Revises: f3a1c9d8e2b4
Create Date: 2026-09-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e4f2a9c1d6'
down_revision: Union[str, None] = 'f3a1c9d8e2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('quiz_attempts', sa.Column('hue_score', sa.Integer(), nullable=True))
    op.add_column('quiz_attempts', sa.Column('value_score', sa.Integer(), nullable=True))
    op.add_column('quiz_attempts', sa.Column('chroma_score', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('quiz_attempts', 'chroma_score')
    op.drop_column('quiz_attempts', 'value_score')
    op.drop_column('quiz_attempts', 'hue_score')
