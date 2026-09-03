import { apiClient } from './client'
import type { Pokemon, ManualPokemonIn } from '../types/pokemon'
import type { Game } from './drive'

export async function listPokemon(): Promise<Pokemon[]> {
  const { data } = await apiClient.get<Pokemon[]>('/pokemon/')
  return data
}

export async function getPokemon(id: number): Promise<Pokemon> {
  const { data } = await apiClient.get<Pokemon>(`/pokemon/${id}`)
  return data
}

export async function addManualPokemon(body: ManualPokemonIn): Promise<Pokemon> {
  const { data } = await apiClient.post<Pokemon>('/pokemon/', body)
  return data
}

export async function getTrainerBag(game: Game = 'firered'): Promise<{ tms: string[] }> {
  const { data } = await apiClient.get<{ tms: string[] }>('/bag/', { params: { game } })
  return data
}
