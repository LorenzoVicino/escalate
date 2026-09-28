import { useEffect, useState } from 'react'
import { useDebounced } from '../hooks/useDebounced'
import type { TicketFilters } from '../types'
import { SearchIcon, UserIcon } from './Icons'

const STATUSES = ['OPEN', 'ROUTED', 'WAITING_CONFIRMATION', 'MANUAL_TRIAGE', 'RESOLVED']
const TIERS = ['L1', 'L2', 'L3', 'ENGINEERING']
const TEAMS = [
  'SUPPORT', 'BACKEND', 'FRONTEND', 'DEVOPS', 'DATABASE',
  'SECURITY', 'MOBILE', 'PLATFORM', 'MIDDLEWARE', 'GTSAT', 'INGESTION', 'UNKNOWN',
]

const pretty = (value: string) => value.replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase())

export function FilterBar(
  { filters, onChange, ownerId }:
  { filters: TicketFilters; onChange: (filters: TicketFilters) => void; ownerId: string | null },
) {
  const [text, setText] = useState(filters.q ?? '')
  const debounced = useDebounced(text)

  useEffect(() => {
    if ((filters.q ?? '') !== debounced) onChange({ ...filters, q: debounced || undefined })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced])

  const set = (patch: Partial<TicketFilters>) => onChange({ ...filters, ...patch })
  const mine = Boolean(ownerId && filters.ownerId === ownerId)
  const active = Boolean(filters.q || filters.status || filters.team || filters.tier || filters.ownerId)

  return <div className="filter-bar">
    <div className="filter-search">
      <SearchIcon />
      <input value={text} onChange={event => setText(event.target.value)} placeholder="Search title, description or customer…" aria-label="Search tickets" />
    </div>
    <select value={filters.status ?? ''} onChange={e => set({ status: e.target.value || undefined })} aria-label="Filter by status">
      <option value="">All statuses</option>
      {STATUSES.map(value => <option key={value} value={value}>{pretty(value)}</option>)}
    </select>
    <select value={filters.tier ?? ''} onChange={e => set({ tier: e.target.value || undefined })} aria-label="Filter by tier">
      <option value="">All tiers</option>
      {TIERS.map(value => <option key={value} value={value}>{pretty(value)}</option>)}
    </select>
    <select value={filters.team ?? ''} onChange={e => set({ team: e.target.value || undefined })} aria-label="Filter by team">
      <option value="">All teams</option>
      {TEAMS.map(value => <option key={value} value={value}>{pretty(value)}</option>)}
    </select>
    {ownerId && <button type="button" className={`filter-toggle${mine ? ' on' : ''}`} aria-pressed={mine} onClick={() => set({ ownerId: mine ? undefined : ownerId })}><UserIcon width={14} height={14} /> My tickets</button>}
    {active && <button type="button" className="filter-clear" onClick={() => { setText(''); onChange({}) }}>Clear</button>}
  </div>
}
