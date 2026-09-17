"""drop pose and split tryon job result into front and side images

Revision ID: 0c5988ba6204
Revises: df6fa924c54b
Create Date: 2026-09-18 01:34:40.841037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c5988ba6204'
down_revision: Union[str, None] = 'df6fa924c54b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tryon_jobs', sa.Column('result_front_blob_url', sa.String(length=1000), nullable=True))
    op.add_column('tryon_jobs', sa.Column('result_side_blob_url', sa.String(length=1000), nullable=True))
    op.execute("UPDATE tryon_jobs SET result_front_blob_url = result_blob_url")
    op.drop_column('tryon_jobs', 'result_blob_url')
    op.drop_column('tryon_jobs', 'pose')


def downgrade() -> None:
    op.add_column('tryon_jobs', sa.Column('pose', sa.String(length=20), nullable=False, server_default='front'))
    op.add_column('tryon_jobs', sa.Column('result_blob_url', sa.String(length=1000), nullable=True))
    op.execute("UPDATE tryon_jobs SET result_blob_url = result_front_blob_url")
    op.drop_column('tryon_jobs', 'result_side_blob_url')
    op.drop_column('tryon_jobs', 'result_front_blob_url')
