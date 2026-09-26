"""add_bwt_ids_to_contact_and_deal

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-08-04 10:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona colunas de IDs BWT nas tabelas contact e deal."""
    op.add_column(
        'contact',
        sa.Column('bwt_account_id', sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        'uq_contact_bwt_account_id', 'contact', ['bwt_account_id']
    )

    op.add_column(
        'contact',
        sa.Column('bwt_contact_id', sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        'uq_contact_bwt_contact_id', 'contact', ['bwt_contact_id']
    )

    op.add_column(
        'deal',
        sa.Column('bwt_deal_id', sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        'uq_deal_bwt_deal_id', 'deal', ['bwt_deal_id']
    )

    op.add_column(
        'deal',
        sa.Column('bwt_responsible_id', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Remove colunas de IDs BWT das tabelas contact e deal."""
    op.drop_column('deal', 'bwt_responsible_id')
    op.drop_constraint('uq_deal_bwt_deal_id', 'deal', type_='unique')
    op.drop_column('deal', 'bwt_deal_id')
    op.drop_constraint('uq_contact_bwt_contact_id', 'contact', type_='unique')
    op.drop_column('contact', 'bwt_contact_id')
    op.drop_constraint('uq_contact_bwt_account_id', 'contact', type_='unique')
    op.drop_column('contact', 'bwt_account_id')
