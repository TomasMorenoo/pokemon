import { useParams, Link, useLocation } from 'react-router-dom'
import { Mars, Venus } from 'lucide-react'
import { usePokemonDetail } from '../hooks/usePokemon'
import { IVStars, ivTotal } from '../components/pokemon/IVStars'
import PokemonSprite from '../components/pokemon/PokemonSprite'

const ACCENT: Record<number, string> = {
  1: '#ef4444', 2: '#f97316', 3: '#eab308', 4: '#22c55e',
  5: '#3b82f6', 6: '#6366f1', 7: '#a855f7', 8: '#ec4899', 9: '#6b7280',
}
function accent(id: number) { return ACCENT[(id % 9) + 1] }

function Bar({ label, value, max, color = '#facc15' }: { label: string; value: number | null; max: number; color?: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-gray-400 text-xs w-24 shrink-0">{label}</span>
      <span className="font-mono text-sm w-8 text-right text-white">{value ?? '?'}</span>
      <div className="flex-1 bg-gray-800 rounded-full h-1.5 overflow-hidden">
        {value != null && (
          <div className="h-full rounded-full" style={{ width: `${Math.min((value / max) * 100, 100)}%`, backgroundColor: color }} />
        )}
      </div>
    </div>
  )
}

function IVBar({ label, value, source }: { label: string; value: number | null; source: string }) {
  const real = source === 'save'
  return (
    <div className="flex items-center gap-3">
      <span className="text-gray-400 text-xs w-24 shrink-0">{label}</span>
      <span className={`font-mono text-sm w-8 text-right ${real ? 'text-green-400' : 'text-yellow-400'}`}>{value ?? '?'}</span>
      <div className="flex-1 bg-gray-800 rounded-full h-1.5 overflow-hidden">
        {value != null && (
          <div className="h-full rounded-full" style={{ width: `${(value / 31) * 100}%`, backgroundColor: real ? '#4ade80' : '#facc15' }} />
        )}
      </div>
    </div>
  )
}

const GAME_LABELS: Record<string, string> = {
  red: 'Rojo', blue: 'Azul', yellow: 'Amarillo',
  gold: 'Oro', silver: 'Plata', crystal: 'Cristal',
  ruby: 'Rubí', sapphire: 'Zafiro', emerald: 'Esmeralda',
  firered: 'Rojo Fuego', leafgreen: 'Verde Hoja',
  diamond: 'Diamante', pearl: 'Perla', platinum: 'Platino',
  heartgold: 'Oro HeartGold', soulsilver: 'Plata SoulSilver',
  black: 'Negro', white: 'Blanco', black2: 'Negro 2', white2: 'Blanco 2',
  x: 'X', y: 'Y', omegaruby: 'Rubí Omega', alphasapphire: 'Zafiro Alfa',
  sun: 'Sol', moon: 'Luna', ultrasun: 'Ultrasol', ultramoon: 'Ultraluna',
  letsgopikachu: "Let's Go, Pikachu!", letsgoeevee: "Let's Go, Eevee!",
  sword: 'Espada', shield: 'Escudo',
  brilliantdiamond: 'Diamante Brillante', shiningpearl: 'Perla Reluciente',
  legendsarceus: 'Leyendas: Arceus',
  scarlet: 'Escarlata', violet: 'Púrpura',
}

const STAT_LABELS: Record<string, string> = {
  hp: 'PS', attack: 'Ataque', defense: 'Defensa',
  sp_attack: 'At. Esp.', sp_defense: 'Def. Esp.', speed: 'Velocidad',
}
const STAT_KEYS = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'] as const

export default function PokemonDetailPage() {
  const location = useLocation()
  const { id } = useParams<{ id: string }>()
  const { data: pokemon, isLoading } = usePokemonDetail(Number(id))

  if (isLoading) return (
    <div className="space-y-4 animate-pulse">
      <div className="h-40 bg-gray-900 rounded-2xl" />
      <div className="h-48 bg-gray-900 rounded-2xl" />
    </div>
  )
  if (!pokemon) return <div className="text-gray-500 py-20 text-center">No encontrado</div>

  const latest = pokemon.latest_measurement
  const dexNum = String(pokemon.species_id).padStart(4, '0')
  const color = accent(pokemon.species_id)

  return (
    <div className="space-y-4">
      {/* Back */}
      <Link to={`/collection${location.search}`} className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors">
        ← Volver
      </Link>

      {/* Hero */}
      <div
        className="rounded-2xl p-6 relative overflow-hidden"
        style={{ background: `linear-gradient(135deg, ${color}22 0%, #111827 60%)` }}
      >
        <PokemonSprite speciesId={pokemon.species_id} shiny={pokemon.is_shiny} name={pokemon.species_name} className="w-24 h-24 object-contain" />
        <div
          className="absolute -top-8 -right-8 w-40 h-40 rounded-full opacity-20"
          style={{ backgroundColor: color }}
        />
        {/* Level + gender — always pinned top-right over the circle */}
        <div className="absolute top-5 right-5 text-right z-10">
          <div className="text-3xl font-black leading-none" style={{ color }}>Nv. {pokemon.current_level ?? '?'}</div>
          <div className="text-sm mt-1 flex items-center justify-end gap-1">
            {pokemon.gender === 'M' && <><Mars className="w-4 h-4 text-blue-400" /><span className="text-blue-400">Macho</span></>}
            {pokemon.gender === 'F' && <><Venus className="w-4 h-4 text-pink-400" /><span className="text-pink-400">Hembra</span></>}
            {pokemon.gender === 'N' && <span className="text-gray-400">Sin género</span>}
          </div>
        </div>

        <div className="relative pr-28">
          <span className="text-xs text-gray-500 font-mono">#{dexNum}</span>
          <h1 className="text-3xl font-extrabold text-white mt-0.5">
            {pokemon.species_name}{pokemon.is_shiny ? ' ✨' : ''}
          </h1>
          {pokemon.nickname && pokemon.nickname !== pokemon.species_name && (
            <p className="text-sm mt-1" style={{ color }}>&ldquo;{pokemon.nickname}&rdquo;</p>
          )}
          <div className="flex flex-wrap gap-2 mt-3">
            {pokemon.nature_name && (
              <span className="text-xs bg-gray-800 border border-gray-700 px-2.5 py-1 rounded-full">{pokemon.nature_name}</span>
            )}
            <span className="text-xs bg-gray-800 border border-gray-700 px-2.5 py-1 rounded-full capitalize">{pokemon.origin}</span>
          </div>
        </div>
      </div>

      {/* Two-column on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left col */}
        <div className="space-y-4">
          {/* OT */}
          <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Entrenador Original</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-500 text-xs mb-0.5">Nombre</div>
                <div className="text-white font-medium">{pokemon.ot_name ?? '—'}</div>
              </div>
              <div>
                <div className="text-gray-500 text-xs mb-0.5">ID</div>
                <div className="text-white font-medium">{pokemon.ot_id}</div>
              </div>
              {pokemon.game && (
                <div>
                  <div className="text-gray-500 text-xs mb-0.5">Juego</div>
                  <div className="text-white font-medium">{GAME_LABELS[pokemon.game] ?? pokemon.game}</div>
                </div>
              )}
            </div>
          </section>

          {/* Stats */}
          <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Stats</h2>
            <div className="space-y-3">
              {STAT_KEYS.map((k) => (
                <Bar key={k} label={STAT_LABELS[k]} value={latest?.[k] ?? null} max={255} color={color} />
              ))}
            </div>
          </section>

          {/* Moves */}
          {latest?.moves && latest.moves.length > 0 && (
            <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Movimientos</h2>
              <div className="grid grid-cols-2 gap-2">
                {latest.moves.map((m, i) => (
                  <div key={i} className="bg-gray-800 rounded-xl px-3 py-2.5">
                    <div className="text-sm font-medium text-white">{m.move_name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">PP {m.pp}/{m.pp_max}</div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Right col */}
        <div className="space-y-4">
          {/* IVs */}
          {latest?.ivs && (
            <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">IVs</h2>
                  <IVStars ivs={latest.ivs} size="md" />
                  <span className="text-xs text-gray-600 font-mono">{ivTotal(latest.ivs)}/186</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  latest.ivs.source === 'save'
                    ? 'bg-green-400/10 text-green-400'
                    : 'bg-yellow-400/10 text-yellow-400'
                }`}>
                  {latest.ivs.source === 'save' ? 'Desde save' : 'Calculado'}
                </span>
              </div>
              <div className="space-y-3">
                {STAT_KEYS.map((k) => (
                  <IVBar key={k} label={STAT_LABELS[k]} value={latest.ivs![k] ?? null} source={latest.ivs!.source} />
                ))}
              </div>
            </section>
          )}

          {/* EVs */}
          {latest?.evs && (
            <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">EVs</h2>
                <span className="text-xs text-gray-500">
                  {STAT_KEYS.reduce((acc, k) => acc + (latest.evs?.[k] ?? 0), 0)} / 510
                </span>
              </div>
              <div className="space-y-3">
                {STAT_KEYS.map((k) => (
                  <Bar key={k} label={STAT_LABELS[k]} value={latest.evs![k] ?? null} max={252} color={color} />
                ))}
              </div>
            </section>
          )}

          {/* History */}
          {pokemon.measurements.length > 1 && (
            <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Historial</h2>
              <div className="space-y-2">
                {[...pokemon.measurements].reverse().map((m) => (
                  <div key={m.id} className="flex items-center justify-between text-sm py-1">
                    <span className="text-gray-500 text-xs">
                      {new Date(m.recorded_at).toLocaleDateString('es-AR', {
                        day: '2-digit', month: '2-digit', year: '2-digit',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                    <span className="text-white font-medium">Nv. {m.level ?? '?'}</span>
                    <span className="text-gray-600 text-xs capitalize">{m.data_source}</span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
