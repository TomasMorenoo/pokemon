from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from .game import Game


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
    game: Game = "firered"
    status: str  # "new" | "updated" | "unchanged" | "removed"
    pokemon: ParsedPokemonPreview
    changes: Optional[dict] = None  # For "updated": what changed


class SyncPreviewOut(BaseModel):
    game: Game = "firered"
    sync_session_id: int
    new_count: int
    updated_count: int
    unchanged_count: int
    removed_count: int = 0
    items: list[SyncDiffItem]


class SyncConfirmIn(BaseModel):
    sync_session_id: int


class SyncResultOut(BaseModel):
    game: Game = "firered"
    sync_session_id: int
    status: str
    new_count: int
    updated_count: int
    unchanged_count: int
    removed_count: int = 0
    completed_at: Optional[datetime]


class BatchPreviewOut(BaseModel):
    previews: list[SyncPreviewOut]


class BatchConfirmIn(BaseModel):
    sync_session_ids: list[int]
