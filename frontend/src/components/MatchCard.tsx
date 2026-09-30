import { Link } from 'react-router-dom'
import { assetUrl } from '../services/apiClient'
import type { Match } from '../services/types'

export function MatchCard({ match }: { match: Match }) {
  const img = assetUrl(match.item.image_url)
  return (
    <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
      <p className="text-sm font-semibold text-indigo-700">🤖 Potential Match</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{match.match_score}% MATCH SCORE</p>
      {img && <img src={img} alt={match.item.title} className="mt-2 h-28 w-full rounded-lg object-cover" />}
      <p className="mt-2 font-medium text-slate-800">{match.item.title}</p>
      <p className="text-xs text-slate-500">
        {match.item.type} · {match.item.location} · {match.item.date}
      </p>
      <ul className="mt-2 space-y-0.5 text-sm text-slate-700">
        {match.matching_attributes.map((a) => (
          <li key={a}>✓ {a.charAt(0).toUpperCase() + a.slice(1)}</li>
        ))}
      </ul>
      <p className="mt-2 text-sm text-slate-600">{match.explanation}</p>
      <Link to={`/items/${match.item.id}`} className="mt-3 inline-block text-sm font-medium text-indigo-600 hover:underline">
        View Match
      </Link>
    </div>
  )
}
