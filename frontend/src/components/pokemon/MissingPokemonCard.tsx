import { GEN3_NAMES } from '../../data/regionalDex'
import { getPrimaryType, TYPE_COLOR } from '../../data/pokemonTypes'
import PokemonSprite from './PokemonSprite'

export default function MissingPokemonCard({ speciesId, regionalNumber }: { speciesId: number; regionalNumber: number }) {
  const name = GEN3_NAMES[speciesId] ?? `Pokémon #${speciesId}`
  const color = TYPE_COLOR[getPrimaryType(speciesId)]
  return (
    <article aria-label={`${name}, faltante`} className="bg-gray-950 border border-dashed border-gray-800 rounded-2xl p-4 flex flex-col gap-2 opacity-75">
      <div className="w-20 h-20 sm:w-28 sm:h-28 rounded-xl flex items-center justify-center overflow-hidden" style={{ backgroundColor: `${color}0d` }}>
        <PokemonSprite speciesId={speciesId} name={name} className="w-full h-full object-contain brightness-0 opacity-35" />
      </div>
      <span className="text-xs text-gray-600">#{String(regionalNumber).padStart(3, '0')}</span>
      <p className="font-semibold text-sm text-gray-500 truncate">{name}</p>
      <span className="text-[10px] uppercase tracking-wider text-gray-700">Faltante</span>
    </article>
  )
}
