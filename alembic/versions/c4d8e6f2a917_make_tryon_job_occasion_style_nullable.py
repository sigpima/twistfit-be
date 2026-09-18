"""make tryon job occasion/style nullable

Revision ID: c4d8e6f2a917
Revises: b7e4f2a9c1d6
Create Date: 2026-09-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d8e6f2a917'
down_revision: Union[str, None] = 'b7e4f2a9c1d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('tryon_jobs', 'occasion', existing_type=sa.String(length=100), nullable=True)
    op.alter_column('tryon_jobs', 'style', existing_type=sa.String(length=100), nullable=True)


def downgrade() -> None:
    op.alter_column('tryon_jobs', 'style', existing_type=sa.String(length=100), nullable=False)
    op.alter_column('tryon_jobs', 'occasion', existing_type=sa.String(length=100), nullable=False)
