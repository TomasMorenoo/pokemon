export function Pokeball({ className = 'w-3 h-3', colored = false }: { className?: string; colored?: boolean }) {
  if (colored) {
    return (
      <svg viewBox="0 0 24 24" className={className}>
        <path d="M 2 12 A 10 10 0 0 1 22 12 Z" fill="#EF4444" />
        <path d="M 2 12 A 10 10 0 0 0 22 12 Z" fill="#ffffff" />
        <circle cx="12" cy="12" r="10" fill="none" stroke="#1f2937" strokeWidth="1.5" />
        <path d="M2 12h20" stroke="#1f2937" strokeWidth="1.5" />
        <circle cx="12" cy="12" r="3.5" fill="#ffffff" stroke="#1f2937" strokeWidth="1.5" />
        <circle cx="12" cy="12" r="1.5" fill="#1f2937" />
      </svg>
    )
  }
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <circle cx="12" cy="12" r="3" fill="white" stroke="currentColor" strokeWidth="2" />
    </svg>
  )
}
