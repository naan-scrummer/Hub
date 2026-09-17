"""Create notifications table migration.

Revision ID: 20260918_001
Revises: 
Create Date: 2026-09-18 03:02:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260918_001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column(
            "source",
            sa.Enum(
                "assignment_deadline",
                "reminder_trigger",
                "announcement",
                "examination",
                "placement",
                name="notificationsource",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column("source_id", sa.Integer, nullable=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column(
            "status",
            sa.Enum("unread", "read", "archived", name="notificationstatus"),
            nullable=False,
            server_default="unread",
            index=True,
        ),
        sa.Column(
            "processing_status",
            sa.Enum("pending", "processed", "failed", name="processingstatus"),
            nullable=False,
            server_default="pending",
            index=True,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_notifications_student_status_created", "notifications", ["student_id", "status", "created_at"], unique=False)
    op.create_index("idx_notifications_student_status", "notifications", ["student_id", "status"], unique=False)
    op.create_index("idx_notifications_processing_status", "notifications", ["processing_status"], unique=False)

def downgrade():
    op.drop_index("idx_notifications_processing_status", table_name="notifications")
    op.drop_index("idx_notifications_student_status", table_name="notifications")
    op.drop_index("ix_notifications_student_status_created", table_name="notifications")
    op.drop_table("notifications")
