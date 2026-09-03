from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..services.auth_service import get_current_user
from ..models.user import User
from ..models.bag import TrainerBag

router = APIRouter()

@router.get("/")
async def get_bag(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrainerBag).where(TrainerBag.user_id == current_user.id))
    bag = result.scalar_one_or_none()
    return {"tms": bag.tms if bag else []}
