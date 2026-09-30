import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { UNAUTHORIZED_EVENT } from '../services/apiClient'
import * as authService from '../services/authService'
import { tokenStorage } from '../services/tokenStorage'
import type { User } from '../services/types'

interface AuthState {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  register: (input: authService.RegisterInput) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(() => tokenStorage.get() !== null)

  useEffect(() => {
    if (!tokenStorage.get()) return
    authService
      .getMe()
      .then(setUser)
      .catch(() => undefined) // a 401 already clears the token in apiClient; keep it on network errors
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const onUnauthorized = () => setUser(null)
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token, user } = await authService.login(email, password)
    tokenStorage.set(access_token)
    setUser(user)
    return user
  }, [])

  const register = useCallback(async (input: authService.RegisterInput) => {
    await authService.register(input)
    await login(input.email, input.password)
  }, [login])

  const logout = useCallback(() => {
    tokenStorage.clear()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
