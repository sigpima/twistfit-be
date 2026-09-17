"""migrate wardrobe items to attributes jsonb

Revision ID: df6fa924c54b
Revises: 8d089c90d4fc
Create Date: 2026-09-18 00:28:27.437328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'df6fa924c54b'
down_revision: Union[str, None] = '8d089c90d4fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "wardrobe_items",
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
    )

    op.execute(
        """
        UPDATE wardrobe_items
        SET attributes = jsonb_build_object(
            'clothing-type', jsonb_build_array(
                CASE category
                    WHEN 'ao-thun' THEN 'ao'
                    WHEN 'ao-so-mi' THEN 'ao'
                    WHEN 'quan-jean' THEN 'quan'
                    WHEN 'dam' THEN 'dam'
                    WHEN 'ao-khoac' THEN 'ao-khoac'
                    ELSE category
                END
            ),
            'style', style_tags,
            'occasion', occasion_tags
        )
        """
    )

    op.alter_column("wardrobe_items", "attributes", server_default=None)
    op.drop_column("wardrobe_items", "category")
    op.drop_column("wardrobe_items", "style_tags")
    op.drop_column("wardrobe_items", "occasion_tags")


def downgrade() -> None:
    op.add_column("wardrobe_items", sa.Column("category", sa.String(length=100), nullable=True))
    op.add_column(
        "wardrobe_items",
        sa.Column("style_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "wardrobe_items",
        sa.Column("occasion_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.execute(
        """
        UPDATE wardrobe_items
        SET category = COALESCE(attributes -> 'clothing-type' ->> 0, 'ao-thun'),
            style_tags = COALESCE(attributes -> 'style', '[]'::jsonb),
            occasion_tags = COALESCE(attributes -> 'occasion', '[]'::jsonb)
        """
    )

    op.alter_column("wardrobe_items", "category", nullable=False)
    op.alter_column("wardrobe_items", "style_tags", nullable=False)
    op.alter_column("wardrobe_items", "occasion_tags", nullable=False)
    op.drop_column("wardrobe_items", "attributes")
