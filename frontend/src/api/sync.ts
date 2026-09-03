import { apiClient } from './client'
import type { SyncPreview, SyncResult } from '../types/pokemon'

export async function syncPreview(): Promise<SyncPreview> {
  const { data } = await apiClient.post<{ previews: SyncPreview[] }>('/sync/preview-all')
  return {
    sync_session_id: data.previews[0].sync_session_id,
    sync_session_ids: data.previews.map(p => p.sync_session_id),
    games: data.previews.map(p => p.game ?? 'firered'),
    new_count: data.previews.reduce((n, p) => n + p.new_count, 0),
    updated_count: data.previews.reduce((n, p) => n + p.updated_count, 0),
    unchanged_count: data.previews.reduce((n, p) => n + p.unchanged_count, 0),
    removed_count: data.previews.reduce((n, p) => n + p.removed_count, 0),
    items: data.previews.flatMap(p => p.items),
  }
}

export async function syncConfirm(syncSessionIds: number[]): Promise<SyncResult[]> {
  const { data } = await apiClient.post<SyncResult[]>('/sync/confirm-all', {
    sync_session_ids: syncSessionIds,
  })
  return data
}
