import type { TimelineStep } from '../services/types'

export function Timeline({ steps }: { steps: TimelineStep[] }) {
  return (
    <ol className="space-y-2" aria-label="Item timeline">
      {steps.map((s) => (
        <li key={s.key} className={`flex items-center gap-2 text-sm ${s.done ? 'text-slate-900' : 'text-slate-400'}`}>
          <span
            className={`flex h-5 w-5 items-center justify-center rounded-full text-xs ${s.done ? 'bg-emerald-500 text-white' : 'bg-slate-200'}`}
          >
            {s.done ? '✓' : ''}
          </span>
          {s.label}
        </li>
      ))}
    </ol>
  )
}
