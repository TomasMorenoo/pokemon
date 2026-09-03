import type { IVSet } from '../../types/pokemon'

export function ivTotal(ivs: IVSet): number {
  return ivs.hp + ivs.attack + ivs.defense + ivs.speed + ivs.sp_attack + ivs.sp_defense
}

export function ivStars(ivs: IVSet): number {
  const total = ivTotal(ivs)
  if (total === 186) return 4
  if (total >= 140) return 3
  if (total >= 93) return 2
  if (total >= 47) return 1
  return 0
}

const COLORS = ['text-gray-600', 'text-red-400', 'text-orange-400', 'text-yellow-300', 'text-yellow-300']

export function IVStars({ ivs, size = 'sm' }: { ivs: IVSet | null; size?: 'sm' | 'md' }) {
  if (!ivs) return null
  const stars = ivStars(ivs)
  const cls = size === 'md' ? 'text-base' : 'text-xs'
  return (
    <span title={`${ivTotal(ivs)}/186`} className={`${cls} ${COLORS[stars]} tracking-tight cursor-default`}>
      {'★'.repeat(stars)}{'☆'.repeat(4 - stars)}
    </span>
  )
}
