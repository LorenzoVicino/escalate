import { useMemo, useState } from 'react'
import { api } from './api'
import { FilterBar } from './components/FilterBar'
import { ArrowIcon, QueueIcon } from './components/Icons'
import { OperatorModal } from './components/OperatorModal'
import { Sidebar } from './components/Sidebar'
import { SyncIndicator } from './components/SyncIndicator'
import { TicketDetail } from './components/TicketDetail'
import { TableSkeleton, TicketTable } from './components/TicketTable'
import { Toast } from './components/Toast'
import { useHealth } from './hooks/useHealth'
import { useLocalStorage } from './hooks/useLocalStorage'
import { useNewTicketAlert } from './hooks/useNewTicketAlert'
import { useOperator } from './hooks/useOperator'
import { useTheme } from './hooks/useTheme'
import { PAGE_SIZE, useTicketQueue } from './hooks/useTicketQueue'
import type { TicketFilters, TicketResult } from './types'

export default function App() {
  const { operator, setOperator } = useOperator()
  const { theme, cycle } = useTheme()
  const [muted, setMuted] = useLocalStorage('escalate.muted', false)
  const [filters, setFilters] = useState<TicketFilters>({})
  const [selected, setSelected] = useState<TicketResult | null>(null)
  const [showOperator, setShowOperator] = useState(false)

  const health = useHealth()
  const queue = useTicketQueue(filters, Boolean(selected))
  const identified = operator !== null

  const unfiltered = Object.keys(filters).length === 0
  const alert = useNewTicketAlert(queue.tickets, {
    muted,
    eligible: unfiltered && queue.page === 1,
  })

  // Falls back to page-local counting if the stats endpoint is unavailable.
  const stats = useMemo(() => queue.stats ?? {
    total: queue.total,
    open: queue.tickets.filter(t => t.status !== 'RESOLVED').length,
    needsReview: queue.tickets.filter(t => ['WAITING_CONFIRMATION', 'MANUAL_TRIAGE'].includes(t.status)).length,
    autoRouted: queue.tickets.filter(t => t.status === 'ROUTED').length,
    byStatus: {}, byTier: {}, byTeam: {},
  }, [queue.stats, queue.total, queue.tickets])

  const pageCount = Math.max(1, Math.ceil(queue.total / PAGE_SIZE))

  async function openTicket(id: string) { setSelected(await api.getTicket(id)) }

  return <div className="app-shell">
    <Sidebar
      openCount={stats.open} newCount={alert.newCount} operator={operator}
      onEditOperator={() => setShowOperator(true)} health={health}
      theme={theme} onCycleTheme={cycle} muted={muted} onToggleMute={() => setMuted(!muted)}
    />
    <div className="workspace">
      <header className="topbar">
        <div><span className="crumb">Operations /</span> Triage queue</div>
        <div className="topbar-actions">
          <SyncIndicator lastSyncedAt={queue.lastSyncedAt} syncing={queue.syncing} onSync={() => void queue.sync()} />
        </div>
      </header>
      {selected ? <TicketDetail ticket={selected} onBack={() => setSelected(null)} /> : <main className="content">
        <div className="page-heading">
          <div><span className="eyebrow">LIVE OPERATIONS</span><h1>Support triage</h1><p>Every ticket, evaluated and routed with an auditable decision.</p></div>
          <div className="date-stamp">{new Date().toLocaleDateString('en', { weekday: 'short', month: 'short', day: 'numeric' })}</div>
        </div>
        <section className="stats-grid">
          <article><span>OPEN TICKETS</span><strong>{stats.open}</strong><small>Across all support tiers</small></article>
          <article><span>NEEDS HUMAN REVIEW</span><strong className={stats.needsReview ? 'amber' : ''}>{stats.needsReview}</strong><small>Confirmation or manual triage</small></article>
          <article><span>AUTO-ROUTED</span><strong>{stats.autoRouted}</strong><small>{stats.total ? Math.round(stats.autoRouted / stats.total * 100) : 0}% of analyzed tickets</small></article>
        </section>
        <section className="panel queue-panel">
          <div className="panel-title"><div><span className="eyebrow">INCOMING WORK</span><h2>Recent tickets</h2></div><span className="record-count">{queue.total} records</span></div>
          <FilterBar filters={filters} onChange={setFilters} ownerId={operator?.id || null} />
          {queue.error && <div className="error-banner">{queue.error}. Start the API and refresh this page.</div>}
          {queue.loading ? <TableSkeleton /> : queue.tickets.length === 0 ? <div className="empty-state">
            <span className="empty-icon"><QueueIcon /></span>
            <h3>{unfiltered ? 'The queue is clear' : 'No tickets match these filters'}</h3>
            <p>{unfiltered ? 'Tickets appear here as they are imported from HubSpot.' : 'Try widening the filters, or clear them to see the full queue.'}</p>
            {unfiltered && <button className="button secondary" onClick={() => void queue.sync()} disabled={queue.syncing}>{queue.syncing ? 'Syncing…' : 'Sync HubSpot now'}</button>}
          </div> : <>
            <TicketTable tickets={queue.tickets} onOpen={id => void openTicket(id)} />
            <div className="pagination">
              <button className="button secondary" disabled={queue.page <= 1} onClick={() => void queue.load(queue.page - 1)}><ArrowIcon style={{ transform: 'rotate(180deg)', width: 14 }} /> Previous</button>
              <span>Page {queue.page} of {pageCount}</span>
              <button className="button secondary" disabled={queue.page >= pageCount} onClick={() => void queue.load(queue.page + 1)}>Next <ArrowIcon style={{ width: 14 }} /></button>
            </div>
          </>}
        </section>
      </main>}
    </div>
    {(showOperator || !identified) && <OperatorModal
      current={operator}
      onSelect={next => { setOperator(next); setShowOperator(false) }}
      onClose={() => setShowOperator(false)}
    />}
    {alert.newCount > 0 && <Toast
      message={`${alert.newCount} new ticket${alert.newCount > 1 ? 's' : ''} imported`}
      actionLabel="View" onAction={() => { alert.dismiss(); void queue.load(1) }} onDismiss={alert.dismiss}
    />}
  </div>
}
