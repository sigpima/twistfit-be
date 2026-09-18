"""add forum post soft delete

Revision ID: f3a1c9d8e2b4
Revises: a274de3aae0b
Create Date: 2026-09-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a1c9d8e2b4'
down_revision: Union[str, None] = 'a274de3aae0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('forum_posts', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('forum_posts', sa.Column('deleted_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_forum_posts_deleted_by_id_users', 'forum_posts', 'users', ['deleted_by_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_forum_posts_deleted_by_id_users', 'forum_posts', type_='foreignkey')
    op.drop_column('forum_posts', 'deleted_by_id')
    op.drop_column('forum_posts', 'deleted_at')
