import struct
from typing import Optional
from ..constants import (
    NATURES, SUBSTRUCTURE_ORDER, SPECIES_NAMES,
    MOVE_NAMES, ITEM_NAMES, GENDER_RATIOS,
    SPECIES_GROWTH_RATE, level_from_exp,
    BASE_STATS, NATURE_STAT_MODS,
)
from ..encoding import decode_gen3_string
from ..firered.constants import (
    PKM_PID_OFFSET, PKM_OTID_OFFSET, PKM_NICKNAME_OFFSET,
    PKM_LANGUAGE_OFFSET, PKM_OT_NAME_OFFSET, PKM_MARKINGS_OFFSET,
    PKM_CHECKSUM_OFFSET, PKM_ENCRYPTED_OFFSET,
    PKM_STATUS_OFFSET, PKM_LEVEL_OFFSET, PKM_POKERUS_OFFSET,
    PKM_CURRENT_HP_OFFSET, PKM_MAX_HP_OFFSET,
    PKM_STAT_ATK_OFFSET, PKM_STAT_DEF_OFFSET, PKM_STAT_SPE_OFFSET,
    PKM_STAT_SPA_OFFSET, PKM_STAT_SPD_OFFSET,
    PARTY_POKEMON_SIZE, BOX_POKEMON_SIZE,
)
from ...base.types import (
    ParsedPokemon, IVSet, EVSet, MoveSlot, DataSource, PokemonOrigin
)


def _decrypt_substructures(raw: bytes, pid: int, otid: int) -> bytes:
    """XOR-decrypt the 48-byte encrypted data block using key = pid ^ otid."""
    key = pid ^ otid
    decrypted = bytearray(48)
    for i in range(12):
        offset = i * 4
        word = struct.unpack_from("<I", raw, PKM_ENCRYPTED_OFFSET + offset)[0]
        struct.pack_into("<I", decrypted, offset, word ^ key)
    return bytes(decrypted)


def _get_substructure(decrypted: bytes, pid: int, letter: str) -> bytes:
    """Return the 12-byte substructure for the given letter (G/A/E/M)."""
    order = SUBSTRUCTURE_ORDER[pid % 24]
    idx = order.index(letter)
    return decrypted[idx * 12 : idx * 12 + 12]


def _compute_checksum(raw: bytes) -> int:
    total = 0
    for i in range(12):
        offset = PKM_ENCRYPTED_OFFSET + i * 4
        # checksum is computed on the UNENCRYPTED data — but in the save the
        # checksum field exists before decryption. We verify against encrypted words
        # XORed with key. Actually: checksum is sum of decrypted u16 words.
        pass
    # Recompute: sum of all u16 words in the decrypted 48-byte block
    # This is done after decryption
    return total


def _verify_checksum(raw: bytes, pid: int, otid: int) -> bool:
    """Verify Pokémon data checksum (sum of u16 words in decrypted data == stored checksum)."""
    stored = struct.unpack_from("<H", raw, PKM_CHECKSUM_OFFSET)[0]
    decrypted = _decrypt_substructures(raw, pid, otid)
    total = 0
    for i in range(0, 48, 2):
        total += struct.unpack_from("<H", decrypted, i)[0]
    computed = total & 0xFFFF
    return computed == stored


def _gender_from_pid(pid: int, species_id: int) -> str:
    ratio = GENDER_RATIOS.get(species_id, 127)
    if ratio == 0:
        return "M"
    if ratio == 254:
        return "F"
    if ratio == 255:
        return "N"
    return "F" if (pid & 0xFF) < ratio else "M"


def _is_shiny(pid: int, trainer_id: int, secret_id: int) -> bool:
    xor = trainer_id ^ secret_id ^ (pid >> 16) ^ (pid & 0xFFFF)
    return xor < 8


def _calc_stats(species_id: int, level: int, ivs, evs, nature_id: int):
    base = BASE_STATS.get(species_id)
    if not base:
        return None, None, None, None, None, None
    b_hp, b_atk, b_def, b_spa, b_spd, b_spe = base
    boost, red = NATURE_STAT_MODS[nature_id]

    def mod(idx: int) -> int:
        if boost == idx: return 110
        if red == idx:   return 90
        return 100

    def stat(b: int, iv: int, ev: int, idx: int, is_hp: bool = False) -> int:
        inner = (2 * b + iv + ev // 4) * level // 100
        return inner + level + 10 if is_hp else (inner + 5) * mod(idx) // 100

    return (
        stat(b_hp,  ivs.hp,        evs.hp,        -1, True),
        stat(b_atk, ivs.attack,    evs.attack,    0),
        stat(b_def, ivs.defense,   evs.defense,   1),
        stat(b_spa, ivs.sp_attack, evs.sp_attack, 2),
        stat(b_spd, ivs.sp_defense,evs.sp_defense,3),
        stat(b_spe, ivs.speed,     evs.speed,     4),
    )


def parse_pokemon(raw: bytes, is_party: bool = False,
                  party_slot: Optional[int] = None,
                  box_number: Optional[int] = None,
                  box_slot: Optional[int] = None) -> Optional[ParsedPokemon]:
    """
    Parse a raw Pokémon byte block.
    raw must be BOX_POKEMON_SIZE (80) or PARTY_POKEMON_SIZE (100) bytes.
    Returns None if the slot is empty (species_id == 0 or is_egg).
    """
    if len(raw) < BOX_POKEMON_SIZE:
        return None

    pid  = struct.unpack_from("<I", raw, PKM_PID_OFFSET)[0]
    otid_raw = struct.unpack_from("<I", raw, PKM_OTID_OFFSET)[0]
    ot_id     = otid_raw & 0xFFFF
    secret_id = (otid_raw >> 16) & 0xFFFF

    # Empty slot check
    if pid == 0 and ot_id == 0:
        return None

    nickname = decode_gen3_string(raw[PKM_NICKNAME_OFFSET:], 10)
    language = struct.unpack_from("<H", raw, PKM_LANGUAGE_OFFSET)[0]
    ot_name  = decode_gen3_string(raw[PKM_OT_NAME_OFFSET:], 7)
    markings = raw[PKM_MARKINGS_OFFSET]

    if not _verify_checksum(raw, pid, otid_raw):
        # Bad egg or corrupted data — skip
        return None

    decrypted = _decrypt_substructures(raw, pid, otid_raw)

    # -- Growth substructure --
    g = _get_substructure(decrypted, pid, "G")
    species_id = struct.unpack_from("<H", g, 0)[0]
    item_id    = struct.unpack_from("<H", g, 2)[0]
    experience = struct.unpack_from("<I", g, 4)[0]

    if species_id == 0:
        return None

    # -- Attacks substructure --
    a = _get_substructure(decrypted, pid, "A")
    move_ids = [
        struct.unpack_from("<H", a, 0)[0],
        struct.unpack_from("<H", a, 2)[0],
        struct.unpack_from("<H", a, 4)[0],
        struct.unpack_from("<H", a, 6)[0],
    ]
    move_pps = [a[8], a[9], a[10], a[11]]
    # PP max from base PP (we store current PP from save; pp_max requires move data)
    moves = [
        MoveSlot(
            move_id=move_ids[i],
            move_name=MOVE_NAMES.get(move_ids[i], f"Move#{move_ids[i]}"),
            pp=move_pps[i],
            pp_max=move_pps[i],  # pp_max = same as current unless PP ups applied
        )
        for i in range(4) if move_ids[i] != 0
    ]

    # -- Effort substructure --
    e = _get_substructure(decrypted, pid, "E")
    evs = EVSet(
        hp=e[0], attack=e[1], defense=e[2],
        speed=e[3], sp_attack=e[4], sp_defense=e[5],
        source=DataSource.SAVE,
    )

    # -- Misc substructure --
    m = _get_substructure(decrypted, pid, "M")
    iv_word = struct.unpack_from("<I", m, 4)[0]
    ivs = IVSet(
        hp       = (iv_word >> 0)  & 0x1F,
        attack   = (iv_word >> 5)  & 0x1F,
        defense  = (iv_word >> 10) & 0x1F,
        speed    = (iv_word >> 15) & 0x1F,
        sp_attack= (iv_word >> 20) & 0x1F,
        sp_defense=(iv_word >> 25) & 0x1F,
        source=DataSource.SAVE,
    )
    is_egg    = bool((iv_word >> 30) & 1)
    ability_slot = int((iv_word >> 31) & 1)

    if is_egg:
        return None

    nature_id   = pid % 25
    nature_name = NATURES[nature_id]
    gender      = _gender_from_pid(pid, species_id)
    shiny       = _is_shiny(pid, ot_id, secret_id)

    # Party-only stats
    level = current_hp = max_hp = None
    stat_attack = stat_defense = stat_speed = stat_sp_attack = stat_sp_defense = None
    status_condition = 0

    if is_party and len(raw) >= PARTY_POKEMON_SIZE:
        status_condition = struct.unpack_from("<I", raw, PKM_STATUS_OFFSET)[0]
        level        = raw[PKM_LEVEL_OFFSET]
        current_hp   = struct.unpack_from("<H", raw, PKM_CURRENT_HP_OFFSET)[0]
        max_hp       = struct.unpack_from("<H", raw, PKM_MAX_HP_OFFSET)[0]
        stat_attack  = struct.unpack_from("<H", raw, PKM_STAT_ATK_OFFSET)[0]
        stat_defense = struct.unpack_from("<H", raw, PKM_STAT_DEF_OFFSET)[0]
        stat_speed   = struct.unpack_from("<H", raw, PKM_STAT_SPE_OFFSET)[0]
        stat_sp_attack  = struct.unpack_from("<H", raw, PKM_STAT_SPA_OFFSET)[0]
        stat_sp_defense = struct.unpack_from("<H", raw, PKM_STAT_SPD_OFFSET)[0]

    if level is None:
        growth_rate = SPECIES_GROWTH_RATE.get(species_id, 0)
        level = level_from_exp(experience, growth_rate)

    if not is_party:
        max_hp, stat_attack, stat_defense, stat_sp_attack, stat_sp_defense, stat_speed = \
            _calc_stats(species_id, level, ivs, evs, nature_id)

    return ParsedPokemon(
        pid=pid,
        ot_id=ot_id,
        ot_secret_id=secret_id,
        species_id=species_id,
        species_name=SPECIES_NAMES.get(species_id, f"Species#{species_id}"),
        nickname=nickname,
        level=level,
        experience=experience,
        nature_id=nature_id,
        nature_name=nature_name,
        gender=gender,
        is_shiny=shiny,
        ability_slot=ability_slot,
        ot_name=ot_name,
        moves=moves,
        ivs=ivs,
        evs=evs,
        current_hp=current_hp,
        max_hp=max_hp,
        stat_attack=stat_attack,
        stat_defense=stat_defense,
        stat_speed=stat_speed,
        stat_sp_attack=stat_sp_attack,
        stat_sp_defense=stat_sp_defense,
        item_id=item_id,
        item_name=ITEM_NAMES.get(item_id, f"Item#{item_id}"),
        is_egg=False,
        status_condition=status_condition,
        language=language,
        markings=markings,
        party_slot=party_slot,
        box_number=box_number,
        box_slot=box_slot,
    )
