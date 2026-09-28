import type { TicketSummary } from '../types'
import { ArrowIcon } from './Icons'

const pretty = (value: string) => value.replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase())

export function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return <div className="table-wrap"><table><tbody>
    {Array.from({ length: rows }, (_, index) => <tr key={index}>
      <td><span className="skeleton" style={{ width: '60%' }} /><span className="skeleton" style={{ width: '25%' }} /></td>
      <td><span className="skeleton" style={{ width: '70%' }} /></td>
      <td><span className="skeleton" style={{ width: '50%' }} /></td>
      <td><span className="skeleton" style={{ width: '45%' }} /></td>
    </tr>)}
  </tbody></table></div>
}

export function TicketTable({ tickets, onOpen }: { tickets: TicketSummary[]; onOpen: (id: string) => void }) {
  return <div className="table-wrap"><table>
    <thead><tr><th>Ticket</th><th>Customer</th><th>Status</th><th>Destination</th><th>Raised</th><th aria-label="Open" /></tr></thead>
    <tbody>{tickets.map(ticket => <tr key={ticket.id}>
      <td><button className="row-open" onClick={() => onOpen(ticket.id)}><strong>{ticket.title}</strong><span>{ticket.id.slice(0, 8).toUpperCase()}</span></button></td>
      <td>{ticket.customerName}</td>
      <td><span className={`status status-${ticket.status.toLowerCase()}`}>{pretty(ticket.status)}</span></td>
      <td>{ticket.assignedTier ? `${ticket.assignedTier} · ${pretty(ticket.assignedTeam ?? '')}` : <span className="cell-muted">Awaiting operator</span>}</td>
      <td title={`Imported ${new Date(ticket.createdAt).toLocaleString()}`}>{new Date(ticket.raisedAt).toLocaleString()}</td>
      <td><ArrowIcon /></td>
    </tr>)}</tbody>
  </table></div>
}
