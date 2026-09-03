from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.auth_service import get_current_user
from ..services.pokemon_service import PokemonService
from ..schemas.pokemon import PokemonOut, ManualPokemonIn, MeasurementOut
from ..models.user import User

router = APIRouter()


@router.get("/", response_model=list[PokemonOut])
async def list_pokemon(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PokemonService(db)
    return await service.list_for_user(current_user.id)


@router.get("/{pokemon_id}", response_model=PokemonOut)
async def get_pokemon(
    pokemon_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PokemonService(db)
    pkm = await service.get_detail(pokemon_id, current_user.id)
    if not pkm:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pkm


@router.post("/", response_model=PokemonOut, status_code=201)
async def add_manual_pokemon(
    data: ManualPokemonIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PokemonService(db)
    return await service.create_manual(current_user.id, data)
