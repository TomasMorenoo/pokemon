import struct
from typing import Optional
from ...base.parser import BaseSaveParser
from ...base.types import ParsedSave, TrainerInfo, ParsedPokemon, SaveParseError
from ..encoding import decode_gen3_string
from .constants import (
    SAVE_SIZE, PARTY_COUNT_OFFSET, PARTY_DATA_OFFSET,
    PARTY_POKEMON_SIZE, BOX_POKEMON_SIZE,
    PC_BOX_DATA_OFFSET, PC_CURRENT_BOX_OFFSET,
    BOX_COUNT, BOX_CAPACITY,
    TRAINER_NAME_OFFSET, TRAINER_GENDER_OFFSET, TRAINER_ID_OFFSET,
    SECTION_TRAINER_INFO, SECTION_TEAM_ITEMS,
    BAG_TM_OFFSET, BAG_TM_COUNT,
)
from .save_sections import get_active_slot, get_section_data, build_pc_buffer
from .pokemon_struct import parse_pokemon


class FireRedParser(BaseSaveParser):
    GAME = "firered"
    GENERATION = 3

    def __init__(self, strict: bool = False, game: str = "firered"):
        if game not in {"firered", "leafgreen", "emerald", "ruby", "sapphire"}:
            raise SaveParseError("Juego no compatible.")
        self.strict = strict
        self.GAME = game
        self.party_count_offset = 0x34 if game in {"firered", "leafgreen"} else 0x234
        self.party_data_offset = self.party_count_offset + 4
        self.tm_offset = {"firered": 0x464, "leafgreen": 0x464, "emerald": 0x690, "ruby": 0x640, "sapphire": 0x640}[game]
        self.tm_count = 58 if game in {"firered", "leafgreen"} else 64
        self.key_offset = {"firered": 0xF20, "leafgreen": 0xF20, "emerald": 0xAC}.get(game)

    def can_parse(self, data: bytes) -> bool:
        return len(data) == SAVE_SIZE

    def parse(self, data: bytes) -> ParsedSave:
        if not self.can_parse(data):
            raise SaveParseError(
                f"Invalid save size: expected {SAVE_SIZE}, got {len(data)}"
            )

        sections = get_active_slot(data)

        trainer = self._parse_trainer(sections)
        party   = self._parse_party(sections, trainer)
        boxes   = self._parse_boxes(sections)
        tms     = self._parse_bag_tms(sections)

        return ParsedSave(
            trainer=trainer,
            party=party,
            boxes=boxes,
            game=self.GAME,
            generation=self.GENERATION,
            tms=tms,
        )

    def _parse_trainer(self, sections: dict) -> TrainerInfo:
        data = get_section_data(sections, SECTION_TRAINER_INFO)
        name   = decode_gen3_string(data[TRAINER_NAME_OFFSET:], 7)
        gender_byte = data[TRAINER_GENDER_OFFSET]
        gender = "F" if gender_byte == 1 else "M"
        id_raw    = struct.unpack_from("<I", data, TRAINER_ID_OFFSET)[0]
        trainer_id = id_raw & 0xFFFF
        secret_id  = (id_raw >> 16) & 0xFFFF
        return TrainerInfo(
            name=name,
            trainer_id=trainer_id,
            secret_id=secret_id,
            gender=gender,
        )

    def _parse_party(self, sections: dict, trainer: TrainerInfo) -> list[ParsedPokemon]:
        data = get_section_data(sections, SECTION_TEAM_ITEMS)
        count = struct.unpack_from("<I", data, self.party_count_offset)[0]
        if self.strict and count > 6:
            raise SaveParseError("La cantidad de Pokémon del equipo no es válida.")
        count = min(count, 6)
        party = []
        for i in range(count):
            offset = self.party_data_offset + i * PARTY_POKEMON_SIZE
            raw = data[offset : offset + PARTY_POKEMON_SIZE]
            pkm = parse_pokemon(raw, is_party=True, party_slot=i, strict=self.strict)
            if pkm is not None:
                party.append(pkm)
        return party

    def _parse_bag_tms(self, sections: dict) -> list[str]:
        import struct
        from ..constants import ITEM_NAMES
        data = get_section_data(sections, SECTION_TEAM_ITEMS)
        tms = []
        key = 0
        if self.key_offset is not None:
            trainer_data = get_section_data(sections, SECTION_TRAINER_INFO)
            key = struct.unpack_from("<I", trainer_data, self.key_offset)[0] & 0xFFFF
        for i in range(self.tm_count):
            offset = self.tm_offset + i * 4
            item_id = struct.unpack_from("<H", data, offset)[0]
            qty = struct.unpack_from("<H", data, offset + 2)[0] ^ key
            if item_id and qty:
                name = ITEM_NAMES.get(item_id, f"Item#{item_id}")
                tms.append(name)
        return tms

    def _parse_boxes(self, sections: dict) -> list[list[Optional[ParsedPokemon]]]:
        pc_buffer = build_pc_buffer(sections)
        boxes: list[list[Optional[ParsedPokemon]]] = []
        for box_num in range(BOX_COUNT):
            box: list[Optional[ParsedPokemon]] = []
            for slot in range(BOX_CAPACITY):
                offset = (
                    PC_BOX_DATA_OFFSET
                    + box_num * BOX_CAPACITY * BOX_POKEMON_SIZE
                    + slot * BOX_POKEMON_SIZE
                )
                raw = pc_buffer[offset : offset + BOX_POKEMON_SIZE]
                pkm = parse_pokemon(
                    raw,
                    is_party=False,
                    box_number=box_num,
                    box_slot=slot,
                    strict=self.strict,
                )
                box.append(pkm)
            boxes.append(box)
        return boxes
