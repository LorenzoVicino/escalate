import { useState, type FormEvent } from 'react'
import type { TicketInput } from '../types'
import { CloseIcon } from './Icons'

interface Props {
  onClose: () => void
  onSubmit: (ticket: TicketInput) => Promise<void>
}

export function TicketForm({ onClose, onSubmit }: Props) {
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    const form = new FormData(event.currentTarget)
    try {
      await onSubmit({
        title: String(form.get('title')),
        description: String(form.get('description')),
        customerName: String(form.get('customerName')),
        source: form.get('source') as 'WEB' | 'API',
      })
    } catch {
      setError('The ticket could not be created. Check that the API is running.')
      setSubmitting(false)
    }
  }

  return <div className="modal-backdrop" role="presentation">
    <section className="modal" role="dialog" aria-modal="true" aria-labelledby="new-ticket-title">
      <div className="modal-head">
        <div><span className="eyebrow">INTAKE</span><h2 id="new-ticket-title">Create a support ticket</h2></div>
        <button className="icon-button" onClick={onClose} aria-label="Close"><CloseIcon /></button>
      </div>
      <form onSubmit={submit}>
        <label>Customer<input name="customerName" placeholder="Acme Mobility" required /></label>
        <div className="form-grid">
          <label>Source<select name="source" defaultValue="WEB"><option>WEB</option><option>API</option></select></label>
          <label>Title<input name="title" placeholder="Brief issue summary" minLength={3} required /></label>
        </div>
        <label>Description<textarea name="description" placeholder="What is happening, who is affected, and since when?" minLength={5} rows={6} required /></label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button primary" disabled={submitting}>{submitting ? 'Analyzing…' : 'Create & analyze'}</button></div>
      </form>
    </section>
  </div>
}

