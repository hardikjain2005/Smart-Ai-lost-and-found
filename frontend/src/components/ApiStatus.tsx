import { useHealth } from '../hooks/useHealth'
import { Spinner } from './ui/Spinner'
import { ErrorMessage } from './ui/ErrorMessage'

export function ApiStatus() {
  const health = useHealth()

  if (health.phase === 'loading') {
    return (
      <p className="flex items-center gap-2 text-sm text-slate-600">
        <Spinner /> Checking server…
      </p>
    )
  }
  if (health.phase === 'error') {
    return <ErrorMessage message={health.message} onRetry={health.retry} />
  }
  return (
    <p className="text-sm text-emerald-700">
      Server {health.data.status} · database {health.data.database} · {health.data.environment}
    </p>
  )
}
