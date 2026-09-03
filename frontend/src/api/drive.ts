import { apiClient } from './client'

export const GAMES = [
  { id: 'firered', name: 'Rojo Fuego', color: '#f87171' },
  { id: 'leafgreen', name: 'Verde Hoja', color: '#a3e635' },
  { id: 'emerald', name: 'Esmeralda', color: '#34d399' },
  { id: 'ruby', name: 'Rubí', color: '#fb7185' },
  { id: 'sapphire', name: 'Zafiro', color: '#60a5fa' },
] as const

export type Game = typeof GAMES[number]['id']

export interface DriveFile {
  id: string
  name: string
  modifiedTime: string
}

export interface DriveConfig {
  game: Game
  synced_at: string | null
  file_id: string
  file_name: string
  folder_id: string | null
  last_drive_modified: string | null
}

export async function getDriveConfigs(): Promise<DriveConfig[]> {
  const { data } = await apiClient.get<DriveConfig[]>('/drive/configs')
  return data
}

export async function getDriveConfig(game: Game = 'firered'): Promise<DriveConfig | null> {
  const { data } = await apiClient.get<DriveConfig | null>('/drive/config', { params: { game } })
  return data
}

export async function setDriveConfig(urlOrId: string, fileName: string, game: Game = 'firered'): Promise<void> {
  await apiClient.post('/drive/config', { url_or_id: urlOrId, file_name: fileName, game })
}
