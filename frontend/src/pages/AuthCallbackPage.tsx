import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { handleGoogleCallback } from '../api/auth'

export default function AuthCallbackPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get('code')
    if (!code) {
      navigate('/login')
      return
    }
    handleGoogleCallback(code)
      .then(({ access_token }) => {
        localStorage.setItem('access_token', access_token)
        navigate('/', { replace: true })
      })
      .catch(() => navigate('/login'))
  }, [navigate])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-gray-400 animate-pulse">Autenticando...</div>
    </div>
  )
}
