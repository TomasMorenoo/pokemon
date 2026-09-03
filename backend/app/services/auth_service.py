from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..database import get_db
from fastapi import Depends


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Single-user app — always return user id=1, create if not exists."""
    result = await db.execute(select(User).where(User.id == 1))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=1, google_id="local", email="local@pokedex", name="Trainer")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
