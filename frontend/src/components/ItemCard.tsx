import { Link } from 'react-router-dom'
import { assetUrl } from '../services/apiClient'
import type { Item } from '../services/types'
import { PrivateBadge, StatusBadge, TypeBadge } from './ui/Badge'

export function ItemCard({ item }: { item: Item }) {
  const img = assetUrl(item.image_url)
  return (
    <article className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      {img ? (
        <img src={img} alt={item.title} className="h-40 w-full object-cover" />
      ) : (
        <div className="flex h-40 items-center justify-center bg-slate-100 text-sm text-slate-400">No image</div>
      )}
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-center justify-between gap-2">
          <span className="flex items-center gap-1">
            <TypeBadge type={item.type} />
            {item.visibility === 'PRIVATE' && <PrivateBadge />}
          </span>
          <StatusBadge status={item.status} />
        </div>
        <h3 className="font-semibold text-slate-900">{item.title}</h3>
        <p className="text-sm text-slate-600">{item.category}</p>
        <p className="text-sm text-slate-500">
          {item.location} · {item.date}
        </p>
        <Link to={`/items/${item.id}`} className="mt-auto text-sm font-medium text-indigo-600 hover:underline">
          View Details
        </Link>
      </div>
    </article>
  )
}

export function ItemGrid({ items }: { items: Item[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((i) => (
        <ItemCard key={i.id} item={i} />
      ))}
    </div>
  )
}
