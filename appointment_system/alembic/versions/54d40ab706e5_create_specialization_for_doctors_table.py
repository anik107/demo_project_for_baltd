"""create specialization for doctors table

Revision ID: 54d40ab706e5
Revises:
Create Date: 2025-07-31 23:01:50.279918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54d40ab706e5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'doctor_profiles',
        sa.Column('specialization', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
