"""add_indexes_to_deal_and_chat

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-08-04 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona índices em deal.contact_id e chat.contact_id para otimizar lookups por FK."""
    op.create_index("ix_deal_contact_id", "deal", ["contact_id"])
    op.create_index("ix_deal_contact_id_rdstation_id", "deal", ["contact_id", "rdstation_id"])
    op.create_index("ix_chat_contact_id", "chat", ["contact_id"])


def downgrade() -> None:
    """Remove os índices de FK adicionados."""
    op.drop_index("ix_chat_contact_id", table_name="chat")
    op.drop_index("ix_deal_contact_id_rdstation_id", table_name="deal")
    op.drop_index("ix_deal_contact_id", table_name="deal")
