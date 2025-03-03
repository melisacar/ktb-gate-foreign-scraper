"""create table

Revision ID: 18ec9a04ef3e
Revises: d947b4ee1d9a
Create Date: 2025-03-03 14:52:44.918703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18ec9a04ef3e'
down_revision: Union[str, None] = 'd947b4ee1d9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
