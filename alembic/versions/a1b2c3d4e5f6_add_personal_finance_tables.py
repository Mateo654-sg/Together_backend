"""add personal finances tables: personal_categories, personal_expenses, personal_incomes

Revision ID: a1b2c3d4e5f6
Revises: 354ed9eafb6f
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '354ed9eafb6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla personal_categories (Tabla 4 — Documento 07)
    op.create_table('personal_categories',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_categories_user_id'), 'personal_categories', ['user_id'], unique=False)

    # Tabla personal_expenses (Tabla 5 — Documento 07)
    op.create_table('personal_expenses',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('payment_method', sa.String(length=50), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=True),
    sa.Column('attachment_url', sa.String(length=500), nullable=True),
    sa.Column('expense_date', sa.Date(), nullable=False),
    sa.Column('is_favorite', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['personal_categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_expenses_user_id'), 'personal_expenses', ['user_id'], unique=False)
    op.create_index(op.f('ix_personal_expenses_category_id'), 'personal_expenses', ['category_id'], unique=False)
    op.create_index(op.f('ix_personal_expenses_expense_date'), 'personal_expenses', ['expense_date'], unique=False)

    # Tabla personal_incomes (Tabla 6 — Documento 07)
    op.create_table('personal_incomes',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('income_date', sa.Date(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['personal_categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_incomes_user_id'), 'personal_incomes', ['user_id'], unique=False)
    op.create_index(op.f('ix_personal_incomes_category_id'), 'personal_incomes', ['category_id'], unique=False)
    op.create_index(op.f('ix_personal_incomes_income_date'), 'personal_incomes', ['income_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_personal_incomes_income_date'), table_name='personal_incomes')
    op.drop_index(op.f('ix_personal_incomes_category_id'), table_name='personal_incomes')
    op.drop_index(op.f('ix_personal_incomes_user_id'), table_name='personal_incomes')
    op.drop_table('personal_incomes')

    op.drop_index(op.f('ix_personal_expenses_expense_date'), table_name='personal_expenses')
    op.drop_index(op.f('ix_personal_expenses_category_id'), table_name='personal_expenses')
    op.drop_index(op.f('ix_personal_expenses_user_id'), table_name='personal_expenses')
    op.drop_table('personal_expenses')

    op.drop_index(op.f('ix_personal_categories_user_id'), table_name='personal_categories')
    op.drop_table('personal_categories')
