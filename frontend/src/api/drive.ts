import { apiClient } from './client'

export interface DriveFile {
  id: string
  name: string
  modifiedTime: string
}

export interface DriveConfig {
  file_id: string
  file_name: string
  folder_id: string | null
  last_drive_modified: string | null
}

export async function getDriveConfig(): Promise<DriveConfig | null> {
  const { data } = await apiClient.get<DriveConfig | null>('/drive/config')
  return data
}

export async function setDriveConfig(urlOrId: string, fileName: string): Promise<void> {
  await apiClient.post('/drive/config', { url_or_id: urlOrId, file_name: fileName })
}
