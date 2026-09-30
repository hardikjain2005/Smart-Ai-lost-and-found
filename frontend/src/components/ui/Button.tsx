import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'secondary'

const styles: Record<Variant, string> = {
  primary: 'bg-indigo-600 text-white hover:bg-indigo-700',
  secondary: 'bg-white text-slate-800 ring-1 ring-slate-300 hover:bg-slate-50',
}

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
}

export function Button({ variant = 'primary', className = '', ...rest }: Props) {
  return (
    <button
      className={`rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 ${styles[variant]} ${className}`}
      {...rest}
    />
  )
}
