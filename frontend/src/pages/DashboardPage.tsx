import { Link } from 'react-router-dom'
import { EmptyState } from '../components/ui/EmptyState'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Loading } from '../components/ui/Loading'
import { StatusBadge } from '../components/ui/Badge'
import { StatCard } from '../components/ui/StatCard'
import { useAuth } from '../context/AuthContext'
import { useAsync } from '../hooks/useAsync'
import { listClaims } from '../services/claimService'
import { getMyItems } from '../services/itemService'

export function DashboardPage() {
  const { user } = useAuth()
  const items = useAsync(getMyItems, [])
  const claims = useAsync(() => listClaims(), [])
  const mine = items.data ?? []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Welcome, {user?.full_name}</h1>
        <p className="text-slate-600">Role: {user?.role}</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <Link to="/report/lost" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">Report Lost Item</Link>
        <Link to="/report/found" className="rounded-lg bg-white px-4 py-2 text-sm font-medium ring-1 ring-slate-300 hover:bg-slate-50">Report Found Item</Link>
        <Link to="/items" className="rounded-lg bg-white px-4 py-2 text-sm font-medium ring-1 ring-slate-300 hover:bg-slate-50">Search Items</Link>
        {user?.role === 'ADMIN' && <Link to="/admin" className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white">Admin Dashboard</Link>}
      </div>

      {items.loading ? <Loading /> : items.error ? <ErrorMessage message={items.error} onRetry={items.reload} /> : (
        <div className="grid gap-4 sm:grid-cols-4">
          <StatCard label="My reports" value={mine.length} />
          <StatCard label="Lost" value={mine.filter((i) => i.type === 'LOST').length} />
          <StatCard label="Found" value={mine.filter((i) => i.type === 'FOUND').length} />
          <StatCard label="Returned" value={mine.filter((i) => i.status === 'RETURNED').length} />
        </div>
      )}

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">My claims</h2>
        {claims.loading && <Loading />}
        {claims.error && <ErrorMessage message={claims.error} onRetry={claims.reload} />}
        {claims.data && claims.data.length === 0 && <EmptyState title="You have not claimed any items" />}
        {claims.data && claims.data.length > 0 && (
          <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
            {claims.data.map((c) => (
              <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
                <Link to={`/items/${c.item_id}`} className="font-medium text-indigo-600 hover:underline">{c.item.title}</Link>
                <span className="flex items-center gap-2">
                  <StatusBadge status={c.status} />
                  {c.review_comment && <span className="text-slate-500">“{c.review_comment}”</span>}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
