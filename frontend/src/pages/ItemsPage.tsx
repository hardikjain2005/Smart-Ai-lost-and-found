import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ItemGrid } from '../components/ItemCard'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/ui/EmptyState'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Input, Select } from '../components/ui/FormField'
import { Loading } from '../components/ui/Loading'
import { useAsync } from '../hooks/useAsync'
import { getMeta, listItems } from '../services/itemService'
import type { ItemFilters } from '../services/types'

const KEYS = ['q', 'type', 'category', 'location', 'date'] as const

export function ItemsPage() {
  const [params, setParams] = useSearchParams()
  const filters: ItemFilters = Object.fromEntries(KEYS.map((k) => [k, params.get(k) ?? '']))
  const [qDraft, setQDraft] = useState(filters.q ?? '')
  const [meta, setMeta] = useState<{ categories: string[]; locations: string[] }>({ categories: [], locations: [] })

  useEffect(() => {
    getMeta().then(setMeta).catch(() => undefined)
  }, [])
  useEffect(() => setQDraft(params.get('q') ?? ''), [params])

  const key = params.toString()
  const result = useAsync(() => listItems(filters), [key])

  function update(k: string, v: string) {
    const next = new URLSearchParams(params)
    if (v) next.set(k, v)
    else next.delete(k)
    setParams(next)
  }
  const hasFilters = KEYS.some((k) => params.get(k))

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Browse Items</h1>
      <form
        role="search"
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          update('q', qDraft.trim())
        }}
      >
        <input
          aria-label="Search items"
          value={qDraft}
          onChange={(e) => setQDraft(e.target.value)}
          placeholder="Search by name, brand, color, description…"
          className="flex-1 rounded-lg border border-slate-300 px-4 py-2 focus:border-indigo-500 focus:outline-none"
        />
        <Button type="submit">Search</Button>
      </form>
      <div className="grid gap-4 sm:grid-cols-5">
        <Select label="Lost / Found" value={filters.type} onChange={(e) => update('type', e.target.value)} options={['LOST', 'FOUND']} placeholder="All" />
        <Select label="Category" value={filters.category} onChange={(e) => update('category', e.target.value)} options={meta.categories} placeholder="All categories" />
        <Select label="Location" value={filters.location} onChange={(e) => update('location', e.target.value)} options={meta.locations} placeholder="All locations" />
        <Input label="Date" type="date" value={filters.date} onChange={(e) => update('date', e.target.value)} />
        <div className="flex items-end">
          <Button variant="secondary" disabled={!hasFilters} onClick={() => setParams({})}>
            Clear filters
          </Button>
        </div>
      </div>

      {result.loading && <Loading text="Searching…" />}
      {result.error && <ErrorMessage message={result.error} onRetry={result.reload} />}
      {!result.loading && result.data && (
        <>
          <p className="text-sm text-slate-500">{result.data.total} item(s) found</p>
          {result.data.items.length === 0 ? (
            <EmptyState title="No items match your search">Try removing a filter.</EmptyState>
          ) : (
            <ItemGrid items={result.data.items} />
          )}
        </>
      )}
    </div>
  )
}
