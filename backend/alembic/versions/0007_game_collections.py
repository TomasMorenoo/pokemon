from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE pokemon_instances SET game = 'firered' WHERE added_via = 'sync' AND game IS NULL")
    op.drop_constraint("uq_pokemon_identity", "pokemon_instances", type_="unique")
    op.create_unique_constraint("uq_pokemon_identity", "pokemon_instances", ["user_id", "game", "pid", "ot_id", "ot_secret_id"])
    op.add_column("trainer_bag", sa.Column("game", sa.String(16), nullable=False, server_default="firered"))
    op.drop_index("ix_trainer_bag_user_id", table_name="trainer_bag")
    op.create_index("ix_trainer_bag_user_id", "trainer_bag", ["user_id"])
    op.create_unique_constraint("uq_bag_user_game", "trainer_bag", ["user_id", "game"])
    op.add_column("drive_configs", sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("""UPDATE drive_configs d SET synced_at = (
        SELECT max(s.completed_at) FROM sync_sessions s
        WHERE s.user_id = d.user_id AND s.status = 'completed'
    ) WHERE d.game = 'firered'""")


def downgrade() -> None:
    if op.get_bind().execute(sa.text("SELECT count(*) FROM pokemon_instances WHERE game <> 'firered' AND added_via = 'sync'")).scalar():
        raise RuntimeError("Cannot downgrade while other games have synchronized collections.")
    op.drop_column("drive_configs", "synced_at")
    op.drop_constraint("uq_bag_user_game", "trainer_bag", type_="unique")
    op.drop_index("ix_trainer_bag_user_id", table_name="trainer_bag")
    op.create_index("ix_trainer_bag_user_id", "trainer_bag", ["user_id"], unique=True)
    op.drop_column("trainer_bag", "game")
    op.drop_constraint("uq_pokemon_identity", "pokemon_instances", type_="unique")
    op.create_unique_constraint("uq_pokemon_identity", "pokemon_instances", ["user_id", "pid", "ot_id", "ot_secret_id"])
