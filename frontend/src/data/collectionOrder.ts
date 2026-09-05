import type { Pokemon } from '../types/pokemon'
import { GEN3_NAMES, regionalDex } from './regionalDex'

export type CollectionRow =
  | { kind: 'pokemon'; pokemon: Pokemon; regionalNumber: number | null; repeated: boolean }
  | { kind: 'missing'; speciesId: number; regionalNumber: number }

export function orderByRegionalDex(collection: Pokemon[], game: string, includeMissing: boolean, ascending = true): CollectionRow[] {
  const dex = [...regionalDex(game)]
  const regionalNumber = new Map(dex.map((speciesId, index) => [speciesId, index + 1]))
  const bySpecies = new Map<number, Pokemon[]>()
  for (const pokemon of collection) {
    const instances = bySpecies.get(pokemon.species_id) ?? []
    instances.push(pokemon)
    bySpecies.set(pokemon.species_id, instances)
  }

  const primary: CollectionRow[] = []
  for (const speciesId of dex) {
    const instances = bySpecies.get(speciesId)
    if (instances?.length) primary.push({ kind: 'pokemon', pokemon: instances.shift()!, regionalNumber: regionalNumber.get(speciesId)!, repeated: false })
    else if (includeMissing) primary.push({ kind: 'missing', speciesId, regionalNumber: regionalNumber.get(speciesId)! })
  }

  const outsideDex = [...bySpecies.entries()]
    .filter(([speciesId, instances]) => !regionalNumber.has(speciesId) && instances.length)
    .sort(([a], [b]) => a - b)
  for (const [, instances] of outsideDex) {
    primary.push({ kind: 'pokemon', pokemon: instances.shift()!, regionalNumber: null, repeated: false })
  }

  const repeated = [...bySpecies.entries()]
    .flatMap(([speciesId, instances]) => instances.map(pokemon => ({ kind: 'pokemon' as const, pokemon, regionalNumber: regionalNumber.get(speciesId) ?? null, repeated: true })))
    .sort((a, b) => (a.regionalNumber ?? a.pokemon.species_id) - (b.regionalNumber ?? b.pokemon.species_id) || a.pokemon.id - b.pokemon.id)

  if (!ascending) {
    primary.reverse()
    repeated.reverse()
  }
  return [...primary, ...repeated]
}

export function collectionRowName(row: CollectionRow) {
  return row.kind === 'pokemon' ? row.pokemon.species_name : GEN3_NAMES[row.speciesId] ?? ''
}
