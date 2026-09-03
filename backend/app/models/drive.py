from datetime import datetime
from sqlalchemy import String, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class DriveConfig(Base):
    __tablename__ = "drive_configs"
    __table_args__ = (UniqueConstraint("user_id", "game", name="uq_drive_user_game"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    game: Mapped[str] = mapped_column(String(16), nullable=False, default="firered", server_default="firered")
    file_id: Mapped[str] = mapped_column(String(256), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    folder_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    last_drive_modified: Mapped[str | None] = mapped_column(String(64), nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
