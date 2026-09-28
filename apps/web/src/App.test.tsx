import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import { mockApi } from './test/mockApi'
import type { TicketResult, TicketSummary } from './types'

const summary: TicketSummary = {
  id: '12ab34cd-0000-0000-0000-000000000000',
  title: 'All customer vehicles offline',
  customerName: 'Acme Mobility',
  source: 'HUBSPOT',
  status: 'ROUTED',
  assignedTier: 'ENGINEERING',
  assignedTeam: 'PLATFORM',
  createdAt: '2026-09-22T08:30:00Z',
  raisedAt: '2026-09-22T08:30:00Z',
}

const ticket: TicketResult = {
  ...summary,
  externalId: 'hs-101',
  description: 'Since 08:30 all 250 vehicles are offline.',
  updatedAt: '2026-09-22T08:30:01Z',
  ownerName: 'Anna Rossi',
  ownerEmail: 'anna@example.com',
  contactEmail: 'ops@acme.io',
  messages: [
    {
      channel: 'EMAIL',
      direction: 'INCOMING_EMAIL',
      author: 'ops@acme.io',
      subject: 'Fleet is dark',
      body: '<p>Nothing is reporting since 08:30.</p>',
      occurredAt: '2026-09-22T08:31:00Z',
    },
  ],
  analysis: {
    category: { value: 'PRODUCTION_INCIDENT', confidence: .95 },
    sentiment: { value: 'NEGATIVE', confidence: .8 },
    urgency: { value: .96, confidence: .92 },
    customerImpact: { value: .98, confidence: .92 },
    technicalComplexity: { value: .86, confidence: .9 },
    requiresDeveloper: { value: .91, confidence: .91 },
    securityRisk: { value: .05, confidence: .96 },
    suggestedTeam: { value: 'PLATFORM', confidence: .9 },
    provider: 'laya', model: 'convaiinnovations/laya', processingTimeMs: 2952,
  },
  routing: {
    supportTier: 'ENGINEERING', team: 'PLATFORM', confidence: .92,
    routingMode: 'AUTOMATIC', reasons: ['Large customer impact detected'],
  },
}

/** The operator modal blocks the queue until someone is identified. */
function identify() {
  window.localStorage.setItem('escalate.operator', JSON.stringify({ id: '1', name: 'Lorenzo Vicino', email: 'lv@example.com' }))
}

const oneTicket = { items: [summary], total: 1, page: 1, pageSize: 10 }

test('opens a synced ticket and shows its explainable routing detail', async () => {
  identify()
  mockApi({ tickets: oneTicket, ticket })
  const user = userEvent.setup()
  render(<App />)

  await user.click(await screen.findByRole('button', { name: /all customer vehicles offline/i }))

  await screen.findByText(/recommended destination/i)
  expect(screen.getByText('Customer impact')).toBeInTheDocument()
  expect(screen.getByText('92% confidence')).toBeInTheDocument()
  expect(screen.getByText('Large customer impact detected')).toBeInTheDocument()
})

test('renders the HubSpot conversation thread on the ticket detail', async () => {
  identify()
  mockApi({ tickets: oneTicket, ticket })
  const user = userEvent.setup()
  render(<App />)

  await user.click(await screen.findByRole('button', { name: /all customer vehicles offline/i }))

  expect(await screen.findByText('Conversation thread')).toBeInTheDocument()
  expect(screen.getByText('Fleet is dark')).toBeInTheDocument()
  expect(screen.getByText('Email')).toBeInTheDocument()
  expect(screen.getByText('Incoming')).toBeInTheDocument()
  expect(screen.getByText('Nothing is reporting since 08:30.')).toBeInTheDocument()
})

test('the queue is read-only — tickets come from HubSpot, not an intake form', async () => {
  identify()
  mockApi({ tickets: oneTicket, ticket })
  render(<App />)

  await screen.findByText('Recent tickets')
  expect(screen.queryByRole('button', { name: /new ticket/i })).not.toBeInTheDocument()
  expect(screen.getByRole('button', { name: /sync hubspot now/i })).toBeInTheDocument()
})

test('asks who the operator is on first load and remembers the choice', async () => {
  mockApi({ owners: [{ id: '42', email: 'anna@example.com', firstName: 'Anna', lastName: 'Rossi' }] })
  const user = userEvent.setup()
  render(<App />)

  expect(await screen.findByRole('dialog')).toBeInTheDocument()
  await user.selectOptions(await screen.findByLabelText(/hubspot user/i), '42')
  await user.click(screen.getByRole('button', { name: /continue/i }))

  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(await screen.findByText('Anna Rossi')).toBeInTheDocument()
  expect(JSON.parse(window.localStorage.getItem('escalate.operator')!).name).toBe('Anna Rossi')
})

test('shows the real provider reported by the API, not a hardcoded label', async () => {
  identify()
  mockApi({ health: { status: 'healthy', provider: 'laya' } })
  render(<App />)

  expect(await screen.findByText('laya provider online')).toBeInTheDocument()
})
