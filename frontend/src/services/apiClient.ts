import axios from 'axios'
import { env } from '../config/env'
import { toApiError } from './errors'
import { tokenStorage } from './tokenStorage'

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 10_000,
})

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Fired when the server rejects our token so the auth context can log the user out. */
export const UNAUTHORIZED_EVENT = 'campusfind:unauthorized'

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError = toApiError(error)
    const isLogin = error?.config?.url?.includes('/auth/login')
    if (apiError.status === 401 && !isLogin && tokenStorage.get()) {
      tokenStorage.clear()
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }
    return Promise.reject(apiError)
  },
)

/** Backend origin (API base without the /api suffix) — used for uploaded image URLs. */
const backendOrigin = env.apiBaseUrl.replace(/\/api\/?$/, '')
export const assetUrl = (path: string | null | undefined) =>
  path ? (path.startsWith('http') ? path : `${backendOrigin}${path}`) : null
