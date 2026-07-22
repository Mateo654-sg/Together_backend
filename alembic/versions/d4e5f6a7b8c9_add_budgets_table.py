"""add budgets table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-22 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla budgets (Tabla 14 — Documento 07)
    op.create_table('budgets',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['personal_categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budgets_user_id'), 'budgets', ['user_id'], unique=False)
    op.create_index(op.f('ix_budgets_category_id'), 'budgets', ['category_id'], unique=False)
    op.create_index(op.f('ix_budgets_month_year'), 'budgets', ['month', 'year'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_budgets_month_year'), table_name='budgets')
    op.drop_index(op.f('ix_budgets_category_id'), table_name='budgets')
    op.drop_index(op.f('ix_budgets_user_id'), table_name='budgets')
    op.drop_table('budgets')
