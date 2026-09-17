"""Add origin column to reminders table

Revision ID: add_reminder_origin
Revises: eedbb6739860
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_reminder_origin'
down_revision = 'eedbb6739860'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the enum type
    reminderorigin = sa.Enum('automatic', 'custom', name='reminderorigin')
    reminderorigin.create(op.get_bind(), checkfirst=True)

    # Add the origin column with default 'custom'
    op.add_column(
        'reminders',
        sa.Column(
            'origin',
            sa.Enum('automatic', 'custom', name='reminderorigin'),
            nullable=False,
            server_default='custom',
        ),
    )


def downgrade() -> None:
    op.drop_column('reminders', 'origin')
    sa.Enum(name='reminderorigin').drop(op.get_bind(), checkfirst=True)
