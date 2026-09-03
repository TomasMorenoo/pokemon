from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.auth_service import get_current_user
from ..services.drive_service import DriveService
from ..models.user import User
from pydantic import BaseModel

router = APIRouter()


class DriveConfigIn(BaseModel):
    url_or_id: str   # Full Drive share URL or bare file ID
    file_name: str = "partida.sav"


@router.post("/config")
async def set_drive_config(
    body: DriveConfigIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DriveService(db)
    return await service.save_config(current_user.id, body.url_or_id, body.file_name)


@router.get("/config")
async def get_drive_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DriveService(db)
    return await service.get_config(current_user.id)
