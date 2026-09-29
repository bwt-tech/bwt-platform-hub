"""composite_unique_email_phone_contact_info

Revision ID: b710c5b8fd97
Revises: c4d5e6f7a8b9
Create Date: 2026-09-29 11:20:26.402081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b710c5b8fd97'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Substitui as unique constraints individuais de email e phone por uma constraint única composta (email, phone)."""
    # Drop individual unique constraints on contact_info
    # Alembic/Postgres or SQLite: drop individual unique constraints
    op.drop_constraint("contact_info_email_key", "contact_info", type_="unique")
    op.drop_constraint("contact_info_phone_key", "contact_info", type_="unique")

    # Create composite unique constraint on (email, phone)
    op.create_unique_constraint(
        "uq_contact_info_email_phone",
        "contact_info",
        ["email", "phone"],
    )


def downgrade() -> None:
    """Restaura as unique constraints individuais de email e phone e remove a composta."""
    op.drop_constraint(
        "uq_contact_info_email_phone",
        "contact_info",
        type_="unique",
    )
    op.create_unique_constraint("contact_info_phone_key", "contact_info", ["phone"])
    op.create_unique_constraint("contact_info_email_key", "contact_info", ["email"])
