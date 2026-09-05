import { X } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Pokemon } from '../../types/pokemon'

export default function LatestChanges({ pokemon, revision, onDismiss }: { pokemon: Pokemon[]; revision: string; onDismiss: () => void }) {
  if (!revision || !pokemon.length) return null
  return (
    <section className="bg-gray-900 border border-gray-800 rounded-2xl p-4" aria-label="Últimos cambios">
      <div className="flex items-center justify-between gap-3 mb-3">
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Últimos cambios</h2>
        <button type="button" onClick={onDismiss} aria-label="Cerrar últimos cambios" className="w-9 h-9 -m-2 flex items-center justify-center text-gray-500 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {pokemon.map(p => (
          <Link key={p.id} to={`/pokemon/${p.id}`} className="bg-gray-800 hover:bg-gray-700 rounded-lg px-3 py-2 text-sm text-white">
            {p.species_name}{p.is_shiny ? ' ✨' : ''} <span className="text-gray-500">Nv. {p.current_level ?? '?'}</span>
          </Link>
        ))}
      </div>
    </section>
  )
}
