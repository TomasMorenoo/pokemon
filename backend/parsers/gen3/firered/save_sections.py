import struct
from ..firered.constants import (
    SECTION_SIZE, SECTION_DATA_SIZE, SLOT_SIZE,
    FOOTER_SECTION_ID_OFFSET, FOOTER_CHECKSUM_OFFSET,
    FOOTER_SIGNATURE_OFFSET, FOOTER_SAVE_INDEX_OFFSET,
    SECTION_SIGNATURE, SLOT_A_OFFSET, SLOT_B_OFFSET,
)
from ...base.types import SaveParseError


def _compute_checksum(data: bytes) -> int:
    """Sum all u32 words in data, fold upper 16 bits into lower 16."""
    total = 0
    for i in range(0, len(data), 4):
        total += struct.unpack_from("<I", data, i)[0]
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF


def parse_section_footer(section: bytes) -> dict:
    """Extract section ID, checksum, signature, save_index from a 4096-byte section."""
    section_id  = struct.unpack_from("<H", section, FOOTER_SECTION_ID_OFFSET)[0]
    checksum    = struct.unpack_from("<H", section, FOOTER_CHECKSUM_OFFSET)[0]
    signature   = struct.unpack_from("<I", section, FOOTER_SIGNATURE_OFFSET)[0]
    save_index  = struct.unpack_from("<I", section, FOOTER_SAVE_INDEX_OFFSET)[0]
    return {
        "section_id": section_id,
        "checksum": checksum,
        "signature": signature,
        "save_index": save_index,
    }


def validate_section(section: bytes) -> bool:
    """Return True if the section has a valid signature and checksum."""
    footer = parse_section_footer(section)
    if footer["signature"] != SECTION_SIGNATURE:
        return False
    data = section[:SECTION_DATA_SIZE]
    expected = _compute_checksum(data)
    return footer["checksum"] == expected


def extract_slot_sections(save_data: bytes, slot_offset: int) -> dict[int, bytes]:
    """
    Extract all 14 sections from a save slot.
    Returns dict mapping section_id → full 4096-byte section bytes.
    Raises SaveParseError if slot is invalid.
    """
    sections: dict[int, bytes] = {}
    for i in range(14):
        start = slot_offset + i * SECTION_SIZE
        section = save_data[start : start + SECTION_SIZE]
        if not validate_section(section):
            continue  # Skip invalid sections (e.g. blank slot)
        footer = parse_section_footer(section)
        sections[footer["section_id"]] = section
    if not sections:
        raise SaveParseError("No valid sections found in slot")
    return sections


def get_active_slot(save_data: bytes) -> dict[int, bytes]:
    """
    Compare the two save slots and return the one with the higher save_index
    (i.e. the most recent save). Falls back to slot A if slot B is invalid.
    """
    try:
        slot_a = extract_slot_sections(save_data, SLOT_A_OFFSET)
    except SaveParseError:
        slot_a = {}

    try:
        slot_b = extract_slot_sections(save_data, SLOT_B_OFFSET)
    except SaveParseError:
        slot_b = {}

    if not slot_a and not slot_b:
        raise SaveParseError("No valid save slots found in file")
    if not slot_a:
        return slot_b
    if not slot_b:
        return slot_a

    # Compare save indices from section 0 of each slot
    idx_a = parse_section_footer(slot_a[0])["save_index"]
    idx_b = parse_section_footer(slot_b[0])["save_index"]
    return slot_b if idx_b > idx_a else slot_a


def get_section_data(sections: dict[int, bytes], section_id: int) -> bytes:
    """Return the data portion (first 3968 bytes) of a section."""
    if section_id not in sections:
        raise SaveParseError(f"Section {section_id} not found in save")
    return sections[section_id][:SECTION_DATA_SIZE]


def build_pc_buffer(sections: dict[int, bytes]) -> bytes:
    """
    Concatenate data portions of sections 5-13 to reconstruct the PC buffer.
    """
    buffer = b""
    for section_id in range(5, 14):
        if section_id not in sections:
            raise SaveParseError(f"PC section {section_id} missing from save")
        buffer += sections[section_id][:SECTION_DATA_SIZE]
    return buffer
