import { useState, type FormEvent } from 'react'
import * as claimService from '../services/claimService'
import { toApiError } from '../services/errors'
import { Button } from './ui/Button'
import { Modal } from './ui/Modal'
import { ErrorMessage } from './ui/ErrorMessage'
import { Input, Textarea } from './ui/FormField'

export function ClaimModal({ itemId, onClose, onSubmitted }: { itemId: number; onClose: () => void; onSubmitted: () => void }) {
  const [reason, setReason] = useState('')
  const [lostLocation, setLostLocation] = useState('')
  const [feature, setFeature] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await claimService.submitClaim(itemId, {
        reason,
        lost_location: lostLocation,
        verification_answer: feature,
      })
      onSubmitted()
    } catch (err) {
      setError(toApiError(err).message)
      setBusy(false)
    }
  }

  return (
    <Modal title="Claim this item" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <Textarea label="Why do you believe this is your item?" required minLength={3} value={reason} onChange={(e) => setReason(e.target.value)} />
        <Input label="Where did you lose it?" required minLength={2} value={lostLocation} onChange={(e) => setLostLocation(e.target.value)} />
        <Textarea
          label="Describe an identifying feature"
          hint="Only the admin sees this. Something only the owner would know."
          required
          minLength={3}
          value={feature}
          onChange={(e) => setFeature(e.target.value)}
        />
        {error && <ErrorMessage message={error} />}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={busy}>
            {busy ? 'Submitting…' : 'Submit claim'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
