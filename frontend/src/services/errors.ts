import axios from 'axios'

export class ApiError extends Error {
  readonly status: number | null
  readonly code: string

  constructor(message: string, status: number | null, code: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

/** Normalises any thrown value (axios, network, unknown) into an ApiError. */
export function toApiError(err: unknown): ApiError {
  if (err instanceof ApiError) return err
  if (axios.isAxiosError(err)) {
    if (!err.response) {
      return new ApiError('Cannot reach the server. Check your connection.', null, 'network_error')
    }
    const envelope = err.response.data?.error
    return new ApiError(
      envelope?.message ?? err.message,
      err.response.status,
      envelope?.code ?? 'http_error',
    )
  }
  return new ApiError(err instanceof Error ? err.message : 'Unexpected error', null, 'unknown')
}
