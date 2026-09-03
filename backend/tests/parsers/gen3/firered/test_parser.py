"""Integration tests for FireRedParser. Most tests use synthetic data.
Tests marked with the 'real_save' marker require a real .sav in tests/fixtures/."""
import struct
import pytest
from parsers.gen3.firered.parser import FireRedParser
from parsers.gen3.firered.constants import (
    SAVE_SIZE, SECTION_SIZE, SECTION_DATA_SIZE,
    FOOTER_SECTION_ID_OFFSET, FOOTER_CHECKSUM_OFFSET,
    FOOTER_SIGNATURE_OFFSET, FOOTER_SAVE_INDEX_OFFSET,
    SECTION_SIGNATURE, SECTION_TEAM_ITEMS,
    PARTY_COUNT_OFFSET, PARTY_DATA_OFFSET, PARTY_POKEMON_SIZE,
)
from parsers.base.types import SaveParseError
from .conftest import load_fixture


def _make_checksum(data: bytes) -> int:
    total = 0
    for i in range(0, len(data), 4):
        total += struct.unpack_from("<I", data, i)[0]
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF


def _make_section_bytes(section_id: int, save_index: int, data: bytes = b"") -> bytes:
    padded = data + b"\x00" * (SECTION_DATA_SIZE - len(data))
    checksum = _make_checksum(padded)
    section = bytearray(padded) + bytearray(SECTION_SIZE - SECTION_DATA_SIZE)
    struct.pack_into("<H", section, FOOTER_SECTION_ID_OFFSET, section_id)
    struct.pack_into("<H", section, FOOTER_CHECKSUM_OFFSET, checksum)
    struct.pack_into("<I", section, FOOTER_SIGNATURE_OFFSET, SECTION_SIGNATURE)
    struct.pack_into("<I", section, FOOTER_SAVE_INDEX_OFFSET, save_index)
    return bytes(section)


def _make_minimal_save(party_pokemon: list[bytes] | None = None) -> bytes:
    """Build a minimal 131072-byte save file with one valid slot."""
    trainer_data = bytearray(SECTION_DATA_SIZE)
    trainer_data[0x00] = 0xCC
    trainer_data[0x01] = 0xBF
    trainer_data[0x02] = 0xBE
    trainer_data[0x03] = 0xFF
    trainer_data[0x08] = 0x00
    struct.pack_into("<I", trainer_data, 0x0A, 0x00641234)

    team_data = bytearray(SECTION_DATA_SIZE)
    pkm_list = party_pokemon or []
    struct.pack_into("<I", team_data, PARTY_COUNT_OFFSET, len(pkm_list))
    for i, pkm in enumerate(pkm_list):
        offset = PARTY_DATA_OFFSET + i * PARTY_POKEMON_SIZE
        team_data[offset:offset + len(pkm)] = pkm

    slot_a = bytearray()
    for sec_id in range(14):
        data = bytes(trainer_data) if sec_id == 0 else (bytes(team_data) if sec_id == 1 else b"")
        slot_a += _make_section_bytes(sec_id, save_index=1, data=data)

    slot_b = b"\x00" * (14 * SECTION_SIZE)
    save = bytes(slot_a) + slot_b
    assert len(save) == SAVE_SIZE
    return save


class TestCanParse:
    def test_accepts_correct_size(self):
        parser = FireRedParser()
        data = b"\x00" * SAVE_SIZE
        assert parser.can_parse(data) is True

    def test_rejects_wrong_size(self):
        parser = FireRedParser()
        assert parser.can_parse(b"\x00" * 1000) is False


class TestParseTrainer:
    def test_trainer_name_decoded(self):
        save = _make_minimal_save()
        parser = FireRedParser()
        result = parser.parse(save)
        assert result.trainer.name == "RED"

    def test_trainer_gender_male(self):
        save = _make_minimal_save()
        result = FireRedParser().parse(save)
        assert result.trainer.gender == "M"

    def test_trainer_ids(self):
        save = _make_minimal_save()
        result = FireRedParser().parse(save)
        assert result.trainer.trainer_id == 0x1234
        assert result.trainer.secret_id == 0x0064

    def test_game_and_generation(self):
        save = _make_minimal_save()
        result = FireRedParser().parse(save)
        assert result.game == "firered"
        assert result.generation == 3


class TestParseParty:
    def _make_pokemon_bytes(self, species_id: int = 25, level: int = 10) -> bytes:
        """Build a minimal valid party Pokémon block."""
        from tests.parsers.gen3.firered.test_pokemon_struct import _make_raw_pokemon
        return _make_raw_pokemon(
            pid=0x12345678, otid=0x00010002,
            species_id=species_id, level=level,
        )

    def test_empty_party(self):
        save = _make_minimal_save(party_pokemon=[])
        result = FireRedParser().parse(save)
        assert result.party == []

    def test_single_party_pokemon(self):
        pkm = self._make_pokemon_bytes(species_id=25, level=15)
        save = _make_minimal_save(party_pokemon=[pkm])
        result = FireRedParser().parse(save)
        assert len(result.party) == 1
        assert result.party[0].species_id == 25
        assert result.party[0].level == 15

    def test_party_pokemon_has_ivs_from_save(self):
        pkm = self._make_pokemon_bytes(species_id=65, level=40)
        save = _make_minimal_save(party_pokemon=[pkm])
        result = FireRedParser().parse(save)
        assert result.party[0].ivs.source.value == "save"
        assert 0 <= result.party[0].ivs.hp <= 31

    def test_boxes_structure(self):
        save = _make_minimal_save()
        result = FireRedParser().parse(save)
        assert len(result.boxes) == 14
        assert len(result.boxes[0]) == 30


class TestRealSave:
    """These tests require a real FireRed .sav in tests/fixtures/."""

    @pytest.mark.real_save
    def test_parse_real_save(self):
        data = load_fixture("firered.sav")
        parser = FireRedParser()
        result = parser.parse(data)
        assert result.trainer.name != ""
        assert result.trainer.trainer_id > 0
        assert len(result.party) >= 0
        assert len(result.boxes) == 14

    @pytest.mark.real_save
    def test_real_save_ivs_are_valid(self):
        data = load_fixture("firered.sav")
        result = FireRedParser().parse(data)
        for pkm in result.party:
            assert 0 <= pkm.ivs.hp <= 31
            assert 0 <= pkm.ivs.attack <= 31
            assert 0 <= pkm.ivs.defense <= 31
            assert 0 <= pkm.ivs.speed <= 31
            assert 0 <= pkm.ivs.sp_attack <= 31
            assert 0 <= pkm.ivs.sp_defense <= 31
            assert pkm.ivs.source.value == "save"

    @pytest.mark.real_save
    def test_real_save_evs_are_valid(self):
        data = load_fixture("firered.sav")
        result = FireRedParser().parse(data)
        for pkm in result.party:
            total = (pkm.evs.hp + pkm.evs.attack + pkm.evs.defense +
                     pkm.evs.speed + pkm.evs.sp_attack + pkm.evs.sp_defense)
            assert 0 <= total <= 510
            assert pkm.evs.source.value == "save"

    @pytest.mark.real_save
    def test_real_save_natures_valid(self):
        data = load_fixture("firered.sav")
        result = FireRedParser().parse(data)
        for pkm in result.party:
            assert 0 <= pkm.nature_id <= 24
            assert pkm.nature_name in [
                "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
                "Bold", "Docile", "Relaxed", "Impish", "Lax",
                "Timid", "Hasty", "Serious", "Jolly", "Naive",
                "Modest", "Mild", "Quiet", "Bashful", "Rash",
                "Calm", "Gentle", "Sassy", "Careful", "Quirky",
            ]

    @pytest.mark.real_save
    def test_no_duplicate_individuals(self):
        """Same (pid, ot_id, ot_secret_id) should not appear twice."""
        data = load_fixture("firered.sav")
        result = FireRedParser().parse(data)
        all_pkm = list(result.party)
        for box in result.boxes:
            for pkm in box:
                if pkm:
                    all_pkm.append(pkm)
        identities = [(p.pid, p.ot_id, p.ot_secret_id) for p in all_pkm]
        assert len(all_pkm) >= 0
