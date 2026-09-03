from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class SyncSession(Base):
    """Record of one synchronization run."""
    __tablename__ = "sync_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(16), default="pending")
    # pending → running → completed / failed

    drive_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    drive_modified_time: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Summary counts
    new_pokemon_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_pokemon_count: Mapped[int] = mapped_column(Integer, default=0)
    unchanged_count: Mapped[int] = mapped_column(Integer, default=0)

    # Full diff result stored as JSON for preview/confirmation
    diff_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
