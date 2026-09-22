import type { TicketResult } from '../types'
import { ArrowIcon } from './Icons'

const label = (value: string) => value.replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase())
const percent = (value: number) => `${Math.round(value * 100)}%`

function Meter({ name, value }: { name: string; value: number }) {
  return <div className="signal-row">
    <div className="signal-label"><span>{name}</span><strong>{percent(value)}</strong></div>
    <div className="meter"><span style={{ width: percent(value) }} /></div>
  </div>
}

export function TicketDetail({ ticket, onBack }: { ticket: TicketResult; onBack: () => void }) {
  const { analysis, routing } = ticket
  return <main className="content detail-content">
    <button className="back-link" onClick={onBack}><ArrowIcon /> Back to triage queue</button>
    <div className="detail-heading">
      <div><span className="ticket-id">TICKET · {ticket.id.slice(0, 8).toUpperCase()}</span><h1>{ticket.title}</h1><p>{ticket.customerName} · {new Date(ticket.createdAt).toLocaleString()}</p></div>
      <span className={`status status-${ticket.status.toLowerCase()}`}>{label(ticket.status)}</span>
    </div>
    <div className="detail-grid">
      <section className="panel original-ticket">
        <div className="panel-title"><div><span className="eyebrow">ORIGINAL REQUEST</span><h2>Customer report</h2></div><span className="source-pill">{ticket.source}</span></div>
        <p>{ticket.description}</p>
      </section>
      <section className="panel recommendation">
        <span className="eyebrow light">RECOMMENDED DESTINATION</span>
        <div className="route-line"><strong>{label(routing.supportTier)}</strong><ArrowIcon /><strong>{label(routing.team)}</strong></div>
        <div className="confidence-line"><span>{percent(routing.confidence)} confidence</span><span className="mode-pill">{label(routing.routingMode)}</span></div>
        <div className="reason-list">{routing.reasons.map(reason => <div key={reason}><span>✓</span>{reason}</div>)}</div>
      </section>
      <section className="panel analysis-panel">
        <div className="panel-title"><div><span className="eyebrow">PROBABILISTIC ANALYSIS</span><h2>Decision signals</h2></div><span className="latency">{analysis.provider} · {analysis.processingTimeMs}ms</span></div>
        <div className="classification"><div><span>Category</span><strong>{label(analysis.category.value)}</strong></div><div><span>Sentiment</span><strong>{label(analysis.sentiment.value)}</strong></div></div>
        <div className="signals-grid">
          <Meter name="Urgency" value={analysis.urgency.value} />
          <Meter name="Customer impact" value={analysis.customerImpact.value} />
          <Meter name="Technical complexity" value={analysis.technicalComplexity.value} />
          <Meter name="Developer required" value={analysis.requiresDeveloper.value} />
          <Meter name="Security risk" value={analysis.securityRisk.value} />
        </div>
        <p className="analysis-note">Sentiment is displayed as an independent signal and does not directly determine technical severity.</p>
      </section>
    </div>
  </main>
}

