import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'

const control =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
      {hint && <span className="block text-xs text-slate-500">{hint}</span>}
    </label>
  )
}

interface Common {
  label: string
  hint?: string
}

export function Input({ label, hint, ...rest }: Common & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <Field label={label} hint={hint}>
      <input className={control} {...rest} />
    </Field>
  )
}

export function Textarea({ label, hint, ...rest }: Common & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <Field label={label} hint={hint}>
      <textarea rows={3} className={control} {...rest} />
    </Field>
  )
}

export function Select({
  label, hint, options, placeholder, ...rest
}: Common & SelectHTMLAttributes<HTMLSelectElement> & { options: string[]; placeholder?: string }) {
  return (
    <Field label={label} hint={hint}>
      <select className={control} {...rest}>
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </Field>
  )
}
