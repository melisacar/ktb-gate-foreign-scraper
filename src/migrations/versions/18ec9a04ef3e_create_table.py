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
    op.create_table(
        'ist_sinir_gelen_yabanci',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tarih', sa.Date, nullable=True),
        sa.Column('sinir_kapilari', sa.String, nullable=True),
        sa.Column('yabanci_ziyaretci', sa.Float, nullable=True),
        sa.Column('erisim_tarihi', sa.Date, nullable=True),
        sa.UniqueConstraint('tarih','sinir_kapilari','yabanci_ziyaretci', name='unique_ist_sinir_kapi_ziyaretci'),               
        schema='etl'
               )


def downgrade() -> None:
    op.execute("""
                DROP TABLE IF EXISTS etl.ist_sinir_gelen_yabanci
               """)
