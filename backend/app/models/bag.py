from sqlalchemy import Integer, String, UniqueConstraint, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class TrainerBag(Base):
    __tablename__ = "trainer_bag"
    __table_args__ = (UniqueConstraint("user_id", "game", name="uq_bag_user_game"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    game: Mapped[str] = mapped_column(String(16), nullable=False, default="firered", server_default="firered")
    tms: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
