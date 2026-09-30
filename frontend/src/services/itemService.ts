import { apiClient } from './apiClient'
import type { Item, ItemDetail, ItemFilters, ItemInput, ItemStatus, Match } from './types'

export async function listItems(filters: ItemFilters = {}, limit = 50) {
  const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v))
  const { data } = await apiClient.get<{ items: Item[]; total: number }>('/items', {
    params: { ...params, limit },
  })
  return data
}

export const getItem = async (id: number | string) =>
  (await apiClient.get<ItemDetail>(`/items/${id}`)).data

export const createItem = async (input: ItemInput) => (await apiClient.post<Item>('/items', input)).data

export const updateItem = async (id: number, input: ItemInput) =>
  (await apiClient.put<Item>(`/items/${id}`, input)).data

export const deleteItem = async (id: number) => {
  await apiClient.delete(`/items/${id}`)
}

export const setItemStatus = async (id: number, status: ItemStatus) =>
  (await apiClient.patch<Item>(`/items/${id}/status`, { status })).data

export const getMyItems = async () => (await apiClient.get<Item[]>('/users/me/items')).data

export const getMatches = async (id: number | string) =>
  (await apiClient.get<Match[]>(`/items/${id}/matches`)).data

export const getMeta = async () =>
  (await apiClient.get<{ categories: string[]; locations: string[] }>('/meta')).data

export async function uploadImage(file: File): Promise<string> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<{ image_url: string }>('/uploads', form)
  return data.image_url
}
