"""add_timestamps_to_entities

Revision ID: a1b2c3d4e5f6
Revises: 0c6e3a5af8f8
Create Date: 2026-07-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0c6e3a5af8f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add created_at and updated_at columns to chat, contact and deal tables."""
    for table in ('chat', 'contact', 'deal'):
        op.add_column(table, sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
        op.add_column(table, sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Remove created_at and updated_at columns from chat, contact and deal tables."""
    for table in ('deal', 'contact', 'chat'):
        op.drop_column(table, 'updated_at')
        op.drop_column(table, 'created_at')
