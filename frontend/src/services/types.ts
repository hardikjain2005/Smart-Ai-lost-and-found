export type Role = 'STUDENT' | 'FACULTY' | 'STAFF' | 'ADMIN'
export type ItemType = 'LOST' | 'FOUND'
export type ItemStatus = 'ACTIVE' | 'MATCHED' | 'CLAIMED' | 'RETURNED' | 'CLOSED'
export type Visibility = 'PUBLIC' | 'PRIVATE'
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED'
export type ClaimStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'COMPLETED'

export interface User {
  id: number
  full_name: string
  email: string
  role: Role
  is_active: boolean
  created_at: string
}

export interface Item {
  id: number
  title: string
  type: ItemType
  category: string
  brand: string | null
  color: string | null
  description: string | null
  location: string
  date: string
  time: string | null
  image_url: string | null
  private_details: string | null
  status: ItemStatus
  approval_status: ApprovalStatus
  visibility: Visibility
  reported_by: number
  reporter_name: string
  created_at: string
  updated_at: string
}

export interface TimelineStep {
  key: string
  label: string
  done: boolean
}

export interface ItemDetail extends Item {
  timeline: TimelineStep[]
}

/** Payload for creating/updating an item. */
export interface ItemInput {
  title: string
  type: ItemType
  category: string
  brand?: string
  color?: string
  description?: string
  location: string
  date: string
  time?: string
  image_url?: string
  private_details?: string
  visibility?: Visibility
}

export interface ItemFilters {
  q?: string
  type?: ItemType | ''
  category?: string
  location?: string
  brand?: string
  color?: string
  date?: string
  status?: ItemStatus | ''
  visibility?: Visibility | ''
}

export interface Match {
  match_score: number
  matching_attributes: string[]
  explanation: string
  item: Item
}

export interface Claim {
  id: number
  item_id: number
  claimant_id: number
  reason: string
  lost_location: string | null
  verification_answer: string
  status: ClaimStatus
  review_comment: string | null
  created_at: string
  updated_at: string
  item: Pick<Item, 'id' | 'title' | 'type' | 'status' | 'location' | 'image_url' | 'private_details'>
  claimant: { id: number; full_name: string; email: string }
}

export interface ClaimInput {
  reason: string
  lost_location: string
  verification_answer: string
}

export interface AdminStats {
  total_users: number
  lost_items: number
  found_items: number
  pending_claims: number
  active_items: number
  returned_items: number
  pending_reports: number
}

export interface ActivityEntry {
  kind: 'report' | 'claim'
  message: string
  item_id: number
  at: string
}
