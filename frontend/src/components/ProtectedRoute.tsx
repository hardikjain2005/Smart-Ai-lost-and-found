import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { Role } from '../services/types'
import { Spinner } from './ui/Spinner'

export function ProtectedRoute({ role }: { role?: Role }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />
  if (role && user.role !== role) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
