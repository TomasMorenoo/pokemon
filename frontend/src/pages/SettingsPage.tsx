import { useState, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { GAMES, getDriveConfig, setDriveConfig, type DriveConfig } from '../api/drive'

function GameSaveSection({ game }: { game: typeof GAMES[number] }) {
  const queryClient = useQueryClient()
  const [config, setConfig] = useState<DriveConfig | null>(null)
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getDriveConfig(game.id)
      .then((value) => { if (active) setConfig(value) })
      .catch(() => { if (active) setError('No se pudo cargar la partida. Recargá la página para reintentar.') })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [game.id])

  async function handleSave(event: React.FormEvent) {
    event.preventDefault()
    if (!url.trim() || saving) return
    setSaving(true)
    setSaved(false)
    setError('')
    try {
      await setDriveConfig(url.trim(), `${game.id}.sav`, game.id)
      setConfig(await getDriveConfig(game.id))
      await queryClient.invalidateQueries({ queryKey: ['drive-configs'] })
      setSaved(true)
      setUrl('')
    } catch {
      setError('No se pudo guardar el enlace. Intentá nuevamente.')
    } finally {
      setSaving(false)
    }
  }

  const savedUrl = config?.file_id
    ? `https://drive.google.com/file/d/${encodeURIComponent(config.file_id)}/view`
    : null

  return (
    <section aria-labelledby={`title-${game.id}`} className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-3">
        <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: game.color }} />
        <h2 id={`title-${game.id}`} className="font-semibold text-white">Pokémon {game.name}</h2>
      </div>
      {loading ? (
        <p className="text-sm text-gray-400" role="status">Cargando partida...</p>
      ) : savedUrl ? (
        <div className="bg-green-400/5 border border-green-400/20 rounded-xl px-4 py-3">
          <p className="text-sm font-medium text-green-400">✓ Archivo configurado</p>
          <a href={savedUrl} target="_blank" rel="noopener noreferrer" className="text-xs font-mono text-gray-400 hover:text-gray-200 break-all">
            {savedUrl}
          </a>
        </div>
      ) : (
        <p className="text-sm text-gray-500 bg-gray-800 rounded-xl px-4 py-3">Sin archivo configurado</p>
      )}
      <form onSubmit={handleSave} className="space-y-3">
        <label htmlFor={`save-${game.id}`} className="block text-xs font-medium text-gray-400">Archivo .sav · Google Drive</label>
        <input
          id={`save-${game.id}`}
          value={url}
          onChange={(event) => { setUrl(event.target.value); setSaved(false) }}
          disabled={loading || saving}
          placeholder="https://drive.google.com/file/d/..."
          className="w-full bg-gray-800 border border-gray-700 focus:border-blue-500 text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none transition-colors placeholder-gray-600"
        />
        <button
          type="submit"
          disabled={loading || saving || !url.trim()}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-semibold py-2.5 rounded-xl text-sm transition-colors"
        >
          {saving ? 'Guardando...' : saved ? '✓ Guardado' : config ? 'Actualizar enlace' : 'Guardar enlace'}
        </button>
      </form>
      {saved && <p role="status" className="text-xs text-green-400">Enlace de {game.name} guardado.</p>}
      {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
    </section>
  )
}

export default function SettingsPage() {
  return (
    <div className="max-w-3xl space-y-6">
      <div className="space-y-2">
        <h1 className="text-xl font-bold text-white">Ajustes</h1>
        <h2 className="text-sm font-semibold text-gray-300">Tus partidas · Generación III</h2>
        <p className="text-sm text-gray-400">Guardá un archivo .sav independiente para cada juego.</p>
        <p className="text-xs text-gray-500 leading-relaxed">
          Compartí cada archivo en Google Drive con la opción «Cualquier persona con el enlace» y pegá su enlace en el juego correspondiente.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {GAMES.map((game) => <GameSaveSection key={game.id} game={game} />)}
      </div>
    </div>
  )
}
