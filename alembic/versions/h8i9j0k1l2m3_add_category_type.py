"""add type column to personal_categories

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-07-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'h8i9j0k1l2m3'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('personal_categories', sa.Column('type', sa.String(20), nullable=False, server_default='expense'))
    op.execute("UPDATE personal_categories SET type = 'income' WHERE name IN ('Salario', 'Freelance', 'Inversiones', 'Regalos')")


def downgrade() -> None:
    op.drop_column('personal_categories', 'type')
