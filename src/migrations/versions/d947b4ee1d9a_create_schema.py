"""create schema

Revision ID: d947b4ee1d9a
Revises: 
Create Date: 2025-03-03 14:37:27.371612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd947b4ee1d9a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS etl')


def downgrade() -> None:
    pass
