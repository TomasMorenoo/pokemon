from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.auth_service import get_current_user
from ..services.drive_service import DriveService
from ..models.user import User
from pydantic import BaseModel
from ..schemas.game import Game
from sqlalchemy import select
from ..models.drive import DriveConfig

router = APIRouter()


@router.get("/configs")
async def list_drive_configs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    configs = (await db.execute(select(DriveConfig).where(DriveConfig.user_id == current_user.id))).scalars()
    return [{"game": c.game, "file_id": c.file_id, "file_name": c.file_name,
             "folder_id": c.folder_id, "last_drive_modified": c.last_drive_modified,
             "synced_at": c.synced_at} for c in configs]


class DriveConfigIn(BaseModel):
    url_or_id: str   # Full Drive share URL or bare file ID
    file_name: str = "partida.sav"
    game: Game = "firered"


@router.post("/config")
async def set_drive_config(
    body: DriveConfigIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DriveService(db)
    return await service.save_config(current_user.id, body.url_or_id, body.file_name, game=body.game)


@router.get("/config")
async def get_drive_config(
    game: Game = "firered",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DriveService(db)
    return await service.get_config(current_user.id, game)
