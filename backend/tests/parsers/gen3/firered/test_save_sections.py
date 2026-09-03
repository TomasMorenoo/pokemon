"""Tests for save section parsing (no real .sav needed for most tests)."""
import struct
import pytest
from parsers.gen3.firered.save_sections import (
    parse_section_footer,
    validate_section,
    extract_slot_sections,
    build_pc_buffer,
    get_active_slot,
)
from parsers.gen3.firered.constants import (
    SECTION_SIZE, SECTION_DATA_SIZE, SECTION_SIGNATURE,
    FOOTER_SECTION_ID_OFFSET, FOOTER_CHECKSUM_OFFSET,
    FOOTER_SIGNATURE_OFFSET, FOOTER_SAVE_INDEX_OFFSET,
)
from parsers.base.types import SaveParseError


def _make_section(section_id: int, save_index: int = 1, data: bytes = b"", corrupt_checksum: bool = False) -> bytes:
    """Build a valid 4096-byte section with correct checksum."""
    padded = data + b"\x00" * (SECTION_DATA_SIZE - len(data))

    total = 0
    for i in range(0, SECTION_DATA_SIZE, 4):
        total += struct.unpack_from("<I", padded, i)[0]
    checksum = ((total >> 16) + (total & 0xFFFF)) & 0xFFFF
    if corrupt_checksum:
        checksum = checksum ^ 0xDEAD

    section = bytearray(padded)
    section += b"\x00" * (SECTION_SIZE - SECTION_DATA_SIZE)

    struct.pack_into("<H", section, FOOTER_SECTION_ID_OFFSET, section_id)
    struct.pack_into("<H", section, FOOTER_CHECKSUM_OFFSET, checksum)
    struct.pack_into("<I", section, FOOTER_SIGNATURE_OFFSET, SECTION_SIGNATURE)
    struct.pack_into("<I", section, FOOTER_SAVE_INDEX_OFFSET, save_index)

    return bytes(section)


def _make_valid_slot(save_index: int = 1) -> bytes:
    """Build a valid 14-section save slot."""
    sections = [_make_section(i, save_index) for i in range(14)]
    return b"".join(sections)


class TestParseSectionFooter:
    def test_reads_section_id(self):
        section = _make_section(section_id=7, save_index=5)
        footer = parse_section_footer(section)
        assert footer["section_id"] == 7

    def test_reads_save_index(self):
        section = _make_section(section_id=0, save_index=42)
        footer = parse_section_footer(section)
        assert footer["save_index"] == 42

    def test_reads_signature(self):
        section = _make_section(section_id=0, save_index=1)
        footer = parse_section_footer(section)
        assert footer["signature"] == SECTION_SIGNATURE


class TestValidateSection:
    def test_valid_section_passes(self):
        section = _make_section(section_id=0, save_index=1)
        assert validate_section(section) is True

    def test_wrong_signature_fails(self):
        section = bytearray(_make_section(section_id=0))
        struct.pack_into("<I", section, FOOTER_SIGNATURE_OFFSET, 0xDEADBEEF)
        assert validate_section(bytes(section)) is False

    def test_corrupt_checksum_fails(self):
        section = _make_section(section_id=0, corrupt_checksum=True)
        assert validate_section(section) is False

    def test_section_with_data_validates(self):
        data = b"\x01\x02\x03\x04" * 100
        section = _make_section(section_id=1, data=data)
        assert validate_section(section) is True


class TestExtractSlotSections:
    def test_extracts_all_14_sections(self):
        slot = _make_valid_slot(save_index=1)
        sections = extract_slot_sections(slot, 0)
        assert len(sections) == 14
        assert set(sections.keys()) == set(range(14))

    def test_sections_keyed_by_id(self):
        slot = _make_valid_slot(save_index=1)
        sections = extract_slot_sections(slot, 0)
        for expected_id in range(14):
            assert expected_id in sections

    def test_empty_slot_raises(self):
        empty = b"\x00" * (14 * SECTION_SIZE)
        with pytest.raises(SaveParseError):
            extract_slot_sections(empty, 0)

    def test_shuffled_section_order(self):
        """Sections within a slot can appear in any order."""
        sections_list = [_make_section(i, save_index=1) for i in range(14)]
        shuffled = b"".join(reversed(sections_list))
        sections = extract_slot_sections(shuffled, 0)
        assert set(sections.keys()) == set(range(14))


class TestGetActiveSlot:
    def test_selects_higher_save_index(self):
        slot_a = _make_valid_slot(save_index=10)
        slot_b = _make_valid_slot(save_index=20)
        save_data = slot_a + slot_b
        sections = get_active_slot(save_data)
        footer = parse_section_footer(sections[0])
        assert footer["save_index"] == 20

    def test_falls_back_to_slot_a_if_b_invalid(self):
        slot_a = _make_valid_slot(save_index=5)
        slot_b = b"\x00" * (14 * SECTION_SIZE)
        save_data = slot_a + slot_b
        sections = get_active_slot(save_data)
        footer = parse_section_footer(sections[0])
        assert footer["save_index"] == 5

    def test_raises_if_both_slots_invalid(self):
        save_data = b"\x00" * (2 * 14 * SECTION_SIZE)
        with pytest.raises(SaveParseError):
            get_active_slot(save_data)


class TestBuildPcBuffer:
    def test_pc_buffer_length(self):
        sections = {i: _make_section(i) for i in range(14)}
        buf = build_pc_buffer(sections)
        assert len(buf) == 9 * SECTION_DATA_SIZE

    def test_missing_pc_section_raises(self):
        sections = {i: _make_section(i) for i in range(14)}
        del sections[7]
        with pytest.raises(SaveParseError):
            build_pc_buffer(sections)
