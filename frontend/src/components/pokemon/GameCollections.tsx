import { Layers } from 'lucide-react'
import { Link } from 'react-router-dom'
import { GAMES, type Game } from '../../api/drive'
import type { Pokemon } from '../../types/pokemon'

export default function GameCollections({ games, pokemon }: {
  games: Game[]; pokemon: Pokemon[]
}) {
  return (
    <section aria-label="Partidas sincronizadas" className="space-y-3">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Tus partidas</p>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-3xl">
        <Link to="/collection" className="min-w-0 p-3 rounded-2xl border border-gray-800 bg-gray-900 hover:border-blue-400 text-left transition-colors">
          <div className="aspect-square rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
            <Layers className="w-12 h-12 text-blue-300" />
          </div>
          <p className="text-sm font-semibold text-white mt-2">Todo</p>
          <p className="text-xs text-gray-400">{pokemon.length} Pokémon</p>
        </Link>
        {GAMES.filter(game => games.includes(game.id)).map(game => (
          <Link key={game.id} to={`/collection?game=${game.id}`}
            className="min-w-0 p-3 rounded-2xl border border-gray-800 bg-gray-900 text-left transition-colors hover:bg-gray-800">
            <img src={`/games/${game.id}.png`} alt={`Carátula de Pokémon ${game.name}`} className="w-full aspect-square object-contain rounded-xl" />
            <p className="text-sm font-semibold text-white mt-2">{game.name}</p>
            <p className="text-xs text-gray-400">{pokemon.filter(p => p.game === game.id).length} Pokémon</p>
          </Link>
        ))}
      </div>
    </section>
  )
}
