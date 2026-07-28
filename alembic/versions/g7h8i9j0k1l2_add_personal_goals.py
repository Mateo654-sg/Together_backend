"""add personal goals support

Revision ID: g7h8i9j0k1l2
Revises: b8c9d0e1f2a3
Create Date: 2026-07-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g7h8i9j0k1l2'
down_revision: Union[str, None] = 'b8c9d0e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('goals', 'couple_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.add_column('goals', sa.Column('user_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'goals', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_goals_user_id', 'goals', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_goals_user_id', table_name='goals')
    op.drop_constraint(None, 'goals', type_='foreignkey')
    op.drop_column('goals', 'user_id')
    op.alter_column('goals', 'couple_id',
               existing_type=sa.UUID(),
               nullable=False)
