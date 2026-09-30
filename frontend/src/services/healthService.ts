import { apiClient } from './apiClient'

export interface HealthStatus {
  status: string
  app: string
  environment: string
  database: string
}

export async function getHealth(): Promise<HealthStatus> {
  const { data } = await apiClient.get<HealthStatus>('/health')
  return data
}
