"""add reports table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-22 04:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla reports
    op.create_table('reports',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('report_type', sa.Enum('MONTHLY', 'YEARLY', 'WEEKLY', 'CATEGORY', 'PERSONAL', 'COUPLE', name='report_type'), nullable=False),
    sa.Column('format', sa.Enum('PDF', 'EXCEL', 'CSV', name='report_format'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='report_status'), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('parameters', sa.Text(), nullable=True),
    sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_user_id'), 'reports', ['user_id'], unique=False)
    op.create_index(op.f('ix_reports_report_type'), 'reports', ['report_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_reports_report_type'), table_name='reports')
    op.drop_index(op.f('ix_reports_user_id'), table_name='reports')
    op.drop_table('reports')
