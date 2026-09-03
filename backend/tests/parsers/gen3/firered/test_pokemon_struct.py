"""Tests for Pokémon struct parsing and decryption logic (no .sav file needed)."""
import struct
import pytest
from parsers.gen3.firered.pokemon_struct import (
    _decrypt_substructures,
    _get_substructure,
    _gender_from_pid,
    _is_shiny,
    _verify_checksum,
)
from parsers.gen3.firered.constants import PKM_ENCRYPTED_OFFSET
from parsers.gen3.constants import SUBSTRUCTURE_ORDER


def _make_raw_pokemon(
    pid: int = 0x1234ABCD,
    otid: int = 0x00050006,
    species_id: int = 25,
    level: int = 10,
    exp: int = 1000,
    iv_word: int = 0b00_11111_11111_11111_11111_11111_11111,
    hp_ev: int = 0, atk_ev: int = 0, def_ev: int = 0,
    spe_ev: int = 0, spa_ev: int = 0, spd_ev: int = 0,
    move1: int = 84, move2: int = 85, move3: int = 0, move4: int = 0,
    pp1: int = 30, pp2: int = 15, pp3: int = 0, pp4: int = 0,
) -> bytes:
    """Build a synthetic 100-byte party Pokémon block with correct checksum."""
    key = pid ^ otid

    order = SUBSTRUCTURE_ORDER[pid % 24]

    substructs: dict[str, bytearray] = {
        "G": bytearray(12),
        "A": bytearray(12),
        "E": bytearray(12),
        "M": bytearray(12),
    }

    g = substructs["G"]
    struct.pack_into("<H", g, 0, species_id)
    struct.pack_into("<H", g, 2, 0)
    struct.pack_into("<I", g, 4, exp)

    a = substructs["A"]
    struct.pack_into("<H", a, 0, move1)
    struct.pack_into("<H", a, 2, move2)
    struct.pack_into("<H", a, 4, move3)
    struct.pack_into("<H", a, 6, move4)
    a[8] = pp1; a[9] = pp2; a[10] = pp3; a[11] = pp4

    e = substructs["E"]
    e[0] = hp_ev; e[1] = atk_ev; e[2] = def_ev
    e[3] = spe_ev; e[4] = spa_ev; e[5] = spd_ev

    m = substructs["M"]
    struct.pack_into("<I", m, 0, iv_word)

    decrypted = bytearray(48)
    for i, letter in enumerate(order):
        decrypted[i*12:(i+1)*12] = substructs[letter]

    total = 0
    for i in range(0, 48, 2):
        total += struct.unpack_from("<H", decrypted, i)[0]
    checksum = total & 0xFFFF

    encrypted = bytearray(48)
    for i in range(12):
        word = struct.unpack_from("<I", decrypted, i*4)[0]
        struct.pack_into("<I", encrypted, i*4, word ^ key)

    raw = bytearray(100)
    struct.pack_into("<I", raw, 0, pid)
    struct.pack_into("<I", raw, 4, otid)
    struct.pack_into("<H", raw, 0x1C, checksum)
    raw[0x20:0x50] = encrypted

    raw[0x54] = level
    struct.pack_into("<H", raw, 0x56, level * 10)
    struct.pack_into("<H", raw, 0x58, level * 10)

    return bytes(raw)


class TestDecryptSubstructures:
    def test_decrypt_then_re_encrypt_roundtrip(self):
        pid = 0xABCD1234
        otid = 0x00010002
        raw = _make_raw_pokemon(pid=pid, otid=otid, species_id=1, exp=500)
        key = pid ^ otid
        decrypted = _decrypt_substructures(raw, pid, otid)
        for i in range(12):
            word = struct.unpack_from("<I", decrypted, i*4)[0]
            assert struct.unpack_from("<I", raw, PKM_ENCRYPTED_OFFSET + i*4)[0] == word ^ key

    def test_all_zero_key_is_identity(self):
        """When pid == otid, key = 0, encrypted == decrypted."""
        pid = otid = 0x12345678
        raw = bytearray(80)
        struct.pack_into("<I", raw, 0, pid)
        struct.pack_into("<I", raw, 4, otid)
        raw[0x20] = 0xAA
        raw[0x21] = 0xBB
        decrypted = _decrypt_substructures(bytes(raw), pid, otid)
        assert decrypted[0] == 0xAA
        assert decrypted[1] == 0xBB


class TestGetSubstructure:
    def test_returns_12_bytes(self):
        pid = 0x12345678
        otid = 0
        raw = _make_raw_pokemon(pid=pid, otid=otid, species_id=25)
        from parsers.gen3.firered.pokemon_struct import _decrypt_substructures
        decrypted = _decrypt_substructures(raw, pid, otid)
        for letter in "GAEM":
            sub = _get_substructure(decrypted, pid, letter)
            assert len(sub) == 12

    def test_growth_contains_species_id(self):
        pid = 0xDEADBEEF
        otid = 0x00010001
        raw = _make_raw_pokemon(pid=pid, otid=otid, species_id=65)
        from parsers.gen3.firered.pokemon_struct import _decrypt_substructures
        decrypted = _decrypt_substructures(raw, pid, otid)
        g = _get_substructure(decrypted, pid, "G")
        species = struct.unpack_from("<H", g, 0)[0]
        assert species == 65


class TestGenderFromPid:
    def test_magikarp_male_female(self):
        assert _gender_from_pid(0x0000007F, 129) == "M"
        assert _gender_from_pid(0x0000007E, 129) == "F"

    def test_voltorb_genderless(self):
        assert _gender_from_pid(0xABCDEF01, 100) == "N"

    def test_tauros_always_male(self):
        assert _gender_from_pid(0xABCDEF01, 128) == "M"

    def test_jynx_always_female(self):
        assert _gender_from_pid(0xABCDEF01, 124) == "F"


class TestIsShiny:
    def test_shiny_detection(self):
        trainer_id = 12345
        secret_id = 54321
        pid_high = 0
        pid_low = trainer_id ^ secret_id ^ 0
        pid = (pid_high << 16) | pid_low
        assert _is_shiny(pid, trainer_id, secret_id) is True

    def test_non_shiny(self):
        assert _is_shiny(0x00000000, 0, 0xFFFF) is False


class TestVerifyChecksum:
    def test_valid_checksum_passes(self):
        raw = _make_raw_pokemon(pid=0x12345678, otid=0x00010002, species_id=1)
        assert _verify_checksum(raw, 0x12345678, 0x00010002) is True

    def test_corrupt_checksum_fails(self):
        raw = bytearray(_make_raw_pokemon(pid=0x12345678, otid=0x00010002, species_id=1))
        raw[0x1C] ^= 0xFF
        assert _verify_checksum(bytes(raw), 0x12345678, 0x00010002) is False


class TestParsePokemon:
    def test_parse_party_pokemon(self):
        from parsers.gen3.firered.pokemon_struct import parse_pokemon
        raw = _make_raw_pokemon(
            pid=0x12345678,
            otid=0x00010002,
            species_id=65,
            level=40,
            exp=125000,
            move1=94,
            pp1=10,
        )
        pkm = parse_pokemon(raw, is_party=True, party_slot=0)
        assert pkm is not None
        assert pkm.species_id == 65
        assert pkm.species_name == "Alakazam"
        assert pkm.level == 40
        assert pkm.experience == 125000
        assert pkm.ot_id == 1
        assert pkm.ot_secret_id == 2
        assert pkm.ivs.hp == 31
        assert pkm.ivs.source.value == "save"
        assert pkm.evs.hp == 0
        assert pkm.evs.source.value == "save"
        assert len(pkm.moves) >= 1
        assert pkm.moves[0].move_id == 94

    def test_empty_slot_returns_none(self):
        from parsers.gen3.firered.pokemon_struct import parse_pokemon
        raw = b"\x00" * 80
        result = parse_pokemon(raw, is_party=False)
        assert result is None

    def test_nature_from_pid(self):
        from parsers.gen3.firered.pokemon_struct import parse_pokemon
        pid = 0x00000006
        raw = _make_raw_pokemon(pid=pid, otid=0x00010002, species_id=25)
        pkm = parse_pokemon(raw, is_party=True, party_slot=0)
        assert pkm is not None
        assert pkm.nature_id == 6
        assert pkm.nature_name == "Docile"

    def test_box_pokemon_has_no_stats(self):
        from parsers.gen3.firered.pokemon_struct import parse_pokemon
        raw = _make_raw_pokemon(pid=0x12345678, otid=0x00010002, species_id=25)
        pkm = parse_pokemon(raw[:80], is_party=False, box_number=0, box_slot=5)
        assert pkm is not None
        assert pkm.current_hp is None
        assert pkm.stat_attack is None
        assert pkm.box_number == 0
        assert pkm.box_slot == 5
