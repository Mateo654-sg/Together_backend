"""add chat_messages table

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-07-22 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla chat_messages (Chat de Pareja)
    op.create_table('chat_messages',
    sa.Column('sender_id', sa.UUID(), nullable=False),
    sa.Column('receiver_id', sa.UUID(), nullable=False),
    sa.Column('message_type', sa.Enum('TEXT', 'EMOJI', 'MOTIVATIONAL', 'SHARE_GOAL', 'SHARE_MOVEMENT', name='message_type'), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('shared_entity_id', sa.UUID(), nullable=True),
    sa.Column('shared_entity_type', sa.String(length=50), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('attachment_url', sa.String(length=500), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_sender_id'), 'chat_messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_receiver_id'), 'chat_messages', ['receiver_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_created_at'), 'chat_messages', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_messages_created_at'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_receiver_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_sender_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
