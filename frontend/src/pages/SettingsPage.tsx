import { useState, useEffect } from 'react'
import { getDriveConfig, setDriveConfig, type DriveConfig } from '../api/drive'

export default function SettingsPage() {
  const [driveConfig, setDriveConfigState] = useState<DriveConfig | null>(null)
  const [url, setUrl] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getDriveConfig().then(setDriveConfigState).catch(() => null)
  }, [])

  async function handleSave() {
    if (!url.trim()) return
    setSaving(true)
    try {
      await setDriveConfig(url.trim(), 'partida.sav')
      const updated = await getDriveConfig()
      setDriveConfigState(updated)
      setSaved(true)
      setUrl('')
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  const savedUrl = driveConfig?.file_id
    ? `https://drive.google.com/file/d/${driveConfig.file_id}/view`
    : null

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-xl font-bold text-white">Ajustes</h1>

      <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Archivo .sav · Google Drive</h2>

        {savedUrl ? (
          <div className="flex items-start gap-3 bg-green-400/5 border border-green-400/20 rounded-xl px-4 py-3">
            <span className="text-green-400 mt-0.5 text-sm">✓</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-green-400">Configurado</p>
              <a
                href={savedUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-mono text-gray-400 hover:text-gray-200 break-all transition-colors"
              >
                {savedUrl}
              </a>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-gray-500 bg-gray-800 rounded-xl px-4 py-3">
            <span>—</span>
            <span>Sin archivo configurado</span>
          </div>
        )}

        <p className="text-xs text-gray-500 leading-relaxed">
          Compartí el archivo .sav con <span className="text-gray-300">"Cualquier persona con el enlace"</span> en Google Drive y pegá el link acá.
        </p>

        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://drive.google.com/file/d/..."
          className="w-full bg-gray-800 border border-gray-700 focus:border-blue-500 text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none transition-colors placeholder-gray-600"
        />

        <button
          onClick={handleSave}
          disabled={saving || !url.trim()}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-semibold py-2.5 rounded-xl text-sm transition-colors"
        >
          {saving ? 'Guardando...' : saved ? '✓ Guardado' : 'Guardar link'}
        </button>
      </section>
    </div>
  )
}
