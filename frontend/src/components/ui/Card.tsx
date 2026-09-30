import type { ReactNode } from 'react'

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      {title && <h3 className="mb-2 text-lg font-semibold text-slate-900">{title}</h3>}
      {children}
    </div>
  )
}
