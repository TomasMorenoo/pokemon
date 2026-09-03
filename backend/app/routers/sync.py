from fastapi import APIRouter, Depends, HTTPException
from parsers.base.types import SaveParseError
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.auth_service import get_current_user
from ..services.sync_service import SyncService
from ..schemas.sync import SyncPreviewOut, SyncConfirmIn, SyncResultOut
from ..models.user import User
from ..schemas.sync import BatchPreviewOut, BatchConfirmIn

router = APIRouter()


@router.post("/preview-all", response_model=BatchPreviewOut)
async def preview_all(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return BatchPreviewOut(previews=await SyncService(db).preview_all(current_user.id))
    except Exception as exc:
        await db.rollback()
        if isinstance(exc, (ValueError, SaveParseError)):
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise


@router.post("/confirm-all", response_model=list[SyncResultOut])
async def confirm_all(body: BatchConfirmIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await SyncService(db).confirm_all(current_user.id, body.sync_session_ids)
    except Exception as exc:
        await db.rollback()
        if isinstance(exc, (ValueError, SaveParseError)):
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        raise HTTPException(status_code=502, detail="No se pudo completar la sincronización. No se aplicaron cambios.") from exc


@router.post("/preview", response_model=SyncPreviewOut)
async def sync_preview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download .sav from Drive, parse it, compute diff — but don't commit yet."""
    service = SyncService(db)
    try:
        return await service.preview(current_user.id)
    except (ValueError, SaveParseError) as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/confirm", response_model=SyncResultOut)
async def sync_confirm(
    body: SyncConfirmIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply a previously previewed sync."""
    service = SyncService(db)
    try:
        return await service.confirm(current_user.id, body.sync_session_id)
    except (ValueError, SaveParseError) as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
