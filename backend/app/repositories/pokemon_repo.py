from sqlalchemy import select, and_, type_coerce, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models.pokemon import PokemonInstance, PokemonMeasurement


class PokemonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_identity(
        self, user_id: int, pid: int, ot_id: int, ot_secret_id: int
    ) -> PokemonInstance | None:
        result = await self.db.execute(
            select(PokemonInstance).where(
                and_(
                    PokemonInstance.user_id == user_id,
                    PokemonInstance.pid == type_coerce(pid, BigInteger),
                    PokemonInstance.ot_id == type_coerce(ot_id, BigInteger),
                    PokemonInstance.ot_secret_id == type_coerce(ot_secret_id, BigInteger),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[PokemonInstance]:
        result = await self.db.execute(
            select(PokemonInstance)
            .where(PokemonInstance.user_id == user_id)
            .options(selectinload(PokemonInstance.measurements))
            .order_by(PokemonInstance.species_id, PokemonInstance.id)
        )
        return list(result.scalars().all())

    async def get_with_measurements(self, instance_id: int, user_id: int) -> PokemonInstance | None:
        result = await self.db.execute(
            select(PokemonInstance)
            .where(
                and_(
                    PokemonInstance.id == instance_id,
                    PokemonInstance.user_id == user_id,
                )
            )
            .options(selectinload(PokemonInstance.measurements))
        )
        return result.scalar_one_or_none()

    async def create(self, instance: PokemonInstance) -> PokemonInstance:
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def add_measurement(self, measurement: PokemonMeasurement) -> PokemonMeasurement:
        self.db.add(measurement)
        await self.db.flush()
        return measurement

    async def get_latest_measurement(self, instance_id: int) -> PokemonMeasurement | None:
        result = await self.db.execute(
            select(PokemonMeasurement)
            .where(PokemonMeasurement.instance_id == instance_id)
            .order_by(PokemonMeasurement.recorded_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
