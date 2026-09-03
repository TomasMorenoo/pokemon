import type React from 'react'
import type { SyncPreview, SyncDiffItem } from '../../types/pokemon'
import { GAMES } from '../../api/drive'

interface Props {
  preview: SyncPreview
  onConfirm: () => void
  onCancel: () => void
  isConfirming: boolean
}

function ChangeSummary({ item }: { item: SyncDiffItem }) {
  if (item.status === 'removed') {
    return <span className="text-red-300 text-xs">Ya no está en el equipo ni en las cajas. Se quitará de tu Pokédex.</span>
  }
  if (item.status === 'new') {
    return (
      <span className="text-green-400 text-xs">Nv. {item.pokemon.level}</span>
    )
  }
  if (!item.changes) return null

  const parts: React.ReactNode[] = []

  if (item.changes.evolution) {
    const { from, to } = item.changes.evolution as { from: string; to: string }
    parts.push(
      <span key="evo" className="text-yellow-300 text-xs font-medium">
        {from} → {to} ✨
      </span>
    )
  }

  if (item.changes.level) {
    const from = item.changes.level.from as number
    const to = item.changes.level.to as number
    const diff = to - from
    parts.push(
      <span key="lvl" className="text-blue-300 text-xs font-mono">
        Nv.{from}→{to} {diff > 0 ? <span className="text-green-400">+{diff}</span> : <span className="text-red-400">{diff}</span>}
      </span>
    )
  }

  if (item.changes.moves) {
    const { added, removed } = item.changes.moves as { added: string[]; removed: string[] }
    removed.forEach((m) => parts.push(<span key={`-${m}`} className="text-red-400 text-xs">−{m}</span>))
    added.forEach((m) => parts.push(<span key={`+${m}`} className="text-green-400 text-xs">+{m}</span>))
  }

  if (item.changes.nickname) {
    parts.push(
      <span key="nick" className="text-yellow-400 text-xs">
        &ldquo;{item.changes.nickname.to as string}&rdquo;
      </span>
    )
  }

  return <div className="flex flex-wrap gap-1.5 mt-1">{parts}</div>
}

export default function SyncModal({ preview, onConfirm, onCancel, isConfirming }: Props) {
  const relevant = preview.items.filter((i) => i.status !== 'unchanged')

  return (
    <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/70 backdrop-blur-sm" onClick={() => { if (!isConfirming) onCancel() }}>
      <div
        className="w-full md:max-w-lg bg-gray-900 border border-gray-800 rounded-t-3xl md:rounded-2xl flex flex-col max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 pt-6 pb-4 border-b border-gray-800">
          <h2 className="text-lg font-bold text-white">Resultado de sincronización</h2>
          <p className="text-xs text-gray-400 mt-1">{preview.games?.map(id => GAMES.find(g => g.id === id)?.name ?? id).join(' · ')}</p>
          <div className="flex flex-wrap gap-4 mt-2 text-xs">
            <span className="text-green-400">{preview.new_count} nuevos</span>
            <span className="text-blue-400">{preview.updated_count} actualizados</span>
            <span className="text-gray-500">{preview.unchanged_count} sin cambios</span>
            <span className="text-red-400">{preview.removed_count ?? 0} retirados</span>
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
          {relevant.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Sin cambios detectados</p>
          ) : (
            relevant.map((item, i) => (
              <div key={i} className="bg-gray-800 rounded-xl px-4 py-3">
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full shrink-0 ${
                    item.status === 'removed' ? 'text-red-400 bg-red-400/10' : item.status === 'new' ? 'text-green-400 bg-green-400/10' : 'text-blue-400 bg-blue-400/10'
                  }`}>
                    {item.status === 'removed' ? 'RETIRADO' : item.status === 'new' ? 'NUEVO' : 'CAMBIOS'}
                  </span>
                  <span className="font-medium text-sm text-white">
                    {item.pokemon.species_name}{item.pokemon.is_shiny ? ' ✨' : ''}
                    {item.pokemon.nickname !== item.pokemon.species_name && (
                      <span className="text-gray-400 text-xs ml-1">&ldquo;{item.pokemon.nickname}&rdquo;</span>
                    )}
                  </span>
                </div>
                <ChangeSummary item={item} />
                <p className="text-xs text-gray-500 mt-1">{GAMES.find(g => g.id === item.game)?.name}</p>
              </div>
            ))
          )}
        </div>

        {/* Actions */}
        <div className="px-6 pb-6 pt-4 border-t border-gray-800 flex gap-3">
          <button onClick={onCancel} disabled={isConfirming}
            className="flex-1 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium text-sm transition-colors">
            Cancelar
          </button>
          <button onClick={onConfirm} disabled={isConfirming}
            className="flex-1 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 text-white font-semibold text-sm transition-colors">
            {isConfirming ? 'Importando...' : 'Confirmar'}
          </button>
        </div>
      </div>
    </div>
  )
}
