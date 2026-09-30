const KEY = 'campusfind.token'

export const tokenStorage = {
  get: (): string | null => {
    try {
      return localStorage.getItem(KEY)
    } catch {
      return null
    }
  },
  set: (t: string) => {
    try {
      localStorage.setItem(KEY, t)
    } catch {
      /* storage unavailable */
    }
  },
  clear: () => {
    try {
      localStorage.removeItem(KEY)
    } catch {
      /* storage unavailable */
    }
  },
}
