export interface IVSet {
  hp: number
  attack: number
  defense: number
  speed: number
  sp_attack: number
  sp_defense: number
  source: 'save' | 'calculated' | 'manual' | 'unknown'
}

export interface EVSet {
  hp: number
  attack: number
  defense: number
  speed: number
  sp_attack: number
  sp_defense: number
  source: 'save' | 'calculated' | 'manual' | 'unknown'
}

export interface MoveSlot {
  move_id: number
  move_name: string
  pp: number
  pp_max: number
}

export interface Measurement {
  id: number
  level: number | null
  experience: number | null
  nickname: string | null
  hp: number | null
  attack: number | null
  defense: number | null
  speed: number | null
  sp_attack: number | null
  sp_defense: number | null
  ivs: IVSet | null
  evs: EVSet | null
  moves: MoveSlot[] | null
  item_name: string | null
  data_source: string
  recorded_at: string
}

export interface Pokemon {
  id: number
  species_id: number
  species_name: string
  nickname: string | null
  current_level: number | null
  nature_name: string | null
  gender: string | null
  is_shiny: boolean
  ot_name: string | null
  ot_id: number
  origin: string
  game: string | null
  added_via: string
  party_slot: number | null
  first_seen_at: string
  latest_measurement: Measurement | null
  measurements: Measurement[]
}

export interface SyncPreview {
  sync_session_id: number
  new_count: number
  updated_count: number
  unchanged_count: number
  items: SyncDiffItem[]
}

export interface SyncDiffItem {
  status: 'new' | 'updated' | 'unchanged'
  pokemon: {
    species_name: string
    species_id: number
    nickname: string
    level: number
    nature_name: string
    gender: string
    is_shiny: boolean
    pid: number
    ot_id: number
  }
  changes: Record<string, { from: unknown; to: unknown }> | null
}

export interface SyncResult {
  sync_session_id: number
  status: string
  new_count: number
  updated_count: number
  unchanged_count: number
  completed_at: string | null
}

export interface User {
  id: number
  email: string
  name: string
  picture_url: string | null
}

export interface ManualPokemonIn {
  species_id: number
  species_name: string
  nickname?: string
  level: number
  nature_name?: string
  gender?: string
  origin?: string
  hp?: number
  attack?: number
  defense?: number
  speed?: number
  sp_attack?: number
  sp_defense?: number
  iv_hp?: number
  iv_attack?: number
  iv_defense?: number
  iv_speed?: number
  iv_sp_attack?: number
  iv_sp_defense?: number
  ev_hp?: number
  ev_attack?: number
  ev_defense?: number
  ev_speed?: number
  ev_sp_attack?: number
  ev_sp_defense?: number
  moves?: MoveSlot[]
  item_name?: string
}
