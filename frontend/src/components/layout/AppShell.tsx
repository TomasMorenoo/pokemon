import { Outlet, Link, useLocation } from 'react-router-dom'
import { HomeIcon, PlusIcon, Cog6ToothIcon, SwordsIcon } from './Icons'
import { Pokeball } from '../ui/Pokeball'

const NAV = [
  { to: '/', icon: <HomeIcon />, label: 'Pokédex' },
  { to: '/add', icon: <PlusIcon />, label: 'Agregar' },
  { to: '/combat', icon: <SwordsIcon />, label: 'Combate' },
  { to: '/settings', icon: <Cog6ToothIcon />, label: 'Ajustes' },
]

export default function AppShell() {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen bg-gray-950 flex">
      {/* Sidebar — desktop */}
      <aside className="hidden md:flex flex-col w-60 shrink-0 bg-gray-900 border-r border-gray-800 fixed inset-y-0 left-0 z-20">
        <div className="px-6 py-6 border-b border-gray-800">
          <span className="text-yellow-400 font-extrabold text-xl tracking-tight flex items-center gap-2">
            <Pokeball className="w-5 h-5" colored /> Pokédex
          </span>
        </div>
        <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
          {NAV.map(({ to, icon, label }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                (pathname === to || (to === '/' && (pathname === '/collection' || pathname.startsWith('/pokemon/'))))
                  ? 'bg-yellow-400/10 text-yellow-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <span className="w-5 h-5 shrink-0">{icon}</span>
              {label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Content */}
      <main className="flex-1 md:ml-60 min-h-screen pb-20 md:pb-0 overflow-x-hidden">
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-6">
          <Outlet />
        </div>
      </main>

      {/* Bottom nav — mobile */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 bg-gray-900 border-t border-gray-800 flex z-20">
        {NAV.map(({ to, icon, label }) => (
          <Link
            key={to}
            to={to}
            className={`flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium transition-colors ${
              (pathname === to || (to === '/' && (pathname === '/collection' || pathname.startsWith('/pokemon/')))) ? 'text-yellow-400' : 'text-gray-500'
            }`}
          >
            <span className="w-5 h-5">{icon}</span>
            {label}
          </Link>
        ))}
      </nav>
    </div>
  )
}
