"""rename_content_to_body_in_posts

Revision ID: 1c764d9dea28
Revises: 255b929c17db
Create Date: 2026-10-06 20:58:03.213214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c764d9dea28'
down_revision: Union[str, Sequence[str], None] = '255b929c17db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'posts',
        'content',      # Eski nom
        new_column_name='body'   # Yangi nom
    )

def downgrade() -> None:
    op.alter_column(
        'posts',
        'body',
        new_column_name='content'
    )
