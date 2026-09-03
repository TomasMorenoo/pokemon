import os
import struct
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.models.pokemon import PokemonInstance
from app.services.sync_service import SyncService
from parsers.base.types import SaveParseError
from parsers.gen3.firered.constants import PARTY_COUNT_OFFSET, PARTY_DATA_OFFSET, SAVE_SIZE, SECTION_DATA_SIZE
from parsers.gen3.firered.parser import FireRedParser
from tests.parsers.gen3.firered.test_parser import _make_section_bytes
from tests.parsers.gen3.firered.test_pokemon_struct import _make_raw_pokemon


def make_save(party=(), boxed=(), game="firered", tm=False):
    team = bytearray(SECTION_DATA_SIZE)
    count_offset = 0x34 if game in {"firered", "leafgreen"} else 0x234
    data_offset = count_offset + 4
    if tm:
        offset = {"firered": 0x464, "leafgreen": 0x464, "emerald": 0x690, "ruby": 0x640, "sapphire": 0x640}[game]
        struct.pack_into("<HH", team, offset, 289, 1)
    struct.pack_into('<I', team, count_offset, len(party))
    for i, raw in enumerate(party):
        start = data_offset + i * 100
        team[start:start + 100] = raw
    pc = bytearray(9 * SECTION_DATA_SIZE)
    for i, raw in enumerate(boxed):
        pc[4 + i * 80:4 + (i + 1) * 80] = raw[:80]
    sections = []
    for section in range(14):
        data = bytes(team) if section == 1 else bytes(pc[(section - 5) * SECTION_DATA_SIZE:(section - 4) * SECTION_DATA_SIZE]) if section >= 5 else b''
        sections.append(_make_section_bytes(section, 1, data))
    return b''.join(sections).ljust(SAVE_SIZE, b'\0')


@pytest.fixture
async def sync_service():
    if not os.getenv('RUN_DB_TESTS'):
        pytest.skip('Requires migrated PostgreSQL database')
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            async with AsyncSession(bind=connection, join_transaction_mode='create_savepoint', expire_on_commit=False) as db:
                yield SyncService(db)
            await transaction.rollback()
    finally:
        await engine.dispose()


async def test_removal_preview_confirm_reappearance_and_isolation(sync_service):
    service = sync_service
    uid = -987654323
    a = _make_raw_pokemon(pid=101)
    b = _make_raw_pokemon(pid=102)
    service.drive_service.download_sav = AsyncMock(return_value=(make_save([a, b]), ''))
    preview = await service.preview(uid)
    await service.confirm(uid, preview.sync_session_id)
    original = {p.pid: p for p in await service.pokemon_repo.list_for_user(uid)}
    original_b = original[102].id
    for user_id, game, added_via, pid in [(uid, 'firered', 'manual', 201), (uid, 'emerald', 'sync', 202), (uid - 1, 'firered', 'sync', 203)]:
        service.db.add(PokemonInstance(user_id=user_id, game=game, added_via=added_via, pid=pid, ot_id=1, ot_secret_id=2, species_id=25, species_name='Pikachu'))
    await service.db.commit()
    service.drive_service.download_sav.return_value = (make_save(boxed=[a]), '')
    preview = await service.preview(uid)
    assert preview.removed_count == 1
    assert [item.pokemon.pid for item in preview.items if item.status == 'removed'] == [102]
    assert len(await service.pokemon_repo.list_for_user(uid)) == 4
    result = await service.confirm(uid, preview.sync_session_id)
    assert result.removed_count == 1
    assert {p.pid for p in await service.pokemon_repo.list_for_user(uid)} == {101, 201, 202}
    assert original[101].party_slot is None
    assert await service.pokemon_repo.get_with_measurements(original_b, uid) is None
    assert len(await service.pokemon_repo.list_for_user(uid - 1)) == 1
    again = await service.preview(uid)
    assert again.removed_count == 0
    service.drive_service.download_sav.return_value = (make_save([a, b]), '')
    returned = await service.preview(uid)
    assert returned.new_count == 1
    await service.confirm(uid, returned.sync_session_id)
    assert (await service.pokemon_repo.find_by_identity(uid, 102, 6, 5)).id == original_b
    assert len(await service.pokemon_repo.list_for_user(uid)) == 4
    service.drive_service.download_sav.return_value = (make_save(), '')
    empty = await service.preview(uid)
    assert empty.removed_count == 2
    await service.confirm(uid, empty.sync_session_id)
    assert {p.pid for p in await service.pokemon_repo.list_for_user(uid)} == {201, 202}


async def test_changed_or_corrupt_save_does_not_remove_pokemon(sync_service):
    service = sync_service
    uid = -987654324
    raw = _make_raw_pokemon(pid=105)
    service.drive_service.download_sav = AsyncMock(return_value=(make_save([raw]), ''))
    preview = await service.preview(uid)
    await service.confirm(uid, preview.sync_session_id)
    preview = await service.preview(uid)
    service.drive_service.download_sav.return_value = (make_save(), '')
    with pytest.raises(ValueError, match='cambió'):
        await service.confirm(uid, preview.sync_session_id)
    assert len(await service.pokemon_repo.list_for_user(uid)) == 1
    corrupt = bytearray(raw)
    corrupt[32] ^= 1
    service.drive_service.download_sav.return_value = (make_save([bytes(corrupt)]), '')
    with pytest.raises(SaveParseError):
        await service.preview(uid)
    assert len(await service.pokemon_repo.list_for_user(uid)) == 1


def test_strict_parser_rejects_corrupt_box_instead_of_treating_it_as_empty():
    raw = bytearray(_make_raw_pokemon())
    raw[32] ^= 1
    with pytest.raises(SaveParseError):
        FireRedParser(strict=True).parse(make_save(boxed=[bytes(raw)]))
