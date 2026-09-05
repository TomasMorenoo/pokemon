import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Mars, Venus } from 'lucide-react'
import type { Pokemon } from '../../types/pokemon'
import { IVStars } from './IVStars'
import { getPrimaryType, getTypes, TYPE_COLOR, TYPE_ES, TYPE_ICON_URL } from '../../data/pokemonTypes'
import { Pokeball } from '../ui/Pokeball'
import PokemonSprite from './PokemonSprite'
import { GAMES } from '../../api/drive'

export default function PokemonCard({ pokemon, regionalNumber, repeated = false }: { pokemon: Pokemon; regionalNumber?: number | null; repeated?: boolean }) {
  const location = useLocation()
  const primary = getPrimaryType(pokemon.species_id)
  const [type1, type2] = getTypes(pokemon.species_id)
  const color = TYPE_COLOR[primary]
  const name = pokemon.nickname && pokemon.nickname !== pokemon.species_name
    ? pokemon.nickname
    : pokemon.species_name

  return (
    <Link
      to={`/pokemon/${pokemon.id}${location.search}`}
      className="group bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-gray-700 rounded-2xl p-4 flex flex-col gap-2 transition-all"
    >
      {/* Sprite left + types+stars right */}
      <div className="flex items-start justify-between">
        <div
          className="w-20 h-20 sm:w-28 sm:h-28 rounded-xl flex items-center justify-center overflow-hidden shrink-0"
          style={{ backgroundColor: color + '22' }}
        >
          <PokemonSprite speciesId={pokemon.species_id} shiny={pokemon.is_shiny} name={pokemon.species_name} className="w-full h-full object-contain" />
        </div>

        <div className="flex flex-col gap-1.5 items-end">
          {[type1, type2].filter(Boolean).map((t) => (
            <div
              key={t}
              title={TYPE_ES[t!]}
              className="w-5 h-5 sm:w-6 sm:h-6"
              style={{
                backgroundColor: TYPE_COLOR[t!],
                maskImage: `url(${TYPE_ICON_URL[t!]})`,
                maskSize: 'contain',
                maskRepeat: 'no-repeat',
                maskPosition: 'center',
                WebkitMaskImage: `url(${TYPE_ICON_URL[t!]})`,
                WebkitMaskSize: 'contain',
                WebkitMaskRepeat: 'no-repeat',
                WebkitMaskPosition: 'center',
              } as React.CSSProperties}
            />
          ))}
          {pokemon.is_shiny && <span className="text-sm">✨</span>}
        </div>
      </div>

      {/* Info */}
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500 flex items-center gap-0.5">
            <Pokeball className="w-3 h-3" colored />#{String(regionalNumber ?? pokemon.species_id).padStart(regionalNumber ? 3 : 4, '0')}
          </span>
          <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: color + '33', color }}>
            Nv. {pokemon.current_level ?? '?'}
          </span>
        </div>
        <div className="font-semibold text-sm leading-tight text-white truncate">{name}</div>
        <div className="text-[10px] text-gray-500">{GAMES.find(g => g.id === pokemon.game)?.name ?? 'Manual'}</div>
        {repeated && <div className="text-[10px] uppercase tracking-wider text-amber-600">Repetido</div>}
        <div className="flex items-center justify-between mt-0.5">
          <span className="text-xs text-gray-500 truncate">
            {pokemon.nickname && pokemon.nickname !== pokemon.species_name ? pokemon.species_name : ''}
          </span>
          <div className="flex items-center gap-1 shrink-0">
            <IVStars ivs={pokemon.latest_measurement?.ivs ?? null} />
            {pokemon.gender === 'M' && <Mars className="w-3.5 h-3.5 text-blue-400" />}
            {pokemon.gender === 'F' && <Venus className="w-3.5 h-3.5 text-pink-400" />}
          </div>
        </div>
      </div>

    </Link>
  )
}
