"""widen avatar_url to Text

Revision ID: c6d7e8f9a0b1
Revises: c5d6e7f8a9b0
Create Date: 2026-08-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6d7e8f9a0b1'
down_revision: Union[str, None] = 'c5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'users',
        'avatar_url',
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'users',
        'avatar_url',
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
