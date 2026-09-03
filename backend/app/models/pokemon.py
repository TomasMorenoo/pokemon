from datetime import datetime
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, DateTime, Text, SmallInteger,
    ForeignKey, UniqueConstraint, func, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class PokemonInstance(Base):
    """One unique individual Pokémon. Identity key: (user_id, pid, ot_id, ot_secret_id)."""
    __tablename__ = "pokemon_instances"
    __table_args__ = (
        UniqueConstraint("user_id", "pid", "ot_id", "ot_secret_id", name="uq_pokemon_identity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)

    # Core identity from save
    pid: Mapped[int] = mapped_column(BigInteger, nullable=False)         # Personality Value
    ot_id: Mapped[int] = mapped_column(BigInteger, nullable=False)       # OT Public ID
    ot_secret_id: Mapped[int] = mapped_column(BigInteger, nullable=False) # OT Secret ID

    # Species
    species_id: Mapped[int] = mapped_column(Integer, nullable=False)
    species_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Current state (denormalized from latest measurement for quick access)
    nickname: Mapped[str | None] = mapped_column(String(32), nullable=True)
    current_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    current_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Fixed attributes (don't change)
    nature_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nature_name: Mapped[str | None] = mapped_column(String(32), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(1), nullable=True)  # M/F/N
    is_shiny: Mapped[bool] = mapped_column(Boolean, default=False)
    ability_slot: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ot_name: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Origin metadata
    origin: Mapped[str] = mapped_column(String(32), default="unknown")  # captured/traded/transferred/unknown
    game: Mapped[str | None] = mapped_column(String(32), nullable=True)  # firered/leafgreen/etc
    generation: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    form_name: Mapped[str | None] = mapped_column(String(64), nullable=True)  # alola/galar/hisui/etc

    # Position in save (updated each sync; None = box Pokemon)
    party_slot: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # Source
    added_via: Mapped[str] = mapped_column(String(16), default="sync")  # sync / manual

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    measurements: Mapped[list["PokemonMeasurement"]] = relationship(
        "PokemonMeasurement", back_populates="instance", order_by="PokemonMeasurement.recorded_at"
    )


class PokemonMeasurement(Base):
    """Historical snapshot of a Pokémon's state at a point in time."""
    __tablename__ = "pokemon_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(ForeignKey("pokemon_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    sync_session_id: Mapped[int | None] = mapped_column(ForeignKey("sync_sessions.id"), nullable=True)

    # Snapshot data
    level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Stats (None = not available/calculated yet)
    hp: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    attack: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    defense: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    speed: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sp_attack: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sp_defense: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # IVs (source: save/calculated/manual/unknown)
    iv_hp: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    iv_attack: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    iv_defense: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    iv_speed: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    iv_sp_attack: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    iv_sp_defense: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    iv_source: Mapped[str] = mapped_column(String(16), default="unknown")

    # EVs
    ev_hp: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ev_attack: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ev_defense: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ev_speed: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ev_sp_attack: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ev_sp_defense: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ev_source: Mapped[str] = mapped_column(String(16), default="unknown")

    # Moves stored as JSON array of {move_id, move_name, pp, pp_max}
    moves: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Held item
    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    item_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Data origin
    data_source: Mapped[str] = mapped_column(String(16), default="sync")  # sync/manual

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    instance: Mapped["PokemonInstance"] = relationship("PokemonInstance", back_populates="measurements")
