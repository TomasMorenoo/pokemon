import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import GameCollections from './GameCollections'
import PokemonSprite from './PokemonSprite'
import { GAMES } from '../../api/drive'

describe('partidas sincronizadas', () => {
  it('muestra seis opciones para cinco juegos, incluso con una colección vacía', () => {
    const html = renderToStaticMarkup(<MemoryRouter><GameCollections games={GAMES.map(g => g.id)} pokemon={[]} /></MemoryRouter>)
    expect(html.match(/<a /g)).toHaveLength(6)
    for (const game of GAMES) expect(html).toContain(`/games/${game.id}.png`)
    expect(html).toContain('href="/collection"')
    expect(html).toContain('Todo')
  })

  it('no muestra carátulas de juegos todavía sin sincronizar', () => {
    const html = renderToStaticMarkup(<MemoryRouter><GameCollections games={['firered']} pokemon={[]} /></MemoryRouter>)
    expect(html.match(/<a /g)).toHaveLength(2)
    expect(html).not.toContain('/games/emerald.png')
  })
})

describe('sprites de Pokémon', () => {
  it('descarga la variante shiny únicamente para Pokémon shiny', () => {
    const shiny = renderToStaticMarkup(<PokemonSprite speciesId={6} shiny name="Charizard" />)
    const normal = renderToStaticMarkup(<PokemonSprite speciesId={6} name="Charizard" />)
    expect(shiny).toContain('/pokemon/shiny/6.png')
    expect(shiny).toContain('alt="Charizard shiny"')
    expect(normal).toContain('/pokemon/6.png')
    expect(normal).not.toContain('/shiny/')
  })
})
