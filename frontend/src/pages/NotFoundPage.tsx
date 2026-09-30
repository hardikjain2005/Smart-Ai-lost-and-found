import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-bold">Page not found</h1>
      <Link to="/" className="text-indigo-600 underline">
        Back to home
      </Link>
    </div>
  )
}
