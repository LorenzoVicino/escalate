import { act, renderHook } from '@testing-library/react'
import { useNewTicketAlert } from './useNewTicketAlert'
import type { TicketSummary } from '../types'

const ticket = (id: string): TicketSummary => ({
  id, title: `Ticket ${id}`, customerName: 'Acme', source: 'HUBSPOT',
  status: 'MANUAL_TRIAGE', assignedTier: null, assignedTeam: null,
  createdAt: '2026-09-22T08:00:00Z', raisedAt: '2026-09-22T08:00:00Z',
})

const options = { muted: false, eligible: true }

test('does not alert on the first load', () => {
  const { result } = renderHook(({ tickets }) => useNewTicketAlert(tickets, options), {
    initialProps: { tickets: [ticket('a'), ticket('b')] },
  })
  expect(result.current.newCount).toBe(0)
})

test('alerts only for ids never seen before', () => {
  const { result, rerender } = renderHook(({ tickets }) => useNewTicketAlert(tickets, options), {
    initialProps: { tickets: [ticket('a')] },
  })

  rerender({ tickets: [ticket('a')] })
  expect(result.current.newCount).toBe(0)

  rerender({ tickets: [ticket('c'), ticket('a')] })
  expect(result.current.newCount).toBe(1)

  act(() => result.current.dismiss())
  expect(result.current.newCount).toBe(0)
})

test('stays silent while paging or filtering', () => {
  const { result, rerender } = renderHook(
    ({ tickets, eligible }) => useNewTicketAlert(tickets, { muted: false, eligible }),
    { initialProps: { tickets: [ticket('a')], eligible: false } },
  )
  rerender({ tickets: [ticket('z')], eligible: false })
  expect(result.current.newCount).toBe(0)
})
