"""add_app_url_index

Revision ID: 4a8b2c9d3e0f
Revises: 3169e8bfb108
Create Date: 2026-01-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4a8b2c9d3e0f'
down_revision: Union[str, Sequence[str], None] = '3169e8bfb108'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index on app_url for faster duplicate detection queries."""
    op.create_index(op.f('ix_apps_app_url'), 'apps', ['app_url'], unique=False)


def downgrade() -> None:
    """Remove app_url index."""
    op.drop_index(op.f('ix_apps_app_url'), table_name='apps')
