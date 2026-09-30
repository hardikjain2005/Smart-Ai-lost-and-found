import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ClaimModal } from '../components/ClaimModal'
import { MatchCard } from '../components/MatchCard'
import { Timeline } from '../components/Timeline'
import { PrivateBadge, StatusBadge, TypeBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Loading } from '../components/ui/Loading'
import { useAuth } from '../context/AuthContext'
import { useAsync } from '../hooks/useAsync'
import { assetUrl } from '../services/apiClient'
import { toApiError } from '../services/errors'
import { listClaims } from '../services/claimService'
import { deleteItem, getItem, getMatches } from '../services/itemService'

export function ItemDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const item = useAsync(() => getItem(id!), [id])
  const matches = useAsync(() => (user ? getMatches(id!) : Promise.resolve([])), [id, user?.id])
  const myClaims = useAsync(() => (user ? listClaims() : Promise.resolve([])), [user?.id, id])
  const [claiming, setClaiming] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  if (item.loading) return <Loading />
  if (item.error || !item.data) return <ErrorMessage message={item.error ?? 'Item not found'} />
  const i = item.data
  const isOwner = user?.id === i.reported_by
  const isAdmin = user?.role === 'ADMIN'
  const hasOpenClaim = (myClaims.data ?? []).some(
    (c) => c.item_id === i.id && c.claimant_id === user?.id && (c.status === 'PENDING' || c.status === 'APPROVED'),
  )
  const canClaim =
    !!user && !isOwner && !hasOpenClaim && i.type === 'FOUND' && (i.status === 'ACTIVE' || i.status === 'MATCHED')
  const img = assetUrl(i.image_url)

  async function remove() {
    if (!window.confirm('Delete this report?')) return
    try {
      await deleteItem(i.id)
      navigate('/my-items')
    } catch (e) {
      setError(toApiError(e).message)
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-3">
      <div className="space-y-6 lg:col-span-2">
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          {img ? <img src={img} alt={i.title} className="max-h-96 w-full object-cover" /> : (
            <div className="flex h-48 items-center justify-center bg-slate-100 text-slate-400">No image</div>
          )}
          <div className="space-y-4 p-6">
            <div className="flex items-center gap-2">
              <TypeBadge type={i.type} />
              <StatusBadge status={i.status} />
              {i.visibility === 'PRIVATE' && <PrivateBadge />}
              {i.approval_status !== 'APPROVED' && <StatusBadge status={i.approval_status} />}
            </div>
            <h1 className="text-2xl font-bold">{i.title}</h1>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              {[['Category', i.category], ['Brand', i.brand], ['Color', i.color], ['Location', i.location],
                ['Date', i.date], ['Time', i.time?.slice(0, 5)], ['Reported by', i.reporter_name]].map(([k, v]) =>
                v ? (
                  <div key={k}>
                    <dt className="text-slate-500">{k}</dt>
                    <dd className="font-medium">{v}</dd>
                  </div>
                ) : null,
              )}
            </dl>
            {i.description && <p className="text-slate-700">{i.description}</p>}
            {i.private_details && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm">
                <p className="font-medium text-amber-800">🔒 Private details (visible only to you and admins)</p>
                <p className="mt-1 text-amber-900">{i.private_details}</p>
              </div>
            )}
            {notice && <p role="status" className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
            {error && <ErrorMessage message={error} />}
            <div className="flex flex-wrap gap-2">
              {hasOpenClaim && <span className="self-center text-sm text-slate-600">You have an open claim on this item.</span>}
              {canClaim && <Button onClick={() => setClaiming(true)}>This is my item</Button>}
              {!user && i.type === 'FOUND' && (
                <Link to="/login" state={{ from: `/items/${i.id}` }} className="text-sm text-indigo-600 underline">Log in to claim this item</Link>
              )}
              {(isOwner || isAdmin) && (
                <>
                  <Link to={`/items/${i.id}/edit`} className="rounded-lg px-4 py-2 text-sm font-medium ring-1 ring-slate-300 hover:bg-slate-50">Edit</Link>
                  <Button variant="secondary" onClick={remove}>Delete</Button>
                </>
              )}
              {isAdmin && <Link to="/admin" className="rounded-lg px-4 py-2 text-sm font-medium ring-1 ring-slate-300 hover:bg-slate-50">Admin panel</Link>}
            </div>
          </div>
        </div>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">
            {i.type === 'LOST' ? 'Possible found items' : 'Possible lost reports'}
          </h2>
          {!user && <p className="text-sm text-slate-500"><Link to="/login" state={{ from: `/items/${i.id}` }} className="text-indigo-600 underline">Log in</Link> to see smart match suggestions.</p>}
          {user && matches.loading && <Loading text="Finding matches…" />}
          {user && matches.error && <ErrorMessage message={matches.error} onRetry={matches.reload} />}
          {user && matches.data && matches.data.length === 0 && <p className="text-sm text-slate-500">No potential matches found yet.</p>}
          <div className="grid gap-4 sm:grid-cols-2">
            {matches.data?.map((m) => <MatchCard key={m.item.id} match={m} />)}
          </div>
        </section>
      </div>

      <aside className="space-y-3">
        <h2 className="text-lg font-semibold">Progress</h2>
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <Timeline steps={i.timeline} />
        </div>
      </aside>

      {claiming && (
        <ClaimModal
          itemId={i.id}
          onClose={() => setClaiming(false)}
          onSubmitted={() => {
            setClaiming(false)
            setNotice('Claim submitted. An admin will review it.')
            item.reload()
            myClaims.reload()
          }}
        />
      )}
    </div>
  )
}
