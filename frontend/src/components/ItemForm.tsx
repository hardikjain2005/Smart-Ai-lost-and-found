import { useEffect, useState, type FormEvent } from 'react'
import { assetUrl } from '../services/apiClient'
import { toApiError } from '../services/errors'
import { getMeta, uploadImage } from '../services/itemService'
import type { ItemInput, ItemType, Visibility } from '../services/types'
import { Button } from './ui/Button'
import { ErrorMessage } from './ui/ErrorMessage'
import { Input, Select, Textarea } from './ui/FormField'

const MAX_MB = 15
const today = () => new Date().toISOString().slice(0, 10)

export function ItemForm({
  initial, submitLabel, onSubmit,
}: {
  initial?: Partial<ItemInput> & { type: ItemType }
  submitLabel: string
  onSubmit: (input: ItemInput) => Promise<void>
}) {
  const [meta, setMeta] = useState<{ categories: string[]; locations: string[] } | null>(null)
  const [form, setForm] = useState<ItemInput>({
    title: '', type: initial?.type ?? 'LOST', category: '', brand: '', color: '', description: '',
    location: '', date: today(), time: '', image_url: '', private_details: '', visibility: 'PUBLIC', ...initial,
    // nulls from the API become empty strings for controlled inputs
  })
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    getMeta().then(setMeta).catch((e) => setError(toApiError(e).message))
  }, [])

  const set = <K extends keyof ItemInput>(k: K, v: ItemInput[K]) => setForm((f) => ({ ...f, [k]: v }))

  function pickFile(f: File | null) {
    setError(null)
    if (f && !['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
      setError('Image must be JPEG, PNG or WEBP')
      return
    }
    if (f && f.size > MAX_MB * 1024 * 1024) {
      setError(`Image must be smaller than ${MAX_MB} MB`)
      return
    }
    setFile(f)
  }

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const image_url = file ? await uploadImage(file) : form.image_url
      const clean = Object.fromEntries(
        Object.entries({ ...form, image_url }).map(([k, v]) => [k, v === '' ? undefined : v]),
      ) as unknown as ItemInput
      await onSubmit(clean)
    } catch (err) {
      setError(toApiError(err).message)
      setBusy(false)
    }
  }

  const preview = file ? URL.createObjectURL(file) : assetUrl(form.image_url)

  return (
    <form onSubmit={submit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <Input label="Item name" required minLength={2} maxLength={120} value={form.title} onChange={(e) => set('title', e.target.value)} placeholder="e.g. Black Dell Laptop" />
      <div className="grid gap-4 sm:grid-cols-2">
        <Select label="Lost / Found" value={form.type} onChange={(e) => set('type', e.target.value as ItemType)} options={['LOST', 'FOUND']} />
        <Select label="Category" required value={form.category} onChange={(e) => set('category', e.target.value)} options={meta?.categories ?? []} placeholder="Select category" />
        <Input label="Brand" value={form.brand} onChange={(e) => set('brand', e.target.value)} />
        <Input label="Color" value={form.color} onChange={(e) => set('color', e.target.value)} />
        <Select label="Campus location" required value={form.location} onChange={(e) => set('location', e.target.value)} options={meta?.locations ?? []} placeholder="Select location" />
        <div className="grid grid-cols-2 gap-2">
          <Input label="Date" type="date" required max={today()} value={form.date} onChange={(e) => set('date', e.target.value)} />
          <Input label="Time" type="time" value={form.time} onChange={(e) => set('time', e.target.value)} />
        </div>
      </div>
      <Textarea label="Description" maxLength={2000} value={form.description} onChange={(e) => set('description', e.target.value)} />
      <Textarea
        label="Private identifying details"
        hint="Never shown publicly. Only you and campus admins can see this, and it is used to verify ownership."
        maxLength={2000}
        value={form.private_details}
        onChange={(e) => set('private_details', e.target.value)}
        placeholder="e.g. small scratch near the logo, sticker, hidden marking"
      />
      <fieldset className="space-y-2">
        <legend className="text-sm font-medium text-slate-700">Visibility</legend>
        {(['PUBLIC', 'PRIVATE'] as Visibility[]).map((v) => (
          <label key={v} className="flex items-center gap-2 text-sm text-slate-800">
            <input
              type="radio"
              name="visibility"
              value={v}
              checked={form.visibility === v}
              onChange={() => set('visibility', v)}
            />
            {v === 'PUBLIC' ? 'Public' : 'Private / Sensitive'}
          </label>
        ))}
        <p className="text-xs text-slate-500">
          Private reports are not shown in public listings or search. They remain accessible to the reporter and
          authorized administrators.
        </p>
      </fieldset>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">
          Image (JPEG, PNG or WEBP, max {MAX_MB} MB)
          <input type="file" accept="image/jpeg,image/png,image/webp" className="mt-1 block text-sm" onChange={(e) => pickFile(e.target.files?.[0] ?? null)} />
        </label>
        {preview && <img src={preview} alt="Preview" className="h-32 rounded-lg object-cover" />}
      </div>
      {error && <ErrorMessage message={error} />}
      <Button type="submit" disabled={busy || !meta}>
        {busy ? 'Saving…' : submitLabel}
      </Button>
    </form>
  )
}
