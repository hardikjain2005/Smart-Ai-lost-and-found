import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Modal } from '../components/ui/Modal'
import { PrivateBadge, StatusBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/ui/EmptyState'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Loading } from '../components/ui/Loading'
import { StatCard } from '../components/ui/StatCard'
import { useAsync } from '../hooks/useAsync'
import * as svc from '../services/claimService'
import { toApiError } from '../services/errors'
import { listItems, setItemStatus } from '../services/itemService'
import type { Claim } from '../services/types'

export function AdminPage() {
  const stats = useAsync(svc.getStats, [])
  const pendingItems = useAsync(svc.getPendingItems, [])
  const claims = useAsync(() => svc.listClaims(), [])
  const activity = useAsync(svc.getActivity, [])
  const privateItems = useAsync(() => listItems({ visibility: 'PRIVATE' }, 100), [])
  const [viewing, setViewing] = useState<Claim | null>(null)
  const [comment, setComment] = useState('')
  const [error, setError] = useState<string | null>(null)

  const refresh = () => [stats, pendingItems, claims, activity, privateItems].forEach((x) => x.reload())

  async function run(fn: () => Promise<unknown>) {
    setError(null)
    try {
      await fn()
      setViewing(null)
      setComment('')
      refresh()
    } catch (e) {
      setError(toApiError(e).message)
    }
  }

  const pendingClaims = (claims.data ?? []).filter((c) => c.status === 'PENDING')
  const approved = (claims.data ?? []).filter((c) => c.status === 'APPROVED')
  const s = stats.data

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>
      {error && <ErrorMessage message={error} />}

      {stats.loading && !s ? <Loading /> : stats.error ? <ErrorMessage message={stats.error} onRetry={stats.reload} /> : s && (
        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard label="Total Users" value={s.total_users} />
          <StatCard label="Lost Items" value={s.lost_items} />
          <StatCard label="Found Items" value={s.found_items} />
          <StatCard label="Pending Claims" value={s.pending_claims} />
          <StatCard label="Active Items" value={s.active_items} />
          <StatCard label="Returned Items" value={s.returned_items} />
        </div>
      )}

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Pending Reports</h2>
        {pendingItems.loading && !pendingItems.data && <Loading />}
        {pendingItems.data?.length === 0 && <EmptyState title="No reports awaiting review" />}
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white empty:hidden">
          {pendingItems.data?.map((i) => (
            <li key={i.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
              <span>
                <Link to={`/items/${i.id}`} className="font-medium text-indigo-600 hover:underline">{i.title}</Link>{' '}
                {i.visibility === 'PRIVATE' && <PrivateBadge />}{' '}
                <span className="text-slate-500">{i.type} · {i.location} · by {i.reporter_name}</span>
              </span>
              <span className="flex gap-2">
                <Button onClick={() => run(() => svc.setApproval(i.id, 'APPROVED'))}>Approve</Button>
                <Button variant="secondary" onClick={() => run(() => svc.setApproval(i.id, 'REJECTED'))}>Reject</Button>
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Private Reports</h2>
        {privateItems.data?.items.length === 0 && <EmptyState title="No private reports" />}
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white empty:hidden">
          {privateItems.data?.items.map((i) => (
            <li key={i.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
              <span>
                <Link to={`/items/${i.id}`} className="font-medium text-indigo-600 hover:underline">{i.title}</Link>{' '}
                <PrivateBadge />{' '}
                <span className="text-slate-500">{i.type} · {i.location} · by {i.reporter_name}</span>
              </span>
              <StatusBadge status={i.status} />
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Pending Claims</h2>
        {claims.loading && !claims.data && <Loading />}
        {claims.error && <ErrorMessage message={claims.error} onRetry={claims.reload} />}
        {claims.data && pendingClaims.length === 0 && <EmptyState title="No pending claims" />}
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white empty:hidden">
          {pendingClaims.map((c) => (
            <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
              <span><strong>{c.claimant.full_name}</strong> claims <strong>{c.item.title}</strong></span>
              <Button onClick={() => setViewing(c)}>View claim</Button>
            </li>
          ))}
        </ul>
        {approved.length > 0 && (
          <>
            <h3 className="pt-2 text-sm font-semibold text-slate-700">Approved — awaiting return</h3>
            <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
              {approved.map((c) => (
                <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
                  <span><strong>{c.claimant.full_name}</strong> · {c.item.title}</span>
                  <Button onClick={() => run(() => setItemStatus(c.item_id, 'RETURNED'))}>Mark Returned</Button>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Recent Activity</h2>
        {activity.data?.length === 0 && <EmptyState title="No activity yet" />}
        <ul className="space-y-1 text-sm text-slate-700">
          {activity.data?.map((a, idx) => (
            <li key={idx}>
              <Link to={`/items/${a.item_id}`} className="hover:underline">{a.message}</Link>{' '}
              <span className="text-slate-400">{new Date(a.at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </section>

      {viewing && (
        <Modal title={`Claim #${viewing.id}: ${viewing.item.title}`} onClose={() => setViewing(null)}>
          <div className="space-y-3 text-sm">
            <p><span className="text-slate-500">Claimant:</span> {viewing.claimant.full_name} ({viewing.claimant.email})</p>
            <p><span className="text-slate-500">Why it is theirs:</span> {viewing.reason}</p>
            <p><span className="text-slate-500">Lost at:</span> {viewing.lost_location}</p>
            <div className="rounded-lg bg-blue-50 p-3">
              <p className="font-medium text-blue-800">Identifying feature they described</p>
              <p>{viewing.verification_answer}</p>
            </div>
            <div className="rounded-lg bg-amber-50 p-3">
              <p className="font-medium text-amber-800">🔒 Private details on the found item report</p>
              <p>{viewing.item.private_details ?? 'None recorded'}</p>
            </div>
            <div className="flex items-center gap-2"><StatusBadge status={viewing.status} /></div>
            <label className="block">
              <span className="text-slate-500">Review comment</span>
              <input value={comment} onChange={(e) => setComment(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
            </label>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => run(() => svc.updateClaimStatus(viewing.id, 'REJECTED', comment || undefined))}>Reject</Button>
              <Button onClick={() => run(() => svc.updateClaimStatus(viewing.id, 'APPROVED', comment || undefined))}>Approve</Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
