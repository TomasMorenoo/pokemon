import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.drive import DriveConfig


def _public_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"


def _extract_file_id(url_or_id: str) -> str:
    """Accept a full Drive URL or bare file ID."""
    if "drive.google.com" in url_or_id:
        # https://drive.google.com/file/d/FILE_ID/view...
        parts = url_or_id.split("/d/")
        if len(parts) > 1:
            return parts[1].split("/")[0].split("?")[0]
    return url_or_id.strip()


class DriveService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_config(self, user_id: int, file_id: str, file_name: str, folder_id: str | None = None) -> dict:
        file_id = _extract_file_id(file_id)
        result = await self.db.execute(
            select(DriveConfig).where(DriveConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        if not config:
            config = DriveConfig(
                user_id=user_id,
                file_id=file_id,
                file_name=file_name,
                folder_id=folder_id,
            )
            self.db.add(config)
        else:
            config.file_id = file_id
            config.file_name = file_name
            config.folder_id = folder_id
        await self.db.commit()
        return {"file_id": file_id, "file_name": file_name}

    async def get_config(self, user_id: int) -> dict | None:
        result = await self.db.execute(
            select(DriveConfig).where(DriveConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        if not config:
            return None
        return {
            "file_id": config.file_id,
            "file_name": config.file_name,
            "folder_id": config.folder_id,
            "last_drive_modified": config.last_drive_modified,
        }

    async def download_sav(self, user_id: int) -> tuple[bytes, str]:
        """Download .sav from public Drive link. Returns (data, modified_time)."""
        config = await self.get_config(user_id)
        if not config:
            raise ValueError("No Drive file configured. Configure one in Settings.")

        url = _public_download_url(config["file_id"])
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.content

        if len(data) < 1000:
            raise ValueError("Downloaded file is too small — check the Drive link is public and correct.")

        return data, ""

    async def download_sav_by_url(self, url_or_id: str) -> bytes:
        """One-off download by URL or file ID (for testing)."""
        file_id = _extract_file_id(url_or_id)
        url = _public_download_url(file_id)
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
