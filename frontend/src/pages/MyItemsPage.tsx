import { Link } from 'react-router-dom'
import { ItemCard } from '../components/ItemCard'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/ui/EmptyState'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Loading } from '../components/ui/Loading'
import { useAsync } from '../hooks/useAsync'
import { deleteItem, getMyItems } from '../services/itemService'
import { toApiError } from '../services/errors'
import { useState } from 'react'

export function MyItemsPage() {
  const items = useAsync(getMyItems, [])
  const [error, setError] = useState<string | null>(null)

  async function remove(id: number) {
    if (!window.confirm('Delete this report?')) return
    try {
      await deleteItem(id)
      items.reload()
    } catch (e) {
      setError(toApiError(e).message)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">My Items</h1>
      {error && <ErrorMessage message={error} />}
      {items.loading && <Loading />}
      {items.error && <ErrorMessage message={items.error} onRetry={items.reload} />}
      {items.data && items.data.length === 0 && (
        <EmptyState title="You have not reported anything yet">
          <Link to="/report/lost" className="text-indigo-600 underline">Report a lost item</Link> or{' '}
          <Link to="/report/found" className="text-indigo-600 underline">a found item</Link>.
        </EmptyState>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.data?.map((i) => (
          <div key={i.id} className="space-y-2">
            <ItemCard item={i} />
            <div className="flex gap-2">
              <Link to={`/items/${i.id}/edit`} className="rounded-lg px-3 py-1.5 text-sm ring-1 ring-slate-300 hover:bg-slate-50">Edit</Link>
              <Button variant="secondary" onClick={() => remove(i.id)}>Delete</Button>
              {i.approval_status !== 'APPROVED' && (
                <span className="self-center text-xs text-slate-500">Review: {i.approval_status}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
