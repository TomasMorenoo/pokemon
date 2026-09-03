import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import PokemonDetailPage from './pages/PokemonDetailPage'
import AddPokemonPage from './pages/AddPokemonPage'
import SettingsPage from './pages/SettingsPage'
import CombatPage from './pages/CombatPage'
import AppShell from './components/layout/AppShell'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<HomePage showGames />} />
        <Route path="collection" element={<HomePage />} />
        <Route path="pokemon/:id" element={<PokemonDetailPage />} />
        <Route path="add" element={<AddPokemonPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="combat" element={<CombatPage />} />
      </Route>
    </Routes>
  )
}
