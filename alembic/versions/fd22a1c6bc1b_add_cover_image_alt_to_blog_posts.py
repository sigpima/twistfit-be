"""add cover_image_alt to blog_posts

Revision ID: fd22a1c6bc1b
Revises: 92aa18f3902b
Create Date: 2026-09-19 18:05:38.126038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd22a1c6bc1b'
down_revision: Union[str, None] = '92aa18f3902b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('blog_posts', sa.Column('cover_image_alt', sa.String(length=300), nullable=True))


def downgrade() -> None:
    op.drop_column('blog_posts', 'cover_image_alt')
