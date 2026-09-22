import { useEffect, useMemo, useState } from 'react'
import { api } from './api'
import { BoltIcon, ChartIcon, PlusIcon, QueueIcon, SettingsIcon, ArrowIcon } from './components/Icons'
import { TicketDetail } from './components/TicketDetail'
import { TicketForm } from './components/TicketForm'
import type { TicketInput, TicketResult, TicketSummary } from './types'

const pretty = (value: string) => value.replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase())

export default function App() {
  const [tickets, setTickets] = useState<TicketSummary[]>([])
  const [selected, setSelected] = useState<TicketResult | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listTickets().then(setTickets).catch(() => setError('API unavailable')).finally(() => setLoading(false))
  }, [])

  const stats = useMemo(() => ({
    open: tickets.filter(t => t.status !== 'RESOLVED').length,
    review: tickets.filter(t => ['WAITING_CONFIRMATION', 'MANUAL_TRIAGE'].includes(t.status)).length,
    routed: tickets.filter(t => t.status === 'ROUTED').length,
  }), [tickets])

  async function openTicket(id: string) {
    setSelected(await api.getTicket(id))
  }

  async function createTicket(input: TicketInput) {
    const created = await api.createTicket(input)
    setTickets(current => [created, ...current])
    setShowForm(false)
    setSelected(created)
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><BoltIcon /></span><div><strong>ESCALATE</strong><small>TRIAGE OPERATIONS</small></div></div>
      <nav aria-label="Primary"><button className="nav-item active"><QueueIcon />Triage queue<span>{stats.open}</span></button><button className="nav-item"><ChartIcon />Analytics</button></nav>
      <div className="sidebar-bottom"><div className="system-status"><span className="pulse" /><div><strong>Decision engine</strong><small>Mock provider online</small></div></div><button className="nav-item"><SettingsIcon />Configuration</button><div className="operator"><span>LV</span><div><strong>Lorenzo Vicino</strong><small>Triage operator</small></div></div></div>
    </aside>
    <div className="workspace">
      <header className="topbar"><div><span className="crumb">Operations /</span> Triage queue</div><button className="button primary" onClick={() => setShowForm(true)}><PlusIcon /> New ticket</button></header>
      {selected ? <TicketDetail ticket={selected} onBack={() => setSelected(null)} /> : <main className="content">
        <div className="page-heading"><div><span className="eyebrow">LIVE OPERATIONS</span><h1>Support triage</h1><p>Every ticket, evaluated and routed with an auditable decision.</p></div><div className="date-stamp">{new Date().toLocaleDateString('en', { weekday: 'short', month: 'short', day: 'numeric' })}</div></div>
        <section className="stats-grid"><article><span>OPEN TICKETS</span><strong>{stats.open}</strong><small>Across all support tiers</small></article><article><span>NEEDS HUMAN REVIEW</span><strong className={stats.review ? 'amber' : ''}>{stats.review}</strong><small>Confirmation or manual triage</small></article><article><span>AUTO-ROUTED</span><strong>{stats.routed}</strong><small>{tickets.length ? Math.round(stats.routed / tickets.length * 100) : 0}% of analyzed tickets</small></article></section>
        <section className="panel queue-panel"><div className="panel-title"><div><span className="eyebrow">INCOMING WORK</span><h2>Recent tickets</h2></div><span className="record-count">{tickets.length} records</span></div>
          {error && <div className="error-banner">{error}. Start the API and refresh this page.</div>}
          {loading ? <div className="empty-state">Loading triage queue…</div> : tickets.length === 0 ? <div className="empty-state"><span className="empty-icon"><QueueIcon /></span><h3>The queue is clear</h3><p>Create a ticket to run the complete analysis and routing workflow.</p><button className="button primary" onClick={() => setShowForm(true)}><PlusIcon /> Create first ticket</button></div> : <div className="table-wrap"><table><thead><tr><th>Ticket</th><th>Customer</th><th>Status</th><th>Destination</th><th>Created</th><th aria-label="Open" /></tr></thead><tbody>{tickets.map(ticket => <tr key={ticket.id} onClick={() => void openTicket(ticket.id)}><td><strong>{ticket.title}</strong><span>{ticket.id.slice(0, 8).toUpperCase()}</span></td><td>{ticket.customerName}</td><td><span className={`status status-${ticket.status.toLowerCase()}`}>{pretty(ticket.status)}</span></td><td>{ticket.assignedTier ? `${ticket.assignedTier} · ${pretty(ticket.assignedTeam ?? '')}` : 'Awaiting operator'}</td><td>{new Date(ticket.createdAt).toLocaleDateString()}</td><td><ArrowIcon /></td></tr>)}</tbody></table></div>}
        </section>
      </main>}
    </div>
    {showForm && <TicketForm onClose={() => setShowForm(false)} onSubmit={createTicket} />}
  </div>
}

