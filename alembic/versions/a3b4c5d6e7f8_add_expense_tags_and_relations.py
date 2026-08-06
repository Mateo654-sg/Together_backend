"""add expense tags and relations

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-08-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla expense_tags (etiquetas de gastos — FR-026)
    op.create_table('expense_tags',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expense_tags_user_id'), 'expense_tags', ['user_id'], unique=False)

    # Tabla expense_tag_relation (relación N:M gastos <-> etiquetas — Tabla 35)
    op.create_table('expense_tag_relation',
    sa.Column('expense_id', sa.UUID(), nullable=False),
    sa.Column('tag_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['expense_id'], ['personal_expenses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['expense_tags.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('expense_id', 'tag_id')
    )


def downgrade() -> None:
    op.drop_table('expense_tag_relation')
    op.drop_index(op.f('ix_expense_tags_user_id'), table_name='expense_tags')
    op.drop_table('expense_tags')
