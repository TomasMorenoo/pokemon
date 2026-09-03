import { useMutation, useQueryClient } from '@tanstack/react-query'
import { syncPreview, syncConfirm } from '../api/sync'

export function useSyncPreview() {
  return useMutation({ mutationFn: syncPreview })
}

export function useSyncConfirm() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: syncConfirm,
    onSuccess: async () => {
      await Promise.all([
        qc.invalidateQueries({ queryKey: ['pokemon'] }),
        qc.invalidateQueries({ queryKey: ['trainer-bag'] }),
        qc.invalidateQueries({ queryKey: ['drive-configs'] }),
      ])
    },
  })
}
