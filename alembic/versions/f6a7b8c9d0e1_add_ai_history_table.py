"""add ai_history table

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-22 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla ai_history
    op.create_table('ai_history',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('endpoint', sa.String(length=100), nullable=False),
    sa.Column('tokens_input', sa.Integer(), nullable=False),
    sa.Column('tokens_output', sa.Integer(), nullable=False),
    sa.Column('cost_usd', sa.Float(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('response_time_ms', sa.Integer(), nullable=False),
    sa.Column('feedback', sa.Integer(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_history_user_id'), 'ai_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_ai_history_endpoint'), 'ai_history', ['endpoint'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_history_endpoint'), table_name='ai_history')
    op.drop_index(op.f('ix_ai_history_user_id'), table_name='ai_history')
    op.drop_table('ai_history')
