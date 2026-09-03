from datetime import datetime, timezone
from hashlib import sha256
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.pokemon_repo import PokemonRepository
from ..models.bag import TrainerBag
from ..repositories.sync_repo import SyncRepository
from ..models.pokemon import PokemonInstance, PokemonMeasurement
from ..models.sync import SyncSession
from ..models.drive import DriveConfig
from ..schemas.sync import SyncPreviewOut, SyncDiffItem, ParsedPokemonPreview, SyncResultOut
from .drive_service import DriveService
from sqlalchemy import select


class SyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pokemon_repo = PokemonRepository(db)
        self.sync_repo = SyncRepository(db)
        self.drive_service = DriveService(db)

    async def preview(self, user_id: int, game: str = "firered", commit: bool = True) -> SyncPreviewOut:
        from parsers.gen3.firered.parser import FireRedParser

        sav_data, modified_time = await self.drive_service.download_sav(user_id, game)
        parser = FireRedParser(strict=True, game=game)
        parsed_save = parser.parse(sav_data)

        all_pokemon = []
        for pkm in parsed_save.party:
            all_pokemon.append(pkm)
        for box in parsed_save.boxes:
            for pkm in box:
                if pkm:
                    all_pokemon.append(pkm)

        diff_items = []
        new_count = updated_count = unchanged_count = 0

        for pkm in all_pokemon:
            existing = await self.pokemon_repo.find_by_identity(
                user_id, pkm.pid, pkm.ot_id, pkm.ot_secret_id, game
            )
            preview = ParsedPokemonPreview(
                species_name=pkm.species_name,
                species_id=pkm.species_id,
                nickname=pkm.nickname,
                level=pkm.level,
                nature_name=pkm.nature_name,
                gender=pkm.gender,
                is_shiny=pkm.is_shiny,
                pid=pkm.pid,
                ot_id=pkm.ot_id,
            )
            if not existing or not existing.is_present:
                diff_items.append(SyncDiffItem(game=game, status="new", pokemon=preview))
                new_count += 1
            else:
                latest = await self.pokemon_repo.get_latest_measurement(existing.id)
                changes = _detect_changes(existing, pkm, latest)
                if changes:
                    diff_items.append(SyncDiffItem(game=game, status="updated", pokemon=preview, changes=changes))
                    updated_count += 1
                else:
                    diff_items.append(SyncDiffItem(game=game, status="unchanged", pokemon=preview))
                    unchanged_count += 1

        identities = {(p.pid, p.ot_id, p.ot_secret_id) for p in all_pokemon}
        removed = [p for p in await self.pokemon_repo.list_for_user(user_id)
                   if p.added_via == "sync" and p.game == parsed_save.game
                   and (p.pid, p.ot_id, p.ot_secret_id) not in identities]
        for p in removed:
            diff_items.append(SyncDiffItem(game=game, status="removed", pokemon=ParsedPokemonPreview(
                species_name=p.species_name, species_id=p.species_id,
                nickname=p.nickname or p.species_name, level=p.current_level or 0,
                nature_name=p.nature_name or "", gender=p.gender or "N",
                is_shiny=p.is_shiny, pid=p.pid, ot_id=p.ot_id,
            )))

        sync_session = SyncSession(
            user_id=user_id,
            status="pending",
            drive_file_id=None,
            drive_modified_time=modified_time,
            new_pokemon_count=new_count,
            updated_pokemon_count=updated_count,
            unchanged_count=unchanged_count,
            diff_result={
                "save_sha256": sha256(sav_data).hexdigest(),
                "game": parsed_save.game,
                "removed_ids": [p.id for p in removed],
                "modified_time": modified_time,
                "pokemon": [
                    {
                        "status": item.status,
                        "pid": item.pokemon.pid,
                        "ot_id": item.pokemon.ot_id,
                        "species_id": item.pokemon.species_id,
                        "species_name": item.pokemon.species_name,
                        "nickname": item.pokemon.nickname,
                        "level": item.pokemon.level,
                        "nature_name": item.pokemon.nature_name,
                        "gender": item.pokemon.gender,
                        "is_shiny": item.pokemon.is_shiny,
                        "changes": item.changes,
                    }
                    for item in diff_items
                ],
            },
        )
        sync_session = await self.sync_repo.create(sync_session)
        if commit:
            await self.db.commit()

        return SyncPreviewOut(
            game=game,
            sync_session_id=sync_session.id,
            new_count=new_count,
            updated_count=updated_count,
            unchanged_count=unchanged_count,
            removed_count=len(removed),
            items=diff_items,
        )

    async def confirm(self, user_id: int, sync_session_id: int, commit: bool = True) -> SyncResultOut:
        from parsers.gen3.firered.parser import FireRedParser

        sync_session = await self.sync_repo.get(sync_session_id, user_id)
        if not sync_session:
            raise ValueError("Sync session not found")
        if sync_session.status not in ("pending",):
            raise ValueError(f"Cannot confirm session with status: {sync_session.status}")

        diff = sync_session.diff_result or {}
        game = diff.get("game", "firered")
        sav_data, modified_time = await self.drive_service.download_sav(user_id, game)
        if diff.get("save_sha256") != sha256(sav_data).hexdigest():
            raise ValueError("La partida cambió desde la vista previa. Volvé a sincronizar antes de confirmar.")
        parser = FireRedParser(strict=True, game=game)
        parsed_save = parser.parse(sav_data)

        sync_session.status = "running"
        await self.db.flush()

        # Build party set (pid, ot_id, ot_secret_id) → party_slot
        party_set = {(p.pid, p.ot_id, p.ot_secret_id): p.party_slot for p in parsed_save.party}

        all_pokemon = list(parsed_save.party)
        for box in parsed_save.boxes:
            for pkm in box:
                if pkm:
                    all_pokemon.append(pkm)

        for pkm in all_pokemon:
            existing = await self.pokemon_repo.find_by_identity(
                user_id, pkm.pid, pkm.ot_id, pkm.ot_secret_id, game
            )
            new_party_slot = party_set.get((pkm.pid, pkm.ot_id, pkm.ot_secret_id))
            if not existing:
                instance = PokemonInstance(
                    user_id=user_id,
                    pid=pkm.pid,
                    ot_id=pkm.ot_id,
                    ot_secret_id=pkm.ot_secret_id,
                    species_id=pkm.species_id,
                    species_name=pkm.species_name,
                    nickname=pkm.nickname,
                    current_level=pkm.level,
                    current_experience=pkm.experience,
                    nature_id=pkm.nature_id,
                    nature_name=pkm.nature_name,
                    gender=pkm.gender,
                    is_shiny=pkm.is_shiny,
                    ability_slot=pkm.ability_slot,
                    ot_name=pkm.ot_name,
                    game=game,
                    generation=3,
                    added_via="sync",
                    origin="unknown",
                    party_slot=new_party_slot,
                )
                instance = await self.pokemon_repo.create(instance)
            else:
                existing.is_present = True
                existing.is_shiny = pkm.is_shiny
                existing.species_id = pkm.species_id
                existing.species_name = pkm.species_name
                existing.current_level = pkm.level
                existing.current_experience = pkm.experience
                existing.nickname = pkm.nickname
                existing.party_slot = new_party_slot
                instance = existing

            latest = await self.pokemon_repo.get_latest_measurement(instance.id)
            if latest is None or _measurement_has_changed(latest, pkm):
                measurement = PokemonMeasurement(
                    instance_id=instance.id,
                    sync_session_id=sync_session.id,
                    level=pkm.level,
                    experience=pkm.experience,
                    nickname=pkm.nickname,
                    hp=pkm.max_hp,
                    attack=pkm.stat_attack,
                    defense=pkm.stat_defense,
                    speed=pkm.stat_speed,
                    sp_attack=pkm.stat_sp_attack,
                    sp_defense=pkm.stat_sp_defense,
                    iv_hp=pkm.ivs.hp,
                    iv_attack=pkm.ivs.attack,
                    iv_defense=pkm.ivs.defense,
                    iv_speed=pkm.ivs.speed,
                    iv_sp_attack=pkm.ivs.sp_attack,
                    iv_sp_defense=pkm.ivs.sp_defense,
                    iv_source=pkm.ivs.source.value,
                    ev_hp=pkm.evs.hp,
                    ev_attack=pkm.evs.attack,
                    ev_defense=pkm.evs.defense,
                    ev_speed=pkm.evs.speed,
                    ev_sp_attack=pkm.evs.sp_attack,
                    ev_sp_defense=pkm.evs.sp_defense,
                    ev_source=pkm.evs.source.value,
                    moves=[{"move_id": m.move_id, "move_name": m.move_name, "pp": m.pp, "pp_max": m.pp_max} for m in pkm.moves],
                    item_id=pkm.item_id,
                    item_name=pkm.item_name,
                    data_source="sync",
                )
                await self.pokemon_repo.add_measurement(measurement)

        removed_count = 0
        for instance in await self.pokemon_repo.list_for_user(user_id):
            if (instance.id in diff.get("removed_ids", [])
                    and instance.added_via == "sync" and instance.game == parsed_save.game):
                instance.is_present = False
                instance.party_slot = None
                removed_count += 1

        # Upsert trainer bag
        result = await self.db.execute(select(TrainerBag).where(TrainerBag.user_id == user_id, TrainerBag.game == game))
        bag = result.scalar_one_or_none()
        if bag:
            bag.tms = parsed_save.tms
        else:
            self.db.add(TrainerBag(user_id=user_id, game=game, tms=parsed_save.tms))

        # Update drive config with new modified time
        result = await self.db.execute(
            select(DriveConfig).where(DriveConfig.user_id == user_id, DriveConfig.game == game)
        )
        drive_config = result.scalar_one_or_none()
        if drive_config:
            drive_config.last_drive_modified = modified_time
            drive_config.synced_at = datetime.now(timezone.utc)

        sync_session.status = "completed"
        sync_session.completed_at = datetime.now(timezone.utc)
        if commit:
            await self.db.commit()

        return SyncResultOut(
            game=game,
            sync_session_id=sync_session.id,
            status="completed",
            new_count=sync_session.new_pokemon_count,
            updated_count=sync_session.updated_pokemon_count,
            unchanged_count=sync_session.unchanged_count,
            removed_count=removed_count,
            completed_at=sync_session.completed_at,
        )


    async def preview_all(self, user_id: int) -> list[SyncPreviewOut]:
        configs = list((await self.db.execute(select(DriveConfig).where(DriveConfig.user_id == user_id).order_by(DriveConfig.game))).scalars())
        if not configs:
            raise ValueError("Agregá al menos una partida en Ajustes antes de sincronizar.")
        previews = []
        for config in configs:
            try:
                previews.append(await self.preview(user_id, config.game, commit=False))
            except Exception as exc:
                raise ValueError(f"No se pudo leer {config.game}: {exc}") from exc
        await self.db.commit()
        return previews

    async def confirm_all(self, user_id: int, session_ids: list[int]) -> list[SyncResultOut]:
        if not session_ids or len(session_ids) > 5 or len(set(session_ids)) != len(session_ids):
            raise ValueError("La selección de partidas no es válida.")
        results = []
        games = set()
        for session_id in sorted(session_ids):
            result = await self.confirm(user_id, session_id, commit=False)
            if result.game in games:
                raise ValueError("Hay más de una sincronización para el mismo juego.")
            games.add(result.game)
            results.append(result)
        await self.db.commit()
        return results


def _detect_changes(existing: PokemonInstance, pkm, latest=None) -> dict | None:
    changes = {}
    if existing.species_id != pkm.species_id:
        changes["evolution"] = {"from": existing.species_name, "to": pkm.species_name}
    if existing.current_level != pkm.level:
        changes["level"] = {"from": existing.current_level, "to": pkm.level}
    if existing.nickname != pkm.nickname:
        changes["nickname"] = {"from": existing.nickname, "to": pkm.nickname}
    if latest and latest.moves:
        old_ids = {m["move_id"]: m["move_name"] for m in latest.moves}
        new_ids = {m.move_id: m.move_name for m in pkm.moves}
        added = [name for mid, name in new_ids.items() if mid not in old_ids]
        removed = [name for mid, name in old_ids.items() if mid not in new_ids]
        if added or removed:
            changes["moves"] = {"added": added, "removed": removed}
    return changes if changes else None


def _measurement_has_changed(latest: PokemonMeasurement, pkm) -> bool:
    return (
        latest.level != pkm.level
        or latest.experience != pkm.experience
        or latest.nickname != pkm.nickname
        or latest.hp is None
        or latest.iv_hp != pkm.ivs.hp
        or latest.iv_attack != pkm.ivs.attack
        or latest.iv_defense != pkm.ivs.defense
        or latest.iv_speed != pkm.ivs.speed
        or latest.iv_sp_attack != pkm.ivs.sp_attack
        or latest.iv_sp_defense != pkm.ivs.sp_defense
        or latest.ev_hp != pkm.evs.hp
        or latest.ev_attack != pkm.evs.attack
    )
