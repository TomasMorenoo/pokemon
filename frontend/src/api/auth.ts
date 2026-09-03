import { apiClient } from './client'
import type { User } from '../types/pokemon'

export async function getGoogleAuthUrl(): Promise<string> {
  const { data } = await apiClient.get<{ url: string }>('/auth/google/url')
  return data.url
}

export async function handleGoogleCallback(code: string): Promise<{ access_token: string; user: User }> {
  const { data } = await apiClient.get<{ access_token: string; user: User }>(
    `/auth/google/callback?code=${code}`
  )
  return data
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me')
  return data
}
