"""add_motorcycle_to_asset_type_enum

Revision ID: e59148323266
Revises: a463b296fdce
Create Date: 2026-09-27 22:22:07.288860

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e59148323266'
down_revision: Union[str, Sequence[str], None] = 'a463b296fdce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add 'MOTORCYCLE' to asset_type_enum."""
    op.execute("ALTER TYPE asset_type_enum ADD VALUE IF NOT EXISTS 'MOTORCYCLE'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
