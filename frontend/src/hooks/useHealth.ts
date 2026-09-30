import { useEffect, useState } from 'react'
import { getHealth, type HealthStatus } from '../services/healthService'
import { toApiError } from '../services/errors'

type State =
  | { phase: 'loading' }
  | { phase: 'ok'; data: HealthStatus }
  | { phase: 'error'; message: string }

export function useHealth(): State & { retry: () => void } {
  const [state, setState] = useState<State>({ phase: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    getHealth()
      .then((data) => !cancelled && setState({ phase: 'ok', data }))
      .catch((e) => !cancelled && setState({ phase: 'error', message: toApiError(e).message }))
    return () => {
      cancelled = true
    }
  }, [attempt])

  return {
    ...state,
    retry: () => {
      setState({ phase: 'loading' })
      setAttempt((n) => n + 1)
    },
  }
}
