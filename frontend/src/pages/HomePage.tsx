import { useState, useMemo } from 'react'
import { isAxiosError } from 'axios'
import { useQuery } from '@tanstack/react-query'
import { GAMES, getDriveConfigs, type Game } from '../api/drive'
import GameCollections from '../components/pokemon/GameCollections'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, RefreshCw, ArrowUp, ArrowDown, X, Clipboard, ClipboardCheck } from 'lucide-react'
import { usePokemonList } from '../hooks/usePokemon'
import { useSyncPreview, useSyncConfirm } from '../hooks/useSync'
import SyncModal from '../components/sync/SyncModal'
import PokemonCard from '../components/pokemon/PokemonCard'
import MissingPokemonCard from '../components/pokemon/MissingPokemonCard'
import LatestChanges from '../components/pokemon/LatestChanges'
import { collectionRowName, orderByRegionalDex } from '../data/collectionOrder'
import { regionalDex } from '../data/regionalDex'
import { ivTotal } from '../components/pokemon/IVStars'
import { getPrimaryType, TYPE_COLOR, TYPE_ES, TYPE_ICON_URL } from '../data/pokemonTypes'
import type { SyncPreview, Pokemon } from '../types/pokemon'
import type { PokemonType } from '../data/pokemonTypes'

type SortKey = 'name' | 'level' | 'dex' | 'missing' | 'stars' | 'recent'

function sorted(list: Pokemon[], key: SortKey, asc: boolean): Pokemon[] {
  const dir = asc ? 1 : -1
  return [...list].sort((a, b) => {
    if (key === 'name') return dir * a.species_name.localeCompare(b.species_name)
    if (key === 'level') return dir * ((a.current_level ?? 0) - (b.current_level ?? 0))
    if (key === 'dex' || key === 'missing') return dir * (a.species_id - b.species_id)
    if (key === 'recent') return dir * (new Date(a.first_seen_at).getTime() - new Date(b.first_seen_at).getTime())
    if (key === 'stars') {
      const sa = a.latest_measurement?.ivs ? ivTotal(a.latest_measurement.ivs) : -1
      const sb = b.latest_measurement?.ivs ? ivTotal(b.latest_measurement.ivs) : -1
      return dir * (sa - sb)
    }
    return 0
  })
}

export default function HomePage({ showGames = false }: { showGames?: boolean }) {
  const { data: pokemon = [], isLoading } = usePokemonList()
  const [preview, setPreview] = useState<SyncPreview | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()
  const { data: configs = [] } = useQuery({ queryKey: ['drive-configs'], queryFn: getDriveConfigs })
  const selectedGame = searchParams.get('game') ?? 'all'
  const syncedGames: Game[] = GAMES.filter(g => configs.some(c => c.game === g.id && c.synced_at)
    || pokemon.some(p => p.game === g.id && p.added_via === 'sync')).map(g => g.id)
  const collection = useMemo(() => selectedGame === 'all' ? pokemon : pokemon.filter(p => p.game === selectedGame), [pokemon, selectedGame])

  const search = searchParams.get('q') ?? ''
  const sortKey = (searchParams.get('sort') ?? 'dex') as SortKey
  const sortAsc = searchParams.get('asc') !== '0'
  const typeFilter = searchParams.get('type') as PokemonType | null

  function setSearch(q: string) {
    setSearchParams((p) => { q ? p.set('q', q) : p.delete('q'); return p }, { replace: true })
  }
  function setSortKey(k: SortKey) {
    setSearchParams((p) => {
      p.set('sort', k)
      p.delete('missing')
      if (k === 'stars' || k === 'level' || k === 'recent') p.set('asc', '0')
      else p.set('asc', '1')
      return p
    }, { replace: true })
  }
  function setSortAsc(fn: (v: boolean) => boolean) {
    setSearchParams((p) => { p.set('asc', fn(sortAsc) ? '1' : '0'); return p }, { replace: true })
  }
  function setTypeFilter(t: PokemonType | null) {
    setSearchParams((p) => { t ? p.set('type', t) : p.delete('type'); return p }, { replace: true })
  }

  const [copied, setCopied] = useState(false)

  function copyCollection() {
    const lines: string[] = ['=== Mi Colección ===', '']
    const bydex = [...collection].sort((a, b) => a.species_id - b.species_id)
    bydex.forEach((p) => {
      const m = p.latest_measurement
      lines.push(`${p.species_name}${p.is_shiny ? ' ✨' : ''} — Nv. ${p.current_level ?? '?'}${p.nature_name ? ` — ${p.nature_name}` : ''}`)
      if (m) {
        if (m.hp != null) lines.push(`  Stats: PS:${m.hp} Atq:${m.attack} Def:${m.defense} At.Esp:${m.sp_attack} Def.Esp:${m.sp_defense} Vel:${m.speed}`)
        if (m.ivs) lines.push(`  IVs:  HP:${m.ivs.hp} Atq:${m.ivs.attack} Def:${m.ivs.defense} At.Esp:${m.ivs.sp_attack} Def.Esp:${m.ivs.sp_defense} Vel:${m.ivs.speed}`)
        if (m.evs) {
          const t = m.evs.hp+m.evs.attack+m.evs.defense+m.evs.sp_attack+m.evs.sp_defense+m.evs.speed
          if (t > 0) lines.push(`  EVs:  HP:${m.evs.hp} Atq:${m.evs.attack} Def:${m.evs.defense} At.Esp:${m.evs.sp_attack} Def.Esp:${m.evs.sp_defense} Vel:${m.evs.speed}`)
        }
        if (m.moves?.length) lines.push(`  Movs: ${m.moves.map(mv => mv.move_name).join(', ')}`)
      }
      lines.push('')
    })
    navigator.clipboard.writeText(lines.join('\n'))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const [dismissedRevision, setDismissedRevision] = useState(() => localStorage.getItem('dismissedRecentRevision') ?? '')
  const syncPreviewMut = useSyncPreview()
  const syncConfirmMut = useSyncConfirm()

  async function handleSync() {
    try {
      const result = await syncPreviewMut.mutateAsync()
      setPreview(result)
    } catch (error) {
      alert(isAxiosError(error) && typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail : 'Error al sincronizar. Verificá tu configuración de Google Drive.')
    }
  }

  async function handleConfirm() {
    if (!preview) return
    try {
      await syncConfirmMut.mutateAsync(preview.sync_session_ids ?? [preview.sync_session_id])
      setPreview(null)
    } catch (error) {
      alert(isAxiosError(error) && typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail : 'No se pudo confirmar la sincronización. Intentá nuevamente.')
      if (isAxiosError(error) && error.response?.status === 409) setPreview(null)
    }
  }

  const recent = useMemo(() => [...pokemon].filter(p => p.added_via === 'sync').sort((a, b) =>
    new Date(b.latest_measurement?.recorded_at ?? b.first_seen_at).getTime() - new Date(a.latest_measurement?.recorded_at ?? a.first_seen_at).getTime()).slice(0, 5), [pokemon])
  const recentRevision = useMemo(() => {
    const revisions = [...configs.map(c => c.synced_at ?? ''), ...recent.map(p => p.latest_measurement?.recorded_at ?? p.first_seen_at)].sort()
    return revisions[revisions.length - 1] ?? ''
  }, [configs, recent])
  const hasNewRecent = Boolean(recentRevision && recentRevision !== dismissedRevision)

  function dismissRecent() {
    localStorage.setItem('dismissedRecentRevision', recentRevision)
    setDismissedRevision(recentRevision)
  }

  // Types present in collection
  const availableTypes = useMemo(() => {
    const types = new Set<PokemonType>()
    collection.forEach((p) => types.add(getPrimaryType(p.species_id)))
    return [...types].sort()
  }, [collection])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    let list = q
      ? collection.filter((p) =>
          p.species_name.toLowerCase().includes(q) ||
          (p.nickname ?? '').toLowerCase().includes(q)
        )
      : collection
    if (typeFilter) {
      list = list.filter((p) => getPrimaryType(p.species_id) === typeFilter)
    }
    return sorted(list, sortKey, sortAsc)
  }, [collection, search, sortKey, sortAsc, typeFilter])

  const showMissing = sortKey === 'missing'
  const dexRows = useMemo(() => {
    const rows = orderByRegionalDex(collection, selectedGame, showMissing, sortAsc)
    const q = search.trim().toLowerCase()
    return rows.filter(row => {
      const speciesId = row.kind === 'pokemon' ? row.pokemon.species_id : row.speciesId
      return (!q || collectionRowName(row).toLowerCase().includes(q)) && (!typeFilter || getPrimaryType(speciesId) === typeFilter)
    })
  }, [collection, selectedGame, showMissing, sortAsc, search, typeFilter])
  const regionalSpecies = useMemo(() => new Set(regionalDex(selectedGame)), [selectedGame])
  const regionalOwned = useMemo(() => new Set(collection.filter(p => regionalSpecies.has(p.species_id)).map(p => p.species_id)).size, [collection, regionalSpecies])
  const regionalRows = dexRows.filter(row => row.kind === 'missing' || (!row.repeated && row.regionalNumber !== null))
  const outsideRows = dexRows.filter(row => row.kind === 'pokemon' && !row.repeated && row.regionalNumber === null)
  const repeatedRows = dexRows.filter(row => row.kind === 'pokemon' && row.repeated)

  return (
    <div className="space-y-6">
      {!showGames && <Link to="/" className="inline-flex text-sm text-gray-400 hover:text-white">← Volver a las partidas</Link>}
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white">{showGames ? 'Mis partidas' : GAMES.find(g => g.id === selectedGame)?.name ?? 'Todos mis Pokémon'}</h1>
          <p className="text-sm text-gray-500 mt-0.5">{showGames ? 'Elegí una partida para ver sus Pokémon' : `${collection.length} Pokémon registrados`}</p>
        </div>
        <div className="flex items-center gap-2">
          {!showGames && collection.length > 0 && (
            <button
              onClick={copyCollection}
              title="Copiar colección"
              className="p-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 transition-colors"
            >
              {copied
                ? <ClipboardCheck className="w-4 h-4 text-green-400" />
                : <Clipboard className="w-4 h-4 text-gray-300" />
              }
            </button>
          )}
          <button
            onClick={handleSync}
            title="Sincronizar todas las partidas configuradas"
            disabled={syncPreviewMut.isPending}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:text-blue-400 text-white font-semibold px-4 py-2.5 rounded-xl text-sm transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${syncPreviewMut.isPending ? 'animate-spin' : ''}`} />
            {syncPreviewMut.isPending ? 'Sincronizando...' : 'Sincronizar'}
          </button>
        </div>
      </div>

      {showGames && (isLoading ? <p className="text-gray-400">Cargando partidas...</p> : <GameCollections games={syncedGames} pokemon={pokemon} />)}

      {showGames && hasNewRecent && <LatestChanges pokemon={recent} revision={recentRevision} onDismiss={dismissRecent} />}

      {!showGames && <>

      {/* Search + Sort */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre..."
            className="w-full bg-gray-900 border border-gray-800 focus:border-blue-500 text-white rounded-xl pl-9 pr-9 py-2.5 text-sm focus:outline-none transition-colors placeholder-gray-600"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        <select
          value={sortKey}
          onChange={(e) => setSortKey(e.target.value as SortKey)}
          className="bg-gray-900 border border-gray-800 text-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 transition-colors"
        >
          <option value="dex">N° Pokédex</option>
          <option value="missing">Faltantes</option>
          <option value="name">Nombre</option>
          <option value="level">Nivel</option>
          <option value="stars">Estrellas</option>
          <option value="recent">Reciente</option>
        </select>
        <button
          onClick={() => setSortAsc((v) => !v)}
          className="bg-gray-900 border border-gray-800 hover:border-gray-600 text-gray-300 rounded-xl px-3 py-2.5 text-sm transition-colors"
          title={sortAsc ? 'Ascendente' : 'Descendente'}
        >
          {sortAsc ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Type filter */}
      {availableTypes.length > 0 && (
        <div className="overflow-x-auto min-w-0 w-full" style={{ scrollbarWidth: 'none' }}>
        <div className="flex gap-2 pb-0.5" style={{ minWidth: 'max-content' }}>
          {typeFilter && (
            <button
              onClick={() => setTypeFilter(null)}
              className="shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
            >
              <X className="w-3 h-3" /> Todos
            </button>
          )}
          {availableTypes.map((t) => {
            const active = typeFilter === t
            return (
              <button
                key={t}
                onClick={() => setTypeFilter(active ? null : t)}
                className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
                style={{
                  backgroundColor: active ? TYPE_COLOR[t] : TYPE_COLOR[t] + '22',
                  color: active ? '#fff' : TYPE_COLOR[t],
                  border: `1px solid ${TYPE_COLOR[t]}55`,
                }}
              >
                <img
                  src={TYPE_ICON_URL[t]}
                  alt=""
                  className="w-3.5 h-3.5 object-contain"
                  style={{ filter: active ? 'brightness(0) invert(1)' : undefined }}
                />
                {TYPE_ES[t]}
              </button>
            )
          })}
        </div>
        </div>
      )}

      {/* Grid */}
      <section>
        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="bg-gray-900 rounded-2xl h-32 animate-pulse" />
            ))}
          </div>
        ) : ((sortKey === 'dex' || sortKey === 'missing') ? dexRows.length : filtered.length) === 0 ? (
          <div className="text-center py-20 text-gray-600">
            {search || typeFilter ? (
              <>
                <Search className="w-10 h-10 mx-auto mb-3 text-gray-600" />
                <p className="font-medium text-gray-400">Sin resultados</p>
              </>
            ) : (
              <>
                <div className="text-5xl mb-4">📭</div>
                <p className="font-medium text-gray-400">Sin Pokémon todavía</p>
                <p className="text-sm mt-1">Sincronizá tu partida o agregá uno manualmente</p>
              </>
            )}
          </div>
        ) : (sortKey === 'dex' || sortKey === 'missing') ? (
          <div className="space-y-8">
            {sortKey === 'missing' && !search && !typeFilter && (
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">Pokédex regional</p>
                  <p className="text-xs text-gray-500 mt-1">Especies registradas</p>
                </div>
                <strong className="text-2xl text-blue-400">{regionalOwned}/{regionalSpecies.size}</strong>
              </div>
            )}
            {regionalRows.length > 0 && <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {regionalRows.map(row => row.kind === 'missing'
                ? <MissingPokemonCard key={`missing-${row.speciesId}`} speciesId={row.speciesId} regionalNumber={row.regionalNumber} />
                : <PokemonCard key={row.pokemon.id} pokemon={row.pokemon} regionalNumber={row.regionalNumber} />)}
            </div>}
            {outsideRows.length > 0 && <section className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Otra región</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {outsideRows.map(row => row.kind === 'pokemon' && <PokemonCard key={row.pokemon.id} pokemon={row.pokemon} />)}
              </div>
            </section>}
            {repeatedRows.length > 0 && <section className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Repetidos</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {repeatedRows.map(row => row.kind === 'pokemon' && <PokemonCard key={row.pokemon.id} pokemon={row.pokemon} regionalNumber={row.regionalNumber} repeated />)}
              </div>
            </section>}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {filtered.map(p => <PokemonCard key={p.id} pokemon={p} />)}
          </div>
        )}
      </section>

      </>}

      {preview && (
        <SyncModal
          preview={preview}
          onConfirm={handleConfirm}
          onCancel={() => setPreview(null)}
          isConfirming={syncConfirmMut.isPending}
        />
      )}
    </div>
  )
}
