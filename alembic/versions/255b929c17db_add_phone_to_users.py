"""add_phone_to_users

Revision ID: 255b929c17db
Revises: 70315ba8e3a3
Create Date: 2026-10-06 20:56:42.275829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '255b929c17db'
down_revision: Union[str, Sequence[str], None] = '70315ba8e3a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('phone', sa.String(20), nullable=True)
    )
    # Index ham qo'shamiz:
    op.create_index(
        'ix_users_phone',
        'users',
        ['phone'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_users_phone', table_name='users')
    op.drop_column('users', 'phone')
