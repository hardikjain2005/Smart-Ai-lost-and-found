import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Input, Select } from '../components/ui/FormField'
import { useAuth } from '../context/AuthContext'
import { toApiError } from '../services/errors'
import type { Role } from '../services/types'

export function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<Exclude<Role, 'ADMIN'>>('STUDENT')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/dashboard" replace />

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await register({ full_name: fullName, email, password, role })
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(toApiError(err).message)
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm space-y-4">
      <h1 className="text-2xl font-bold">Create account</h1>
      <form onSubmit={submit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <Input label="Full name" required minLength={2} value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <Input label="Email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input label="Password" type="password" required minLength={8} maxLength={64} hint="At least 8 characters" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <Select label="I am a" value={role} onChange={(e) => setRole(e.target.value as Exclude<Role, 'ADMIN'>)} options={['STUDENT', 'FACULTY', 'STAFF']} />
        {error && <ErrorMessage message={error} />}
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? 'Creating…' : 'Register'}
        </Button>
      </form>
      <p className="text-sm text-slate-600">
        Already registered? <Link to="/login" className="text-indigo-600 underline">Log in</Link>
      </p>
    </div>
  )
}
