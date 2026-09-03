import { useState, useEffect, useRef } from 'react'
import { Search, X, Clipboard, ClipboardCheck } from 'lucide-react'
import { usePokemonList, useTrainerBag } from '../hooks/usePokemon'
import { getTypes } from '../data/pokemonTypes'
import { getEffectiveness } from '../data/typeEffectiveness'
import { TYPE_ES, TYPE_ICON_URL } from '../data/pokemonTypes'
import { GAMES, type Game } from '../api/drive'
import type { Pokemon } from '../types/pokemon'
import type { PokemonType } from '../data/pokemonTypes'

interface Rival {
  name: string
  sprite: string | null
  types: PokemonType[]
  isType?: boolean
}

interface MoveScore {
  move_name: string
  type: PokemonType
  eff: number
}

interface TeamScore {
  pkm: Pokemon
  bestOffensive: number
  bestMove: MoveScore | null
  offType: PokemonType
  offEff: number
  defensiveExposure: number
  total: number
}

const EFF_COLOR: Record<string, string> = {
  '4': '#22c55e', '2': '#86efac', '1': '#9ca3af',
  '0.5': '#f87171', '0.25': '#ef4444', '0': '#6b7280',
}
function effColor(eff: number): string { return EFF_COLOR[String(eff)] ?? '#9ca3af' }
function effLabel(eff: number): string { return eff === 0 ? 'x0' : `x${eff}` }

function starsIcon(total: number): string {
  if (total >= 4) return '★★★'
  if (total >= 1.5) return '★★'
  if (total >= 0.75) return '★'
  return '☆'
}
function starsColor(total: number): string {
  if (total >= 4) return 'text-yellow-300'
  if (total >= 1.5) return 'text-yellow-500'
  if (total >= 0.75) return 'text-orange-500'
  return 'text-gray-600'
}

const POKEAPI_TYPE_MAP: Record<string, PokemonType> = {
  normal: 'Normal', fire: 'Fire', water: 'Water', electric: 'Electric',
  grass: 'Grass', ice: 'Ice', fighting: 'Fighting', poison: 'Poison',
  ground: 'Ground', flying: 'Flying', psychic: 'Psychic', bug: 'Bug',
  rock: 'Rock', ghost: 'Ghost', dragon: 'Dragon', dark: 'Dark', steel: 'Steel',
}

// Spanish → PokemonType lookup (normalized, no accents)
const normalize = (s: string) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
const TYPE_ES_LOOKUP: Record<string, PokemonType> = Object.fromEntries(
  Object.entries(TYPE_ES).map(([k, v]) => [normalize(v), k as PokemonType])
)
function matchType(q: string): PokemonType | null {
  return TYPE_ES_LOOKUP[normalize(q)] ?? null
}

function spriteUrl(speciesId: number, shiny = false): string {
  return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${shiny ? 'shiny/' : ''}${speciesId}.png`
}

const ALL_TYPES = Object.keys(TYPE_ES) as PokemonType[]

export default function CombatPage() {
  const { data: allPokemon = [] } = usePokemonList()
  const [game, setGame] = useState<Game>('firered')
  const { data: bag } = useTrainerBag(game)
  const [moveTypes, setMoveTypes] = useState<Record<number, PokemonType>>({})
  const [rival, setRival] = useState<Rival | null>(null)
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<{ name: string; id: number }[]>([])
  const [typeSuggestions, setTypeSuggestions] = useState<PokemonType[]>([])
  const [allNames, setAllNames] = useState<{ name: string; id: number }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  const team = [...allPokemon]
    .filter(p => p.game === game)
    .filter((p) => p.party_slot !== null && p.party_slot !== undefined)
    .sort((a, b) => (a.party_slot ?? 99) - (b.party_slot ?? 99))

  useEffect(() => {
    fetch('https://pokeapi.co/api/v2/pokemon?limit=386')
      .then((r) => r.json())
      .then((data) => setAllNames(data.results.map((p: { name: string }, i: number) => ({ name: p.name, id: i + 1 }))))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const ids = new Set<number>()
    team.forEach((p) => p.latest_measurement?.moves?.forEach((m) => ids.add(m.move_id)))
    if (ids.size === 0) return
    const missing = [...ids].filter((id) => !(id in moveTypes))
    if (missing.length === 0) return
    Promise.all(
      missing.map((id) =>
        fetch(`https://pokeapi.co/api/v2/move/${id}`)
          .then((r) => r.json())
          .then((d) => ({ id, type: POKEAPI_TYPE_MAP[d.type?.name] as PokemonType | undefined }))
          .catch(() => ({ id, type: undefined }))
      )
    ).then((results) => {
      setMoveTypes((prev) => {
        const next = { ...prev }
        results.forEach(({ id, type }) => { if (type) next[id] = type })
        return next
      })
    })
  }, [team.map((p) => p.id).join(',')])

  useEffect(() => {
    function handle(e: MouseEvent) {
      if (!inputRef.current?.contains(e.target as Node) && !suggestionsRef.current?.contains(e.target as Node))
        setShowSuggestions(false)
    }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [])

  function handleQueryChange(v: string) {
    setQuery(v)
    setError(null)
    if (!v.trim()) { setSuggestions([]); setTypeSuggestions([]); setShowSuggestions(false); return }

    const q = normalize(v)
    // Type suggestions (Spanish)
    const matchedTypes = ALL_TYPES.filter((t) => normalize(TYPE_ES[t]).startsWith(q))
    // Pokemon name suggestions
    const matchedPokemon = allNames.filter((p) => p.name.includes(v.toLowerCase()) || String(p.id).startsWith(v)).slice(0, 6)

    setSuggestions(matchedPokemon)
    setTypeSuggestions(matchedTypes)
    setShowSuggestions(matchedTypes.length > 0 || matchedPokemon.length > 0)
  }

  function selectType(type: PokemonType) {
    setQuery(TYPE_ES[type])
    setRival({ name: TYPE_ES[type], sprite: null, types: [type], isType: true })
    setShowSuggestions(false)
    setError(null)
  }

  async function searchRival(nameOrId?: string) {
    const raw = (nameOrId ?? query).trim()
    if (!raw) return

    // Check if it's a type search
    const typeMatch = matchType(raw)
    if (typeMatch) { selectType(typeMatch); return }

    const q = raw.toLowerCase().replace(/\s+/g, '-')
    setLoading(true)
    setError(null)
    setShowSuggestions(false)
    try {
      const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${q}`)
      if (!res.ok) throw new Error('No encontrado')
      const data = await res.json()
      const types: PokemonType[] = data.types
        .sort((a: { slot: number }, b: { slot: number }) => a.slot - b.slot)
        .map((t: { type: { name: string } }) => POKEAPI_TYPE_MAP[t.type.name])
        .filter(Boolean)
      const displayName = data.name.charAt(0).toUpperCase() + data.name.slice(1)
      setQuery(displayName)
      setRival({ name: displayName, sprite: data.sprites?.front_default ?? null, types })
    } catch {
      setError('Pokémon no encontrado')
    } finally {
      setLoading(false)
    }
  }

  function scoreTeam(rivalTypes: PokemonType[]): TeamScore[] {
    return team.map((pkm) => {
      const myTypes = getTypes(pkm.species_id)
      const moves = pkm.latest_measurement?.moves ?? []
      const moveCandidates: MoveScore[] = moves
        .filter((m) => moveTypes[m.move_id])
        .map((m) => ({ move_name: m.move_name, type: moveTypes[m.move_id], eff: getEffectiveness(moveTypes[m.move_id], rivalTypes) }))
      const typeScores = myTypes.filter(Boolean).map((t) => ({ type: t!, eff: getEffectiveness(t!, rivalTypes) }))
      const bestMoveEff = moveCandidates.length > 0 ? Math.max(...moveCandidates.map((m) => m.eff)) : 0
      const bestTypeEff = typeScores.length > 0 ? Math.max(...typeScores.map((t) => t.eff)) : 0
      const bestOffensive = Math.max(bestMoveEff, bestTypeEff, 0.25)
      const useMove = bestMoveEff >= bestTypeEff && moveCandidates.length > 0
      const bestMove = useMove ? (moveCandidates.find((m) => m.eff === bestMoveEff) ?? null) : null
      const offType = bestMove ? bestMove.type : (typeScores.sort((a, b) => b.eff - a.eff)[0]?.type ?? myTypes[0]!)
      const offEff = bestMove ? bestMove.eff : bestTypeEff
      const defensiveExposure = Math.max(...rivalTypes.map((rt) => getEffectiveness(rt, myTypes.filter(Boolean) as PokemonType[])), 0.25)
      return { pkm, bestOffensive, bestMove, offType, offEff, defensiveExposure, total: bestOffensive / defensiveExposure }
    }).sort((a, b) => b.total - a.total)
  }

  const scores = rival ? scoreTeam(rival.types) : []

  const [copied, setCopied] = useState(false)

  function copyTeam() {
    const lines: string[] = ['=== Mi Equipo ===', '']
    team.forEach((p, i) => {
      const m = p.latest_measurement
      lines.push(`${i + 1}. ${p.species_name}${p.is_shiny ? ' ✨' : ''} — Nv. ${p.current_level ?? '?'}${p.nature_name ? ` — ${p.nature_name}` : ''}`)
      if (m) {
        if (m.hp != null) lines.push(`   Stats: PS:${m.hp} Atq:${m.attack} Def:${m.defense} At.Esp:${m.sp_attack} Def.Esp:${m.sp_defense} Vel:${m.speed}`)
        if (m.ivs) lines.push(`   IVs:   HP:${m.ivs.hp} Atq:${m.ivs.attack} Def:${m.ivs.defense} At.Esp:${m.ivs.sp_attack} Def.Esp:${m.ivs.sp_defense} Vel:${m.ivs.speed} (${m.ivs.hp+m.ivs.attack+m.ivs.defense+m.ivs.sp_attack+m.ivs.sp_defense+m.ivs.speed}/186)`)
        if (m.evs) {
          const evTotal = m.evs.hp+m.evs.attack+m.evs.defense+m.evs.sp_attack+m.evs.sp_defense+m.evs.speed
          if (evTotal > 0) lines.push(`   EVs:   HP:${m.evs.hp} Atq:${m.evs.attack} Def:${m.evs.defense} At.Esp:${m.evs.sp_attack} Def.Esp:${m.evs.sp_defense} Vel:${m.evs.speed}`)
        }
        if (m.moves && m.moves.length > 0) lines.push(`   Movs:  ${m.moves.map(mv => mv.move_name).join(', ')}`)
      }
      lines.push('')
    })
    if (bag?.tms?.length) {
      lines.push('=== MTs en la mochila ===')
      lines.push(bag.tms.join(', '))
      lines.push('')
    }
    navigator.clipboard.writeText(lines.join('\n'))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-5 sm:space-y-6 min-w-0">
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
        <h1 className="text-2xl font-extrabold text-white">Combate</h1>
        <select aria-label="Partida para combate" value={game} onChange={e => setGame(e.target.value as Game)} className="w-full sm:w-auto min-w-0 min-h-11 bg-gray-900 border border-gray-800 rounded-xl px-3 py-2 text-base sm:text-sm text-gray-300">
          {GAMES.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
        <p className="w-full text-sm text-gray-500">¿A quién querés enfrentarte?</p>
      </div>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Mi equipo</h2>
          {team.length > 0 && (
            <button
              onClick={copyTeam}
              title="Copiar estadísticas del equipo"
              className="flex items-center gap-1.5 min-h-11 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors text-xs font-medium"
            >
              {copied
                ? <><ClipboardCheck className="w-4 h-4 text-green-400" /><span className="text-green-400">¡Copiado!</span></>
                : <><Clipboard className="w-4 h-4 text-gray-300" /><span className="text-gray-300">Copiar stats</span></>
              }
            </button>
          )}
        </div>
        {team.length === 0 ? (
          <p className="text-gray-600 text-sm">No hay Pokémon en el equipo. Sincronizá tu partida.</p>
        ) : (
          <div className="grid grid-cols-2 min-[420px]:grid-cols-3 xl:grid-cols-6 gap-2 sm:gap-3">
            {team.map((p) => (
              <div key={p.id} className="bg-gray-900 border border-gray-800 rounded-xl p-2.5 sm:p-3 flex flex-col items-center gap-1.5 sm:gap-2 min-w-0">
                <img
                  src={spriteUrl(p.species_id, p.is_shiny)}
                  alt={p.species_name}
                  className="w-16 h-16 sm:w-20 sm:h-20 object-contain"
                  style={{ imageRendering: 'pixelated' }}
                />
                <div className="text-sm font-semibold text-white text-center leading-tight break-words w-full">
                  {p.species_name}{p.is_shiny ? ' ✨' : ''}
                </div>
                <div className="flex gap-1.5 justify-center">
                  {getTypes(p.species_id).filter(Boolean).map((t) => (
                    <img key={t} src={TYPE_ICON_URL[t!]} alt={TYPE_ES[t!]} title={TYPE_ES[t!]} className="w-5 h-5 object-contain" />
                  ))}
                </div>
                <div className="text-xs text-gray-600">Nv. {p.current_level ?? '?'}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Rival search */}
      <section>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Rival</h2>
        <div className="flex gap-2">
          <div className="relative flex-1 min-w-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => handleQueryChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchRival()}
              onFocus={() => (suggestions.length > 0 || typeSuggestions.length > 0) && setShowSuggestions(true)}
              placeholder="Nombre, número o tipo..."
              className="w-full min-h-11 bg-gray-900 border border-gray-800 focus:border-blue-500 text-white rounded-xl pl-9 pr-9 py-2.5 text-base sm:text-sm focus:outline-none transition-colors placeholder-gray-600"
            />
            {query && (
              <button
                onClick={() => { setQuery(''); setRival(null); setError(null); setSuggestions([]); setTypeSuggestions([]); setShowSuggestions(false) }}
                aria-label="Limpiar rival"
                className="absolute right-0 top-1/2 -translate-y-1/2 w-9 h-11 flex items-center justify-center text-gray-500 hover:text-gray-300"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

            {showSuggestions && (typeSuggestions.length > 0 || suggestions.length > 0) && (
              <div
                ref={suggestionsRef}
                className="absolute top-full left-0 right-0 mt-1 bg-gray-900 border border-gray-700 rounded-xl max-h-[50vh] overflow-y-auto overscroll-contain z-30 shadow-xl"
              >
                {/* Type suggestions first */}
                {typeSuggestions.length > 0 && (
                  <>
                    <div className="px-4 py-1.5 text-xs text-gray-600 uppercase tracking-wider border-b border-gray-800">Tipos</div>
                    {typeSuggestions.map((t) => (
                      <button
                        key={t}
                        onMouseDown={(e) => { e.preventDefault(); selectType(t) }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-800 text-left transition-colors"
                      >
                        <img src={TYPE_ICON_URL[t]} alt="" className="w-5 h-5 object-contain" />
                        <span className="text-sm text-white">{TYPE_ES[t]}</span>
                        <span className="text-xs text-gray-600 ml-auto">tipo</span>
                      </button>
                    ))}
                  </>
                )}
                {/* Pokemon suggestions */}
                {suggestions.length > 0 && (
                  <>
                    {typeSuggestions.length > 0 && <div className="border-t border-gray-800" />}
                    {suggestions.map((s) => (
                      <button
                        key={s.id}
                        onMouseDown={(e) => { e.preventDefault(); searchRival(s.name) }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-800 text-left transition-colors"
                      >
                        <img src={spriteUrl(s.id)} alt="" className="w-8 h-8 object-contain" style={{ imageRendering: 'pixelated' }} />
                        <span className="text-sm text-white capitalize">{s.name}</span>
                        <span className="text-xs text-gray-600 ml-auto">#{String(s.id).padStart(3, '0')}</span>
                      </button>
                    ))}
                  </>
                )}
              </div>
            )}
          </div>
          <button
            onClick={() => searchRival()}
            disabled={loading || !query.trim()}
            className="shrink-0 min-h-11 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:text-blue-400 text-white font-semibold px-3 sm:px-4 py-2.5 rounded-xl text-sm transition-colors"
          >
            {loading ? '...' : 'Buscar'}
          </button>
        </div>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}

        {rival && (
          <div className="mt-3 flex items-center gap-3 bg-gray-900 border border-gray-800 rounded-xl px-4 py-3">
            {rival.sprite
              ? <img src={rival.sprite} alt={rival.name} className="w-12 h-12 object-contain" style={{ imageRendering: 'pixelated' }} />
              : rival.isType && (
                <img src={TYPE_ICON_URL[rival.types[0]]} alt="" className="w-10 h-10 object-contain" />
              )
            }
            <div>
              <div className="text-white font-semibold">{rival.name}</div>
              <div className="flex gap-1.5 mt-1">
                {rival.types.map((t) => (
                  <img key={t} src={TYPE_ICON_URL[t]} alt={TYPE_ES[t]} title={TYPE_ES[t]} className="w-5 h-5 object-contain" />
                ))}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Results */}
      {rival && scores.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Mejor matchup</h2>
          <div className="space-y-2">
            {scores.map(({ pkm, offType, offEff, bestMove, defensiveExposure, total }) => (
              <div key={pkm.id} className="bg-gray-900 border border-gray-800 rounded-xl px-3 sm:px-4 py-3 grid grid-cols-[2.5rem_minmax(0,1fr)_auto] items-center gap-x-2 sm:gap-x-4 gap-y-1">
                <img src={spriteUrl(pkm.species_id, pkm.is_shiny)} alt={pkm.species_name} className="w-10 h-10 object-contain row-span-2" style={{ imageRendering: 'pixelated' }} />
                <span className={`col-start-3 row-start-1 text-sm sm:text-base whitespace-nowrap text-right ${starsColor(total)}`}>{starsIcon(total)}</span>
                <div className="col-start-2 row-start-1 row-span-2 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-white font-medium text-sm">{pkm.species_name}</span>
                    {pkm.is_shiny && <span>✨</span>}
                  </div>
                  <div className="flex items-center gap-3 mt-1 flex-wrap">
                    <div className="flex flex-wrap items-center gap-1.5 text-xs min-w-0">
                      <img src={TYPE_ICON_URL[offType]} alt="" className="w-3.5 h-3.5 object-contain" />
                      <span className="text-gray-400 break-words min-w-0">{bestMove ? bestMove.move_name : TYPE_ES[offType]}</span>
                      <span className="font-bold font-mono" style={{ color: effColor(offEff) }}>{effLabel(offEff)}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <span>🛡</span>
                      <span className="font-mono" style={{ color: effColor(defensiveExposure) }}>{effLabel(defensiveExposure)}</span>
                    </div>
                  </div>
                </div>
                <div className="col-start-3 row-start-2 text-right text-xs text-gray-500 font-mono">{total.toFixed(2)}</div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
