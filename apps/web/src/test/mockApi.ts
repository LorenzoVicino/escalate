import { vi } from 'vitest'
import type { TicketResult, TicketSummary } from '../types'

export interface MockRoutes {
  tickets?: { items: TicketSummary[]; total: number; page: number; pageSize: number }
  stats?: Record<string, unknown>
  owners?: unknown[]
  health?: Record<string, unknown>
  ticket?: TicketResult
}

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status })

/**
 * Routes by URL rather than by call order, so adding a bootstrap request
 * (owners, stats, health) never invalidates unrelated tests.
 */
export function mockApi(routes: MockRoutes = {}) {
  const tickets = routes.tickets ?? { items: [], total: 0, page: 1, pageSize: 10 }
  const fetchMock = vi.spyOn(globalThis, 'fetch')

  fetchMock.mockImplementation((input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    const path = url.replace(/^https?:\/\/[^/]+/, '')

    if (path.startsWith('/health')) return Promise.resolve(json(routes.health ?? { status: 'healthy', provider: 'mock' }))
    if (path.startsWith('/api/v1/integrations/hubspot/owners')) return Promise.resolve(json(routes.owners ?? []))
    if (path.startsWith('/api/v1/integrations/hubspot/sync')) return Promise.resolve(json({ imported: 0, skipped: 0, pages: 1, nextCursor: null }))
    if (path.startsWith('/api/v1/tickets/stats')) return Promise.resolve(json(routes.stats ?? { total: tickets.total, open: tickets.total, needsReview: 0, autoRouted: 0, byStatus: {}, byTier: {}, byTeam: {} }))
    if (/^\/api\/v1\/tickets\/[^?]+/.test(path)) return Promise.resolve(json(routes.ticket))
    if (path.startsWith('/api/v1/tickets')) return Promise.resolve(json(tickets))

    return Promise.resolve(json({}, 404))
  })

  return fetchMock
}
