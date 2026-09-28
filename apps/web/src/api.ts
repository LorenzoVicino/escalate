import type {
  Health,
  Owner,
  TicketFilters,
  TicketPage,
  TicketResult,
  TicketStats,
} from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

function query(filters: TicketFilters = {}, extra: Record<string, string | number> = {}) {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries({ ...extra, ...filters })) {
    if (value !== undefined && value !== null && value !== '') params.set(key, String(value))
  }
  const search = params.toString()
  return search ? `?${search}` : ''
}

export const api = {
  listTickets: (page = 1, pageSize = 10, filters: TicketFilters = {}) =>
    request<TicketPage>(`/api/v1/tickets${query(filters, { page, pageSize })}`),
  ticketStats: (filters: TicketFilters = {}) =>
    request<TicketStats>(`/api/v1/tickets/stats${query(filters)}`),
  getTicket: (id: string) => request<TicketResult>(`/api/v1/tickets/${id}`),
  listOwners: () => request<Owner[]>('/api/v1/integrations/hubspot/owners'),
  syncHubspot: () => request<unknown>('/api/v1/integrations/hubspot/sync?max_pages=1', {
    method: 'POST',
  }),
  health: () => request<Health>('/health'),
}
