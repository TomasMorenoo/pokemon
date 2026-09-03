import { apiClient } from './client'
import type { SyncPreview, SyncResult } from '../types/pokemon'

export async function syncPreview(): Promise<SyncPreview> {
  const { data } = await apiClient.post<SyncPreview>('/sync/preview')
  return data
}

export async function syncConfirm(syncSessionId: number): Promise<SyncResult> {
  const { data } = await apiClient.post<SyncResult>('/sync/confirm', {
    sync_session_id: syncSessionId,
  })
  return data
}
