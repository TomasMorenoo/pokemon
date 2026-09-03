import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listPokemon, getPokemon, addManualPokemon, getTrainerBag } from '../api/pokemon'
import type { ManualPokemonIn } from '../types/pokemon'

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

export function useTrainerBag() {
  return useQuery({ queryKey: ['trainer-bag'], queryFn: getTrainerBag })
}

export function useAddPokemon() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ManualPokemonIn) => addManualPokemon(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pokemon'] }),
  })
}
