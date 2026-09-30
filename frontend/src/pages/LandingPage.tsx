import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiStatus } from '../components/ApiStatus'
import { ItemGrid } from '../components/ItemCard'
import { EmptyState } from '../components/ui/EmptyState'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Loading } from '../components/ui/Loading'
import { useAsync } from '../hooks/useAsync'
import { listItems } from '../services/itemService'

export function LandingPage() {
  const [q, setQ] = useState('')
  const navigate = useNavigate()
  const recent = useAsync(() => listItems({}, 6), [])

  function search(e: FormEvent) {
    e.preventDefault()
    navigate(q.trim() ? `/items?q=${encodeURIComponent(q.trim())}` : '/items')
  }

  return (
    <div className="space-y-12">
      <section className="space-y-5">
        <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">Smart Campus Lost &amp; Found</p>
        <h1 className="text-4xl font-bold tracking-tight">Lost something on campus?</h1>
        <p className="max-w-2xl text-lg text-slate-600">
          Report lost and found items, get smart match suggestions, and recover what is yours.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to="/report/lost" className="rounded-lg bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700">
            Report Lost Item
          </Link>
          <Link to="/report/found" className="rounded-lg bg-white px-5 py-2.5 font-medium text-slate-800 ring-1 ring-slate-300 hover:bg-slate-50">
            Report Found Item
          </Link>
        </div>
        <form onSubmit={search} className="flex max-w-xl gap-2" role="search">
          <input
            aria-label="Search items"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search for an item, e.g. laptop"
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 focus:border-indigo-500 focus:outline-none"
          />
          <button className="rounded-lg bg-slate-900 px-5 font-medium text-white hover:bg-slate-700">Search</button>
        </form>
        <ApiStatus />
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Recently reported</h2>
        {recent.loading && <Loading />}
        {recent.error && <ErrorMessage message={recent.error} onRetry={recent.reload} />}
        {recent.data && recent.data.items.length === 0 && <EmptyState title="No items reported yet" />}
        {recent.data && recent.data.items.length > 0 && <ItemGrid items={recent.data.items} />}
      </section>
    </div>
  )
}
