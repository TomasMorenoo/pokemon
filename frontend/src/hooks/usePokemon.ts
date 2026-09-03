import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listPokemon, getPokemon, addManualPokemon, getTrainerBag } from '../api/pokemon'
import type { ManualPokemonIn } from '../types/pokemon'
import type { Game } from '../api/drive'

export function usePokemonList() {
  return useQuery({
    queryKey: ['pokemon'],
    queryFn: listPokemon,
  })
}

export function usePokemonDetail(id: number) {
  return useQuery({
    queryKey: ['pokemon', id],
    queryFn: () => getPokemon(id),
  })
}

export function useTrainerBag(game: Game = 'firered') {
  return useQuery({ queryKey: ['trainer-bag', game], queryFn: () => getTrainerBag(game) })
}

export function useAddPokemon() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ManualPokemonIn) => addManualPokemon(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pokemon'] }),
  })
}
