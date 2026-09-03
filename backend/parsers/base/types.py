from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DataSource(str, Enum):
    SAVE = "save"
    CALCULATED = "calculated"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class PokemonOrigin(str, Enum):
    CAPTURED = "captured"
    TRADED = "traded"
    TRANSFERRED = "transferred"
    UNKNOWN = "unknown"


@dataclass
class IVSet:
    hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    source: DataSource = DataSource.SAVE


@dataclass
class EVSet:
    hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    source: DataSource = DataSource.SAVE


@dataclass
class MoveSlot:
    move_id: int
    move_name: str
    pp: int
    pp_max: int


@dataclass
class ParsedPokemon:
    # Core identity (stable cross-sync key: pid + ot_id + ot_secret_id)
    pid: int
    ot_id: int
    ot_secret_id: int

    # Species
    species_id: int
    species_name: str

    # Basic
    nickname: str
    level: int
    experience: int

    # Derived from PID
    nature_id: int
    nature_name: str
    gender: str           # "M", "F", "N"
    is_shiny: bool
    ability_slot: int     # 0 or 1

    # OT
    ot_name: str

    # Moves
    moves: list[MoveSlot]

    # IVs (read directly from save)
    ivs: IVSet

    # EVs (read directly from save)
    evs: EVSet

    # Stats (only available for party Pokémon, None for box)
    current_hp: Optional[int]
    max_hp: Optional[int]
    stat_attack: Optional[int]
    stat_defense: Optional[int]
    stat_speed: Optional[int]
    stat_sp_attack: Optional[int]
    stat_sp_defense: Optional[int]

    # Item
    item_id: int
    item_name: str

    # Flags
    is_egg: bool
    status_condition: int
    language: int
    markings: int

    # Position
    box_number: Optional[int] = None
    box_slot: Optional[int] = None
    party_slot: Optional[int] = None

    # Origin
    origin: PokemonOrigin = PokemonOrigin.UNKNOWN


@dataclass
class TrainerInfo:
    name: str
    trainer_id: int
    secret_id: int
    gender: str   # "M" or "F"


@dataclass
class ParsedSave:
    trainer: TrainerInfo
    party: list[ParsedPokemon]
    boxes: list[list[Optional[ParsedPokemon]]]  # 14 boxes x 30 slots
    game: str        # "firered"
    generation: int  # 3
    tms: list[str] = field(default_factory=list)


class SaveParseError(Exception):
    pass
