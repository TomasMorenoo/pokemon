import { useQuery } from '@tanstack/react-query'
import { getMe } from '../api/auth'

export function useAuth() {
  const token = localStorage.getItem('access_token')
  return useQuery({
    queryKey: ['me'],
    queryFn: getMe,
    enabled: !!token,
    retry: false,
  })
}
