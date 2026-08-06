"""add transfers table

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-08-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c5d6e7f8a9'
down_revision: Union[str, None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla transfers (transferencias entre métodos de pago — FR-021)
    op.create_table('transfers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('from_method', sa.String(length=50), nullable=False),
    sa.Column('to_method', sa.String(length=50), nullable=False),
    sa.Column('amount', sa.Numeric(12, 2), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('transfer_date', sa.Date(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transfers_user_id'), 'transfers', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_transfers_user_id'), table_name='transfers')
    op.drop_table('transfers')
