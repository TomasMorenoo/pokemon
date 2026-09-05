import { describe, expect, it } from 'vitest'
import type { Pokemon } from '../types/pokemon'
import { orderByRegionalDex } from './collectionOrder'

function pokemon(id: number, speciesId: number): Pokemon {
  return {
    id,
    species_id: speciesId,
    species_name: `Pokemon ${speciesId}`,
    nickname: null,
    current_level: 5,
    nature_name: null,
    gender: null,
    is_shiny: false,
    ot_name: null,
    ot_id: 1,
    origin: 'save',
    game: 'firered',
    added_via: 'sync',
    party_slot: null,
    first_seen_at: '2026-01-01T00:00:00Z',
    latest_measurement: null,
    measurements: [],
  }
}

describe('orderByRegionalDex', () => {
  it('keeps one specimen in regional order and sends duplicates to the end', () => {
    const rows = orderByRegionalDex([pokemon(1, 16), pokemon(2, 1), pokemon(3, 16)], 'firered', false)
    expect(rows.map(row => row.kind === 'pokemon' ? row.pokemon.species_id : row.speciesId)).toEqual([1, 16, 16])
    expect(rows[rows.length - 1]).toMatchObject({ kind: 'pokemon', repeated: true })
  })

  it('adds named dex slots for missing species', () => {
    const rows = orderByRegionalDex([pokemon(1, 1)], 'leafgreen', true)
    expect(rows).toHaveLength(151)
    expect(rows[1]).toEqual({ kind: 'missing', speciesId: 2, regionalNumber: 2 })
  })

  it('uses the Hoenn order for generation three Hoenn games', () => {
    const rows = orderByRegionalDex([pokemon(1, 63), pokemon(2, 252)], 'emerald', false)
    expect(rows.map(row => row.kind === 'pokemon' ? row.pokemon.species_id : row.speciesId)).toEqual([252, 63])
    expect(rows[0]).toMatchObject({ regionalNumber: 1 })
    expect(rows[1]).toMatchObject({ regionalNumber: 39 })
  })
})
