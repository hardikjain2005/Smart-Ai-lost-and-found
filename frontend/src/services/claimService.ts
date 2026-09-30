import { apiClient } from './apiClient'
import type { ActivityEntry, AdminStats, ApprovalStatus, Claim, ClaimInput, ClaimStatus, Item } from './types'

export const submitClaim = async (itemId: number, input: ClaimInput) =>
  (await apiClient.post<Claim>(`/items/${itemId}/claim`, input)).data

export const listClaims = async (status?: ClaimStatus) =>
  (await apiClient.get<Claim[]>('/claims', { params: status ? { status } : {} })).data

export const updateClaimStatus = async (id: number, status: ClaimStatus, review_comment?: string) =>
  (await apiClient.patch<Claim>(`/claims/${id}/status`, { status, review_comment })).data

export const getStats = async () => (await apiClient.get<AdminStats>('/admin/stats')).data
export const getPendingItems = async () => (await apiClient.get<Item[]>('/admin/pending-items')).data
export const getActivity = async () => (await apiClient.get<ActivityEntry[]>('/admin/activity')).data
export const setApproval = async (id: number, approval_status: ApprovalStatus) =>
  (await apiClient.patch<Item>(`/admin/items/${id}/approval`, { approval_status })).data
