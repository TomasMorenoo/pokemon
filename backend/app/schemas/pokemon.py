from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class IVSetSchema(BaseModel):
    hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    source: str  # save/calculated/manual/unknown


class EVSetSchema(BaseModel):
    hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    source: str


class MoveSlotSchema(BaseModel):
    move_id: int
    move_name: str
    pp: int
    pp_max: int


class MeasurementOut(BaseModel):
    id: int
    level: Optional[int]
    experience: Optional[int]
    nickname: Optional[str]
    hp: Optional[int]
    attack: Optional[int]
    defense: Optional[int]
    speed: Optional[int]
    sp_attack: Optional[int]
    sp_defense: Optional[int]
    ivs: Optional[IVSetSchema]
    evs: Optional[EVSetSchema]
    moves: Optional[list[MoveSlotSchema]]
    item_name: Optional[str]
    data_source: str
    recorded_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_db(cls, m) -> "MeasurementOut":
        ivs = None
        if m.iv_hp is not None:
            ivs = IVSetSchema(
                hp=m.iv_hp, attack=m.iv_attack, defense=m.iv_defense,
                speed=m.iv_speed, sp_attack=m.iv_sp_attack, sp_defense=m.iv_sp_defense,
                source=m.iv_source,
            )
        evs = None
        if m.ev_hp is not None:
            evs = EVSetSchema(
                hp=m.ev_hp, attack=m.ev_attack, defense=m.ev_defense,
                speed=m.ev_speed, sp_attack=m.ev_sp_attack, sp_defense=m.ev_sp_defense,
                source=m.ev_source,
            )
        moves = None
        if m.moves:
            moves = [MoveSlotSchema(**mv) for mv in m.moves]
        return cls(
            id=m.id,
            level=m.level,
            experience=m.experience,
            nickname=m.nickname,
            hp=m.hp,
            attack=m.attack,
            defense=m.defense,
            speed=m.speed,
            sp_attack=m.sp_attack,
            sp_defense=m.sp_defense,
            ivs=ivs,
            evs=evs,
            moves=moves,
            item_name=m.item_name,
            data_source=m.data_source,
            recorded_at=m.recorded_at,
        )


class PokemonOut(BaseModel):
    id: int
    species_id: int
    species_name: str
    nickname: Optional[str]
    current_level: Optional[int]
    nature_name: Optional[str]
    gender: Optional[str]
    is_shiny: bool
    ot_name: Optional[str]
    ot_id: int
    origin: str
    game: Optional[str] = None
    form_name: Optional[str] = None
    added_via: str
    party_slot: Optional[int] = None
    first_seen_at: datetime
    latest_measurement: Optional[MeasurementOut] = None
    measurements: list[MeasurementOut] = []

    model_config = {"from_attributes": True}


class ManualPokemonIn(BaseModel):
    species_id: int
    species_name: str
    nickname: Optional[str] = None
    level: int
    nature_name: Optional[str] = None
    gender: Optional[str] = None
    is_shiny: bool = False
    origin: str = "unknown"
    game: Optional[str] = None
    form_name: Optional[str] = None
    # Stats
    hp: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    speed: Optional[int] = None
    sp_attack: Optional[int] = None
    sp_defense: Optional[int] = None
    # IVs (optional)
    iv_hp: Optional[int] = None
    iv_attack: Optional[int] = None
    iv_defense: Optional[int] = None
    iv_speed: Optional[int] = None
    iv_sp_attack: Optional[int] = None
    iv_sp_defense: Optional[int] = None
    # EVs (optional)
    ev_hp: Optional[int] = None
    ev_attack: Optional[int] = None
    ev_defense: Optional[int] = None
    ev_speed: Optional[int] = None
    ev_sp_attack: Optional[int] = None
    ev_sp_defense: Optional[int] = None
    # Moves
    moves: Optional[list[MoveSlotSchema]] = None
    # Item
    item_name: Optional[str] = None
