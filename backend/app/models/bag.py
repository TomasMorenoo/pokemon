from sqlalchemy import Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class TrainerBag(Base):
    __tablename__ = "trainer_bag"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    tms: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
