"""add reminders and notifications tables

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-07-22 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla reminders (Recordatorios)
    op.create_table('reminders',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('repeat_type', sa.Enum('NONE', 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', name='reminder_repeat_type'), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('amount', sa.String(length=50), nullable=True),
    sa.Column('notification_sent', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminders_user_id'), 'reminders', ['user_id'], unique=False)
    op.create_index(op.f('ix_reminders_due_date'), 'reminders', ['due_date'], unique=False)

    # Tabla notifications (Notificaciones)
    op.create_table('notifications',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('notification_type', sa.Enum('PUSH', 'EMAIL', 'IN_APP', name='notification_type'), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('link', sa.String(length=500), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')

    op.drop_index(op.f('ix_reminders_due_date'), table_name='reminders')
    op.drop_index(op.f('ix_reminders_user_id'), table_name='reminders')
    op.drop_table('reminders')
