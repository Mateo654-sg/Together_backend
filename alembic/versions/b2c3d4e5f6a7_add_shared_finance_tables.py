"""add shared finance tables: shared_categories, shared_expenses, shared_incomes, debts

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-22 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla shared_categories (Tabla 7 — Documento 07)
    op.create_table('shared_categories',
    sa.Column('couple_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shared_categories_couple_id'), 'shared_categories', ['couple_id'], unique=False)

    # Tabla shared_expenses (Tabla 8 — Documento 07)
    op.create_table('shared_expenses',
    sa.Column('couple_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=True),
    sa.Column('paid_by', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('split_type', sa.Enum('EQUAL', 'PERCENTAGE', 'CUSTOM', name='split_type'), nullable=False),
    sa.Column('split_details', sa.Text(), nullable=True),
    sa.Column('expense_date', sa.Date(), nullable=False),
    sa.Column('attachment_url', sa.String(length=500), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['shared_categories.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['paid_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shared_expenses_couple_id'), 'shared_expenses', ['couple_id'], unique=False)
    op.create_index(op.f('ix_shared_expenses_paid_by'), 'shared_expenses', ['paid_by'], unique=False)
    op.create_index(op.f('ix_shared_expenses_expense_date'), 'shared_expenses', ['expense_date'], unique=False)

    # Tabla shared_incomes (Tabla 9 — Documento 07)
    op.create_table('shared_incomes',
    sa.Column('couple_id', sa.UUID(), nullable=False),
    sa.Column('received_by', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('income_date', sa.Date(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['received_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shared_incomes_couple_id'), 'shared_incomes', ['couple_id'], unique=False)
    op.create_index(op.f('ix_shared_incomes_income_date'), 'shared_incomes', ['income_date'], unique=False)

    # Tabla debts (Tabla 10 — Documento 07)
    op.create_table('debts',
    sa.Column('debtor_id', sa.UUID(), nullable=False),
    sa.Column('creditor_id', sa.UUID(), nullable=False),
    sa.Column('shared_expense_id', sa.UUID(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'PAID', 'CANCELLED', name='debt_status'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['creditor_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['debtor_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['shared_expense_id'], ['shared_expenses.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_debts_debtor_id'), 'debts', ['debtor_id'], unique=False)
    op.create_index(op.f('ix_debts_creditor_id'), 'debts', ['creditor_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_debts_creditor_id'), table_name='debts')
    op.drop_index(op.f('ix_debts_debtor_id'), table_name='debts')
    op.drop_table('debts')

    op.drop_index(op.f('ix_shared_incomes_income_date'), table_name='shared_incomes')
    op.drop_index(op.f('ix_shared_incomes_couple_id'), table_name='shared_incomes')
    op.drop_table('shared_incomes')

    op.drop_index(op.f('ix_shared_expenses_expense_date'), table_name='shared_expenses')
    op.drop_index(op.f('ix_shared_expenses_paid_by'), table_name='shared_expenses')
    op.drop_index(op.f('ix_shared_expenses_couple_id'), table_name='shared_expenses')
    op.drop_table('shared_expenses')

    op.drop_index(op.f('ix_shared_categories_couple_id'), table_name='shared_categories')
    op.drop_table('shared_categories')
