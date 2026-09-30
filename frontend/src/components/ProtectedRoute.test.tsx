import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi } from 'vitest'
import { ProtectedRoute } from './ProtectedRoute'
import type { Role } from '../services/types'

let mockUser: { role: Role } | null = null
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: mockUser, loading: false }),
}))

function renderAt(path: string, role?: Role) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<p>login page</p>} />
        <Route path="/dashboard" element={<p>dashboard page</p>} />
        <Route element={<ProtectedRoute role={role} />}>
          <Route path="/secret" element={<p>secret page</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

test('anonymous users are sent to login', () => {
  mockUser = null
  renderAt('/secret')
  expect(screen.getByText('login page')).toBeInTheDocument()
})

test('signed-in users see the page', () => {
  mockUser = { role: 'STUDENT' }
  renderAt('/secret')
  expect(screen.getByText('secret page')).toBeInTheDocument()
})

test('non-admins are kept out of admin routes', () => {
  mockUser = { role: 'STUDENT' }
  renderAt('/secret', 'ADMIN')
  expect(screen.getByText('dashboard page')).toBeInTheDocument()
})

test('admins can enter admin routes', () => {
  mockUser = { role: 'ADMIN' }
  renderAt('/secret', 'ADMIN')
  expect(screen.getByText('secret page')).toBeInTheDocument()
})
