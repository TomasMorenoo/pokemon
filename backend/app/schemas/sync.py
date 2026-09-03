from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ParsedPokemonPreview(BaseModel):
    species_name: str
    species_id: int
    nickname: str
    level: int
    nature_name: str
    gender: str
    is_shiny: bool
    pid: int
    ot_id: int


class SyncDiffItem(BaseModel):
    status: str  # "new" | "updated" | "unchanged"
    pokemon: ParsedPokemonPreview
    changes: Optional[dict] = None  # For "updated": what changed


class SyncPreviewOut(BaseModel):
    sync_session_id: int
    new_count: int
    updated_count: int
    unchanged_count: int
    items: list[SyncDiffItem]


class SyncConfirmIn(BaseModel):
    sync_session_id: int


class SyncResultOut(BaseModel):
    sync_session_id: int
    status: str
    new_count: int
    updated_count: int
    unchanged_count: int
    completed_at: Optional[datetime]
