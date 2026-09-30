import { apiClient } from './apiClient'
import type { Role, User } from './types'

export interface RegisterInput {
  full_name: string
  email: string
  password: string
  role: Exclude<Role, 'ADMIN'>
}

export async function register(input: RegisterInput): Promise<User> {
  return (await apiClient.post<User>('/auth/register', input)).data
}

export async function login(email: string, password: string) {
  const { data } = await apiClient.post<{ access_token: string; user: User }>('/auth/login', {
    email,
    password,
  })
  return data
}

export async function getMe(): Promise<User> {
  return (await apiClient.get<User>('/auth/me')).data
}
