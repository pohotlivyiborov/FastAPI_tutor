"""add column content

Revision ID: caaafddfe950
Revises: 8ea12d29bd42
Create Date: 2026-03-12 18:34:33.113590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caaafddfe950'
down_revision: Union[str, Sequence[str], None] = '8ea12d29bd42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("posts", "content")
    pass
