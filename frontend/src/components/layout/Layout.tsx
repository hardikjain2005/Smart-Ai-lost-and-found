import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../ui/Button'

const link = ({ isActive }: { isActive: boolean }) =>
  `text-sm font-medium ${isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'}`

export function Layout() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-6 py-4">
          <Link to="/" className="mr-auto text-lg font-bold text-indigo-600">
            CampusFind AI
          </Link>
          <NavLink to="/items" className={link}>Browse Items</NavLink>
          {user && (
            <>
              <NavLink to="/report/lost" className={link}>Report Lost</NavLink>
              <NavLink to="/report/found" className={link}>Report Found</NavLink>
              <NavLink to="/my-items" className={link}>My Items</NavLink>
              <NavLink to="/dashboard" className={link}>Dashboard</NavLink>
              {user.role === 'ADMIN' && <NavLink to="/admin" className={link}>Admin</NavLink>}
              <span className="text-sm text-slate-500">{user.full_name}</span>
              <Button
                variant="secondary"
                onClick={() => {
                  logout()
                  navigate('/login')
                }}
              >
                Logout
              </Button>
            </>
          )}
          {!user && !loading && (
            <>
              <NavLink to="/login" className={link}>Login</NavLink>
              <Link to="/register" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
                Register
              </Link>
            </>
          )}
        </nav>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-500">
        CampusFind AI — Smart Campus Lost &amp; Found
      </footer>
    </div>
  )
}
