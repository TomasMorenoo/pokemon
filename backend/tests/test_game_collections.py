from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.models.bag import TrainerBag
from app.models.drive import DriveConfig
from parsers.gen3.firered.parser import FireRedParser
from tests.test_sync_presence import make_save, sync_service
from tests.parsers.gen3.firered.test_pokemon_struct import _make_raw_pokemon

GAMES = ["firered", "leafgreen", "emerald", "ruby", "sapphire"]


@pytest.mark.parametrize("game", GAMES)
def test_party_boxes_hoenn_species_and_bag(game):
    raw = _make_raw_pokemon(pid=1, otid=0x00010000, species_id=277)
    boxed = _make_raw_pokemon(pid=2, species_id=406)
    parsed = FireRedParser(strict=True, game=game).parse(make_save([raw], [boxed], game, tm=True))
    assert parsed.game == game
    assert parsed.party[0].species_id == 252
    assert parsed.party[0].species_name == "Treecko"
    assert parsed.party[0].is_shiny
    assert parsed.boxes[0][0].species_id == 384
    assert parsed.boxes[0][0].species_name == "Rayquaza"
    assert parsed.tms


async def test_batch_keeps_same_pokemon_and_removals_separate(sync_service):
    service = sync_service
    uid = -987654331
    raw = _make_raw_pokemon(pid=101)
    saves = {game: make_save([raw], game=game, tm=True) for game in GAMES}
    for game in GAMES:
        service.db.add(DriveConfig(user_id=uid, game=game, file_id=f"test_{game}", file_name=f"{game}.sav"))
    await service.db.commit()

    async def download(user_id, game):
        return saves[game], ""

    service.drive_service.download_sav = AsyncMock(side_effect=download)
    previews = await service.preview_all(uid)
    assert len(previews) == 5
    assert all(p.new_count == 1 for p in previews)
    results = await service.confirm_all(uid, [p.sync_session_id for p in previews])
    assert len(results) == 5
    pokemon = await service.pokemon_repo.list_for_user(uid)
    assert len(pokemon) == 5
    assert {p.game for p in pokemon} == set(GAMES)
    assert len({p.id for p in pokemon}) == 5
    bags = (await service.db.execute(select(TrainerBag).where(TrainerBag.user_id == uid))).scalars().all()
    assert len(bags) == 5
    configs = (await service.db.execute(select(DriveConfig).where(DriveConfig.user_id == uid))).scalars().all()
    assert all(c.synced_at for c in configs)

    saves["emerald"] = make_save(game="emerald")
    previews = await service.preview_all(uid)
    assert sum(p.removed_count for p in previews) == 1
    assert next(p for p in previews if p.game == "emerald").removed_count == 1
    await service.confirm_all(uid, [p.sync_session_id for p in previews])
    assert {p.game for p in await service.pokemon_repo.list_for_user(uid)} == set(GAMES) - {"emerald"}


async def test_batch_failure_rolls_back_earlier_games(sync_service):
    service = sync_service
    uid = -987654332
    saves = {game: make_save([_make_raw_pokemon(pid=101)], game=game) for game in GAMES}
    for game in GAMES:
        service.db.add(DriveConfig(user_id=uid, game=game, file_id=game, file_name=f"{game}.sav"))
    await service.db.commit()

    async def download(user_id, game):
        return saves[game], ""

    service.drive_service.download_sav = AsyncMock(side_effect=download)
    previews = await service.preview_all(uid)
    saves[previews[-1].game] = make_save(game=previews[-1].game)
    with pytest.raises(ValueError, match="cambió"):
        try:
            await service.confirm_all(uid, [p.sync_session_id for p in previews])
        except Exception:
            await service.db.rollback()
            raise
    assert await service.pokemon_repo.list_for_user(uid) == []
    configs = (await service.db.execute(select(DriveConfig).where(DriveConfig.user_id == uid))).scalars().all()
    assert all(c.synced_at is None for c in configs)
