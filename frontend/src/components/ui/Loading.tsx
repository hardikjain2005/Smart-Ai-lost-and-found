import { Spinner } from './Spinner'

export function Loading({ text = 'Loading…' }: { text?: string }) {
  return (
    <p className="flex items-center gap-2 py-8 text-sm text-slate-600">
      <Spinner /> {text}
    </p>
  )
}
