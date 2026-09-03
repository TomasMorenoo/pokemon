import { useMutation, useQueryClient } from '@tanstack/react-query'
import { syncPreview, syncConfirm } from '../api/sync'

export function useSyncPreview() {
  return useMutation({ mutationFn: syncPreview })
}

export function useSyncConfirm() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: syncConfirm,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pokemon'] }),
  })
}
