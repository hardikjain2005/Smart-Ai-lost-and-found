import type { ClaimStatus, ItemStatus, ItemType } from '../../services/types'

const base = 'inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold'

export function TypeBadge({ type }: { type: ItemType }) {
  const c = type === 'LOST' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
  return <span className={`${base} ${c}`}>{type}</span>
}

export function PrivateBadge() {
  return <span className={`${base} bg-slate-800 text-white`}>🔒 PRIVATE</span>
}

const statusColors: Record<string, string> = {
  ACTIVE: 'bg-blue-100 text-blue-700',
  MATCHED: 'bg-amber-100 text-amber-800',
  CLAIMED: 'bg-purple-100 text-purple-700',
  RETURNED: 'bg-emerald-100 text-emerald-700',
  CLOSED: 'bg-slate-200 text-slate-700',
  PENDING: 'bg-amber-100 text-amber-800',
  APPROVED: 'bg-emerald-100 text-emerald-700',
  REJECTED: 'bg-red-100 text-red-700',
  COMPLETED: 'bg-emerald-100 text-emerald-700',
}

export function StatusBadge({ status }: { status: ItemStatus | ClaimStatus | string }) {
  return <span className={`${base} ${statusColors[status] ?? 'bg-slate-100 text-slate-700'}`}>{status}</span>
}
