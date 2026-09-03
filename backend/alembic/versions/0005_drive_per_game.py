from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drive_configs", sa.Column("game", sa.String(16), nullable=False, server_default="firered"))
    op.drop_index("ix_drive_configs_user_id", table_name="drive_configs")
    op.create_index("ix_drive_configs_user_id", "drive_configs", ["user_id"])
    op.create_unique_constraint("uq_drive_user_game", "drive_configs", ["user_id", "game"])


def downgrade() -> None:
    count = op.get_bind().execute(sa.text("SELECT count(*) FROM drive_configs WHERE game <> 'firered'")).scalar()
    if count:
        raise RuntimeError("Cannot downgrade while other games have configured saves.")
    op.drop_constraint("uq_drive_user_game", "drive_configs", type_="unique")
    op.drop_index("ix_drive_configs_user_id", table_name="drive_configs")
    op.create_index("ix_drive_configs_user_id", "drive_configs", ["user_id"], unique=True)
    op.drop_column("drive_configs", "game")
