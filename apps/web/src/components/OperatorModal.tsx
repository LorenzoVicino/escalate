import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Operator } from '../hooks/useOperator'
import type { Owner } from '../types'
import { CloseIcon, UserIcon } from './Icons'

const displayName = (owner: Owner) =>
  [owner.firstName, owner.lastName].filter(Boolean).join(' ') || owner.email || owner.id

export function OperatorModal(
  { current, onSelect, onClose }:
  { current: Operator | null; onSelect: (operator: Operator) => void; onClose: () => void },
) {
  const [owners, setOwners] = useState<Owner[]>([])
  const [selected, setSelected] = useState(current?.id ?? '')
  const [state, setState] = useState<'loading' | 'ready' | 'unavailable'>('loading')

  useEffect(() => {
    api.listOwners()
      .then(result => { setOwners(result); setState(result.length ? 'ready' : 'unavailable') })
      .catch(() => setState('unavailable'))
  }, [])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape' && current) onClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [current, onClose])

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    if (state === 'ready') {
      const owner = owners.find(candidate => candidate.id === selected)
      if (!owner) return
      onSelect({ id: owner.id, name: displayName(owner), email: owner.email })
      return
    }
    const name = String(form.get('name') ?? '').trim()
    if (!name) return
    onSelect({ id: '', name, email: null })
  }

  return <div className="modal-backdrop">
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="operator-title">
      <div className="modal-head">
        <div><span className="eyebrow">WHO IS ON TRIAGE</span><h2 id="operator-title">Identify yourself</h2></div>
        {current && <button className="icon-button" onClick={onClose} aria-label="Close"><CloseIcon /></button>}
      </div>
      <form onSubmit={submit}>
        <p className="modal-intro">Escalate tags your session so you can filter the queue down to the tickets you own in HubSpot.</p>
        {state === 'loading' && <p className="modal-intro">Loading HubSpot users…</p>}
        {state === 'ready' && <label>HubSpot user
          <select name="owner" value={selected} onChange={event => setSelected(event.target.value)} autoFocus>
            <option value="" disabled>Select your name…</option>
            {owners.map(owner => <option key={owner.id} value={owner.id}>{displayName(owner)}{owner.email ? ` — ${owner.email}` : ''}</option>)}
          </select>
        </label>}
        {state === 'unavailable' && <>
          <div className="form-error">HubSpot users are unavailable — the private app may be missing the owners scope. Enter your name instead.</div>
          <label>Name and surname<input name="name" defaultValue={current?.name ?? ''} placeholder="Lorenzo Vicino" autoFocus /></label>
        </>}
        <div className="modal-actions">
          {current && <button type="button" className="button secondary" onClick={onClose}>Cancel</button>}
          <button type="submit" className="button primary" disabled={state === 'loading' || (state === 'ready' && !selected)}><UserIcon /> Continue</button>
        </div>
      </form>
    </div>
  </div>
}
