from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.pokemon_repo import PokemonRepository
from ..models.pokemon import PokemonInstance, PokemonMeasurement
from ..schemas.pokemon import ManualPokemonIn, PokemonOut, MeasurementOut


class PokemonService:
    def __init__(self, db: AsyncSession):
        self.repo = PokemonRepository(db)

    async def list_for_user(self, user_id: int) -> list[PokemonOut]:
        instances = await self.repo.list_for_user(user_id)
        result = []
        for inst in instances:
            latest = MeasurementOut.from_db(inst.measurements[-1]) if inst.measurements else None
            out = _instance_to_out(inst, latest, [])
            result.append(out)
        return result

    async def get_detail(self, pokemon_id: int, user_id: int) -> PokemonOut | None:
        inst = await self.repo.get_with_measurements(pokemon_id, user_id)
        if not inst:
            return None
        measurements = [MeasurementOut.from_db(m) for m in inst.measurements]
        latest = measurements[-1] if measurements else None
        return _instance_to_out(inst, None, measurements, latest)

    async def create_manual(self, user_id: int, data: ManualPokemonIn) -> PokemonOut:
        import random
        fake_pid = random.randint(1, 0x7FFFFFFF)

        instance = PokemonInstance(
            user_id=user_id,
            pid=fake_pid,
            ot_id=0,
            ot_secret_id=0,
            species_id=data.species_id,
            species_name=data.species_name,
            nickname=data.nickname,
            current_level=data.level,
            nature_name=data.nature_name,
            gender=data.gender,
            is_shiny=data.is_shiny,
            origin=data.origin,
            game=data.game,
            form_name=data.form_name,
            added_via="manual",
        )
        instance = await self.repo.create(instance)

        iv_source = "manual" if data.iv_hp is not None else "unknown"
        ev_source = "manual" if data.ev_hp is not None else "unknown"

        measurement = PokemonMeasurement(
            instance_id=instance.id,
            level=data.level,
            nickname=data.nickname,
            hp=data.hp,
            attack=data.attack,
            defense=data.defense,
            speed=data.speed,
            sp_attack=data.sp_attack,
            sp_defense=data.sp_defense,
            iv_hp=data.iv_hp,
            iv_attack=data.iv_attack,
            iv_defense=data.iv_defense,
            iv_speed=data.iv_speed,
            iv_sp_attack=data.iv_sp_attack,
            iv_sp_defense=data.iv_sp_defense,
            iv_source=iv_source,
            ev_hp=data.ev_hp,
            ev_attack=data.ev_attack,
            ev_defense=data.ev_defense,
            ev_speed=data.ev_speed,
            ev_sp_attack=data.ev_sp_attack,
            ev_sp_defense=data.ev_sp_defense,
            ev_source=ev_source,
            moves=[m.model_dump() for m in data.moves] if data.moves else None,
            item_name=data.item_name,
            data_source="manual",
        )
        measurement = await self.repo.add_measurement(measurement)
        await self.repo.db.commit()
        await self.repo.db.refresh(instance)
        return _instance_to_out(instance, MeasurementOut.from_db(measurement), [MeasurementOut.from_db(measurement)])


def _instance_to_out(
    inst: PokemonInstance,
    latest: MeasurementOut | None,
    measurements: list[MeasurementOut],
    override_latest: MeasurementOut | None = None,
) -> PokemonOut:
    return PokemonOut(
        id=inst.id,
        species_id=inst.species_id,
        species_name=inst.species_name,
        nickname=inst.nickname,
        current_level=inst.current_level,
        nature_name=inst.nature_name,
        gender=inst.gender,
        is_shiny=inst.is_shiny,
        ot_name=inst.ot_name,
        ot_id=inst.ot_id,
        origin=inst.origin,
        game=inst.game,
        added_via=inst.added_via,
        party_slot=inst.party_slot,
        first_seen_at=inst.first_seen_at,
        latest_measurement=override_latest or latest,
        measurements=measurements,
    )
