import { useState } from 'react'

export function pokemonSpriteUrl(speciesId: number, shiny = false) {
  return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${shiny ? 'shiny/' : ''}${speciesId}.png`
}

export default function PokemonSprite({ speciesId, shiny = false, name, className = '' }: {
  speciesId: number; shiny?: boolean; name: string; className?: string
}) {
  const src = pokemonSpriteUrl(speciesId, shiny)
  const [failed, setFailed] = useState('')
  return failed === src ? (
    <span className={className} role="img" aria-label={`${name}: imagen no disponible`}>?</span>
  ) : (
    <img src={src} alt={`${name}${shiny ? ' shiny' : ''}`} loading="lazy" className={className}
      style={{ imageRendering: 'pixelated' }} onError={() => setFailed(src)} />
  )
}
