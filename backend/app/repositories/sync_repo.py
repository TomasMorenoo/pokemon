from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.sync import SyncSession


class SyncRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session: SyncSession) -> SyncSession:
        self.db.add(session)
        await self.db.flush()
        return session

    async def get(self, session_id: int, user_id: int) -> SyncSession | None:
        result = await self.db.execute(
            select(SyncSession).where(
                SyncSession.id == session_id,
                SyncSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, session: SyncSession) -> SyncSession:
        await self.db.flush()
        return session
