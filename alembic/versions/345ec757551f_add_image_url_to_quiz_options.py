"""add image_url to quiz_options

Revision ID: 345ec757551f
Revises: 0c5988ba6204
Create Date: 2026-09-18 15:46:50.059887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '345ec757551f'
down_revision: Union[str, None] = '0c5988ba6204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('quiz_options', sa.Column('image_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('quiz_options', 'image_url')
