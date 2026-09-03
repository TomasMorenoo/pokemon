from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.auth_service import get_current_user
from ..services.sync_service import SyncService
from ..schemas.sync import SyncPreviewOut, SyncConfirmIn, SyncResultOut
from ..models.user import User

router = APIRouter()


@router.post("/preview", response_model=SyncPreviewOut)
async def sync_preview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download .sav from Drive, parse it, compute diff — but don't commit yet."""
    service = SyncService(db)
    return await service.preview(current_user.id)


@router.post("/confirm", response_model=SyncResultOut)
async def sync_confirm(
    body: SyncConfirmIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply a previously previewed sync."""
    service = SyncService(db)
    return await service.confirm(current_user.id, body.sync_session_id)
