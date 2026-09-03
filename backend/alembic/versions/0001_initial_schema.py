"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("google_id", sa.String(128), nullable=False, unique=True),
        sa.Column("email", sa.String(256), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("picture_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "oauth_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.Text(), default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "drive_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, unique=True, index=True),
        sa.Column("file_id", sa.String(256), nullable=False),
        sa.Column("file_name", sa.String(512), nullable=False),
        sa.Column("folder_id", sa.String(256), nullable=True),
        sa.Column("last_drive_modified", sa.String(64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "sync_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("status", sa.String(16), default="pending"),
        sa.Column("drive_file_id", sa.String(256), nullable=True),
        sa.Column("drive_modified_time", sa.String(64), nullable=True),
        sa.Column("new_pokemon_count", sa.Integer(), default=0),
        sa.Column("updated_pokemon_count", sa.Integer(), default=0),
        sa.Column("unchanged_count", sa.Integer(), default=0),
        sa.Column("diff_result", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "pokemon_instances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("pid", sa.Integer(), nullable=False),
        sa.Column("ot_id", sa.Integer(), nullable=False),
        sa.Column("ot_secret_id", sa.Integer(), nullable=False),
        sa.Column("species_id", sa.Integer(), nullable=False),
        sa.Column("species_name", sa.String(64), nullable=False),
        sa.Column("nickname", sa.String(32), nullable=True),
        sa.Column("current_level", sa.SmallInteger(), nullable=True),
        sa.Column("current_experience", sa.Integer(), nullable=True),
        sa.Column("nature_id", sa.SmallInteger(), nullable=True),
        sa.Column("nature_name", sa.String(32), nullable=True),
        sa.Column("gender", sa.String(1), nullable=True),
        sa.Column("is_shiny", sa.Boolean(), default=False),
        sa.Column("ability_slot", sa.SmallInteger(), nullable=True),
        sa.Column("ot_name", sa.String(32), nullable=True),
        sa.Column("origin", sa.String(32), default="unknown"),
        sa.Column("game", sa.String(32), nullable=True),
        sa.Column("generation", sa.SmallInteger(), nullable=True),
        sa.Column("added_via", sa.String(16), default="sync"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "pid", "ot_id", "ot_secret_id", name="uq_pokemon_identity"),
    )

    op.create_table(
        "pokemon_measurements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("instance_id", sa.Integer(), sa.ForeignKey("pokemon_instances.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sync_session_id", sa.Integer(), sa.ForeignKey("sync_sessions.id"), nullable=True),
        sa.Column("level", sa.SmallInteger(), nullable=True),
        sa.Column("experience", sa.Integer(), nullable=True),
        sa.Column("nickname", sa.String(32), nullable=True),
        sa.Column("hp", sa.SmallInteger(), nullable=True),
        sa.Column("attack", sa.SmallInteger(), nullable=True),
        sa.Column("defense", sa.SmallInteger(), nullable=True),
        sa.Column("speed", sa.SmallInteger(), nullable=True),
        sa.Column("sp_attack", sa.SmallInteger(), nullable=True),
        sa.Column("sp_defense", sa.SmallInteger(), nullable=True),
        sa.Column("iv_hp", sa.SmallInteger(), nullable=True),
        sa.Column("iv_attack", sa.SmallInteger(), nullable=True),
        sa.Column("iv_defense", sa.SmallInteger(), nullable=True),
        sa.Column("iv_speed", sa.SmallInteger(), nullable=True),
        sa.Column("iv_sp_attack", sa.SmallInteger(), nullable=True),
        sa.Column("iv_sp_defense", sa.SmallInteger(), nullable=True),
        sa.Column("iv_source", sa.String(16), default="unknown"),
        sa.Column("ev_hp", sa.SmallInteger(), nullable=True),
        sa.Column("ev_attack", sa.SmallInteger(), nullable=True),
        sa.Column("ev_defense", sa.SmallInteger(), nullable=True),
        sa.Column("ev_speed", sa.SmallInteger(), nullable=True),
        sa.Column("ev_sp_attack", sa.SmallInteger(), nullable=True),
        sa.Column("ev_sp_defense", sa.SmallInteger(), nullable=True),
        sa.Column("ev_source", sa.String(16), default="unknown"),
        sa.Column("moves", postgresql.JSONB(), nullable=True),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("item_name", sa.String(64), nullable=True),
        sa.Column("data_source", sa.String(16), default="sync"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("pokemon_measurements")
    op.drop_table("pokemon_instances")
    op.drop_table("sync_sessions")
    op.drop_table("drive_configs")
    op.drop_table("oauth_tokens")
    op.drop_table("users")
