import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import type { TicketResult } from './types'

const ticket: TicketResult = {
  id: '12ab34cd-0000-0000-0000-000000000000',
  externalId: null,
  title: 'All customer vehicles offline',
  description: 'Since 08:30 all 250 vehicles are offline.',
  customerName: 'Acme Mobility',
  source: 'WEB',
  status: 'ROUTED',
  assignedTier: 'ENGINEERING',
  assignedTeam: 'PLATFORM',
  createdAt: '2026-09-22T08:30:00Z',
  updatedAt: '2026-09-22T08:30:01Z',
  analysis: {
    category: { value: 'PRODUCTION_INCIDENT', confidence: .95 },
    sentiment: { value: 'NEGATIVE', confidence: .8 },
    urgency: { value: .96, confidence: .92 },
    customerImpact: { value: .98, confidence: .92 },
    technicalComplexity: { value: .86, confidence: .9 },
    requiresDeveloper: { value: .91, confidence: .91 },
    securityRisk: { value: .05, confidence: .96 },
    suggestedTeam: { value: 'PLATFORM', confidence: .9 },
    provider: 'mock', model: 'deterministic-demo-v1', processingTimeMs: 1,
  },
  routing: {
    supportTier: 'ENGINEERING', team: 'PLATFORM', confidence: .92,
    routingMode: 'AUTOMATIC', reasons: ['Large customer impact detected'],
  },
}

afterEach(() => { vi.restoreAllMocks() })

test('creates a ticket and displays its explainable routing detail', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch')
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 }))
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify(ticket), { status: 201 }))
  const user = userEvent.setup()
  render(<App />)

  await screen.findByText('The queue is clear')
  await user.click(screen.getByRole('button', { name: /new ticket/i }))
  await user.type(screen.getByLabelText('Customer'), 'Acme Mobility')
  await user.type(screen.getByLabelText('Title'), ticket.title)
  await user.type(screen.getByLabelText('Description'), ticket.description)
  await user.click(screen.getByRole('button', { name: /create & analyze/i }))

  await screen.findByText(/recommended destination/i)
  expect(screen.getByText('Customer impact')).toBeInTheDocument()
  expect(screen.getByText('92% confidence')).toBeInTheDocument()
  expect(screen.getByText('Large customer impact detected')).toBeInTheDocument()
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
})
