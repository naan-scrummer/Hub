"""Notification schema refinement and processing status

Revision ID: 20260917_001
Revises: add_reminder_origin
Create Date: 2026-09-17 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260917_001'
down_revision = 'add_reminder_origin'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check/add processing_status column
    try:
        processingstatus = sa.Enum('pending', 'processed', 'failed', name='processingstatus')
        processingstatus.create(op.get_bind(), checkfirst=True)
    except Exception:
        pass

    try:
        op.add_column(
            'notifications',
            sa.Column('processing_status', sa.String(length=20), server_default='pending', nullable=False)
        )
    except Exception:
        pass

    try:
        op.add_column(
            'notifications',
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
        )
    except Exception:
        pass

    try:
        op.create_index('idx_notifications_student_status', 'notifications', ['student_id', 'status'])
    except Exception:
        pass

    try:
        op.create_index('idx_notifications_processing_status', 'notifications', ['processing_status'])
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_index('idx_notifications_processing_status', table_name='notifications')
    except Exception:
        pass
    try:
        op.drop_index('idx_notifications_student_status', table_name='notifications')
    except Exception:
        pass
    try:
        op.drop_column('notifications', 'updated_at')
    except Exception:
        pass
    try:
        op.drop_column('notifications', 'processing_status')
    except Exception:
        pass
