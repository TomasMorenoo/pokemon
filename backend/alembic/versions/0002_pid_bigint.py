"""pid bigint

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-21
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('pokemon_instances', 'pid', type_=sa.BigInteger())
    op.alter_column('pokemon_instances', 'ot_id', type_=sa.BigInteger())
    op.alter_column('pokemon_instances', 'ot_secret_id', type_=sa.BigInteger())


def downgrade() -> None:
    op.alter_column('pokemon_instances', 'pid', type_=sa.Integer())
    op.alter_column('pokemon_instances', 'ot_id', type_=sa.Integer())
    op.alter_column('pokemon_instances', 'ot_secret_id', type_=sa.Integer())
