"""add goals and goal_contributions tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-22 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla goals (Tabla 12 — Documento 07)
    op.create_table('goals',
    sa.Column('couple_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('image', sa.String(length=500), nullable=True),
    sa.Column('target_amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('current_amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'CANCELLED', name='goal_status'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_couple_id'), 'goals', ['couple_id'], unique=False)
    op.create_index(op.f('ix_goals_status'), 'goals', ['status'], unique=False)

    # Tabla goal_contributions (Tabla 13 — Documento 07)
    op.create_table('goal_contributions',
    sa.Column('goal_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('contribution_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goal_contributions_goal_id'), 'goal_contributions', ['goal_id'], unique=False)
    op.create_index(op.f('ix_goal_contributions_user_id'), 'goal_contributions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_goal_contributions_user_id'), table_name='goal_contributions')
    op.drop_index(op.f('ix_goal_contributions_goal_id'), table_name='goal_contributions')
    op.drop_table('goal_contributions')

    op.drop_index(op.f('ix_goals_status'), table_name='goals')
    op.drop_index(op.f('ix_goals_couple_id'), table_name='goals')
    op.drop_table('goals')
